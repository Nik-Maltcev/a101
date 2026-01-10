"""LLM Client for interacting with Deepseek/GPT API."""

import json
import logging
from typing import Optional

import httpx

from app.config import settings
from app.models.schemas import SplitResult, ClassifyResult, DefectItem


logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class LLMAPIError(LLMClientError):
    """Error when LLM API returns an error."""
    pass


class LLMResponseParseError(LLMClientError):
    """Error when LLM response cannot be parsed."""
    pass


class LLMClient:
    """Client for working with LLM API (Deepseek/GPT)."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 120.0,
    ):
        """
        Initialize LLM client.
        
        Args:
            api_key: API key for authentication
            api_url: Base URL for the API
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or settings.LLM_API_KEY
        self.api_url = api_url or settings.LLM_API_URL
        self.model = model or settings.LLM_MODEL
        self.timeout = timeout
        
        self._client: Optional[httpx.AsyncClient] = None
        
        # Validate API key
        if not self.api_key or not self.api_key.strip():
            raise LLMClientError(
                "LLM_API_KEY is not configured. "
                "Please set the LLM_API_KEY environment variable."
            )
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _call_api(self, messages: list[dict]) -> str:
        """
        Make a call to the LLM API.
        
        Args:
            messages: List of message dicts with role and content
            
        Returns:
            The assistant's response content
            
        Raises:
            LLMAPIError: If the API returns an error
        """
        client = await self._get_client()
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,  # Low temperature for consistent results
        }
        
        # Add response_format for JSON output (supported by both deepseek-chat and deepseek-reasoner)
        payload["response_format"] = {"type": "json_object"}
        
        try:
            logger.info(f"Sending request to LLM API: {self.api_url}/chat/completions")
            logger.debug(f"Payload model: {payload.get('model')}, messages count: {len(messages)}")
            
            response = await client.post(
                f"{self.api_url}/chat/completions",
                json=payload,
            )
            
            logger.info(f"LLM API response status: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            message = data["choices"][0]["message"]
            
            # For deepseek-reasoner model, reasoning_content contains the thinking process
            # We only need the final content for our use case
            content = message.get("content", "")
            
            # Log reasoning if present (for debugging)
            if message.get("reasoning_content"):
                logger.debug(f"Model reasoning: {message['reasoning_content'][:200]}...")
            
            return content
            
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API HTTP error: {e.response.status_code} - {e.response.text}")
            raise LLMAPIError(f"API returned status {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"LLM API request error: {e}")
            raise LLMAPIError(f"Request failed: {e}")
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected API response format: {e}")
            raise LLMAPIError(f"Unexpected response format: {e}")
    
    def _build_split_prompt(self, comments: list[str]) -> list[dict]:
        """Build prompt for splitting comments into defects."""
        comments_text = "\n".join(
            f"{i+1}. {comment}" for i, comment in enumerate(comments)
        )
        
        system_prompt = """Ты - эксперт по анализу комментариев о дефектах. 
Твоя задача - разделить каждый комментарий на отдельные дефекты.

Правила:
1. Каждый отдельный дефект должен быть выделен как отдельный элемент
2. Если комментарий пустой или содержит "нет замечаний" - верни пустой список дефектов
3. Сохраняй оригинальный текст дефекта без изменений
4. Если в комментарии один дефект - верни список с одним элементом

Формат ответа (JSON):
{
  "results": [
    {"defects": [{"text": "текст дефекта 1"}, {"text": "текст дефекта 2"}]},
    {"defects": [{"text": "единственный дефект"}]},
    {"defects": []}
  ]
}

Количество элементов в results должно соответствовать количеству входных комментариев."""

        user_prompt = f"""Разделите следующие комментарии на отдельные дефекты:

{comments_text}

Верните JSON с результатами для каждого комментария."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _build_classify_prompt(self, defects_with_candidates: list[dict]) -> list[dict]:
        """
        Build prompt for classifying defects.
        
        Args:
            defects_with_candidates: List of dicts with 'defect' and 'candidates' keys
        """
        items_text = "\n".join(
            f"{i+1}. Дефект: {item['defect']}\n   Кандидаты: {', '.join(item['candidates'])}"
            for i, item in enumerate(defects_with_candidates)
        )
        
        system_prompt = """Ты - эксперт по классификации дефектов.
Твоя задача - выбрать наиболее подходящую категорию для каждого дефекта из списка кандидатов.

Правила:
1. Выбирай ТОЛЬКО из предложенных кандидатов
2. Выбирай категорию, которая наиболее точно описывает дефект
3. Если ни одна категория не подходит идеально, выбери наиболее близкую

Формат ответа (JSON):
{
  "results": [
    {"chosen": "выбранная категория 1"},
    {"chosen": "выбранная категория 2"}
  ]
}

Количество элементов в results должно соответствовать количеству входных дефектов."""

        user_prompt = f"""Классифицируйте следующие дефекты, выбрав категорию из списка кандидатов:

{items_text}

Верните JSON с выбранной категорией для каждого дефекта."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    
    def _parse_split_response(self, response: str, expected_count: int) -> list[SplitResult]:
        """
        Parse LLM response for split operation.
        
        Args:
            response: JSON string from LLM
            expected_count: Expected number of results
            
        Returns:
            List of SplitResult objects
            
        Raises:
            LLMResponseParseError: If response cannot be parsed
        """
        try:
            data = json.loads(response)
            results = data.get("results", [])
            
            if len(results) != expected_count:
                logger.warning(
                    f"Expected {expected_count} results, got {len(results)}. "
                    "Padding with empty results."
                )
                # Pad with empty results if needed
                while len(results) < expected_count:
                    results.append({"defects": []})
                # Truncate if too many
                results = results[:expected_count]
            
            parsed_results = []
            for item in results:
                defects = [
                    DefectItem(text=d.get("text", ""))
                    for d in item.get("defects", [])
                    if d.get("text", "").strip()  # Skip empty defects
                ]
                parsed_results.append(SplitResult(defects=defects))
            
            return parsed_results
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse split response: {e}")
            raise LLMResponseParseError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Error parsing split response: {e}")
            raise LLMResponseParseError(f"Failed to parse response: {e}")

    def _parse_classify_response(self, response: str, expected_count: int) -> list[ClassifyResult]:
        """
        Parse LLM response for classify operation.
        
        Args:
            response: JSON string from LLM
            expected_count: Expected number of results
            
        Returns:
            List of ClassifyResult objects
            
        Raises:
            LLMResponseParseError: If response cannot be parsed
        """
        try:
            data = json.loads(response)
            results = data.get("results", [])
            
            if len(results) != expected_count:
                logger.warning(
                    f"Expected {expected_count} results, got {len(results)}. "
                    "Padding with 'Неизвестно'."
                )
                # Pad with unknown category if needed
                while len(results) < expected_count:
                    results.append({"chosen": "Неизвестно"})
                # Truncate if too many
                results = results[:expected_count]
            
            return [
                ClassifyResult(chosen=item.get("chosen", "Неизвестно"))
                for item in results
            ]
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse classify response: {e}")
            raise LLMResponseParseError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Error parsing classify response: {e}")
            raise LLMResponseParseError(f"Failed to parse response: {e}")
    
    async def split_comments(self, comments: list[str]) -> list[SplitResult]:
        """
        Split comments into individual defects using LLM.
        
        Processes comments in batches according to SPLIT_BATCH_SIZE setting.
        
        Args:
            comments: List of comment strings to split
            
        Returns:
            List of SplitResult objects, one per input comment
            
        Raises:
            LLMAPIError: If API call fails
            LLMResponseParseError: If response cannot be parsed
        """
        if not comments:
            return []
        
        batch_size = settings.SPLIT_BATCH_SIZE
        all_results: list[SplitResult] = []
        total_batches = (len(comments) + batch_size - 1) // batch_size
        
        for i in range(0, len(comments), batch_size):
            batch = comments[i:i + batch_size]
            batch_num = i // batch_size + 1
            logger.info(f"Processing split batch {batch_num}/{total_batches}, size: {len(batch)}")
            
            messages = self._build_split_prompt(batch)
            logger.info(f"Calling LLM API for batch {batch_num}...")
            response = await self._call_api(messages)
            logger.info(f"Batch {batch_num} response received, parsing...")
            batch_results = self._parse_split_response(response, len(batch))
            all_results.extend(batch_results)
            logger.info(f"Batch {batch_num} complete")
        
        return all_results

    async def classify_defects(
        self, 
        defects_with_candidates: list[dict]
    ) -> list[ClassifyResult]:
        """
        Classify defects by selecting category from candidates using LLM.
        
        Processes defects in batches according to CLASSIFY_BATCH_SIZE setting.
        
        Args:
            defects_with_candidates: List of dicts with keys:
                - 'defect': str - the defect text
                - 'candidates': list[str] - candidate categories
                
        Returns:
            List of ClassifyResult objects, one per input defect
            
        Raises:
            LLMAPIError: If API call fails
            LLMResponseParseError: If response cannot be parsed
        """
        if not defects_with_candidates:
            return []
        
        batch_size = settings.CLASSIFY_BATCH_SIZE
        all_results: list[ClassifyResult] = []
        
        for i in range(0, len(defects_with_candidates), batch_size):
            batch = defects_with_candidates[i:i + batch_size]
            logger.info(f"Processing classify batch {i // batch_size + 1}, size: {len(batch)}")
            
            messages = self._build_classify_prompt(batch)
            response = await self._call_api(messages)
            batch_results = self._parse_classify_response(response, len(batch))
            all_results.extend(batch_results)
        
        return all_results
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
