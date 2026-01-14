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


def _extract_json_from_text(text: str) -> str:
    """
    Extract JSON from text that may contain markdown code blocks or other text.
    
    Args:
        text: Raw text that may contain JSON
        
    Returns:
        Extracted JSON string
    """
    import re
    
    # Log raw response for debugging
    logger.debug(f"Raw LLM response: {text[:1000]}...")
    
    # Try to find JSON in code blocks first
    code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1)
    
    # Try to find complete JSON object with results array
    # Look for the LAST occurrence of {"results": to handle reasoning text before JSON
    results_start = text.rfind('{"results":')
    if results_start == -1:
        results_start = text.rfind('{ "results":')
    
    if results_start != -1:
        # Find matching closing brace
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(results_start, len(text)):
            char = text[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"':
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return text[results_start:i+1]
    
    # Fallback: find anything that looks like JSON
    brace_start = text.find('{')
    brace_end = text.rfind('}')
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        return text[brace_start:brace_end + 1]
    
    return text


def _fix_json_string(json_str: str) -> str:
    """
    Attempt to fix common JSON issues from LLM responses.
    
    Args:
        json_str: Potentially malformed JSON string
        
    Returns:
        Fixed JSON string
    """
    import re
    
    # Remove trailing commas before ] or }
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # Fix unescaped newlines in strings
    json_str = re.sub(r'(?<!\\)\n', r'\\n', json_str)
    
    # Remove control characters
    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
    
    return json_str


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

    async def _call_api(self, messages: list[dict], use_json_format: bool = True) -> str:
        """
        Make a call to the LLM API.
        
        Args:
            messages: List of message dicts with role and content
            use_json_format: Whether to request JSON response format
            
        Returns:
            The assistant's response content
            
        Raises:
            LLMAPIError: If the API returns an error
        """
        client = await self._get_client()
        
        is_reasoner = "reasoner" in self.model.lower()
        
        # For reasoner model, convert system message to user message
        if is_reasoner and messages and messages[0].get("role") == "system":
            system_content = messages[0]["content"]
            messages = messages[1:]
            if messages:
                messages[0]["content"] = f"{system_content}\n\n{messages[0]['content']}"
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        # Reasoner doesn't support temperature and response_format
        if not is_reasoner:
            payload["temperature"] = 0.1
            if use_json_format:
                payload["response_format"] = {"type": "json_object"}
        
        try:
            logger.info(f"Sending request to LLM API: {self.api_url}/chat/completions (model: {self.model})")
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
            content = message.get("content", "")
            
            # Log reasoning if present (for debugging)
            if message.get("reasoning_content"):
                logger.info(f"Model reasoning length: {len(message['reasoning_content'])} chars")
                logger.debug(f"Model reasoning: {message['reasoning_content'][:500]}...")
            
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
        
        system_prompt = """Ты - эксперт по анализу комментариев о дефектах в строительстве. 
Твоя задача - разделить каждый комментарий на отдельные дефекты.

КРИТИЧЕСКИ ВАЖНО: Каждый отдельный дефект = отдельный элемент в списке!

Правила разделения:
1. Если дефекты пронумерованы (1, 2, 3... или 1., 2., 3... или 1Текст 2Текст) - это РАЗНЫЕ дефекты
2. Если дефекты разделены точкой с запятой (;) - это РАЗНЫЕ дефекты
3. Если дефекты в отдельных предложениях - это РАЗНЫЕ дефекты
4. Убирай номера из начала дефекта (например "1Царапины" → "Царапины", "2. Трещина" → "Трещина")
5. Если комментарий пустой или "нет замечаний" - верни пустой список []
6. Сохраняй текст дефекта без изменений (кроме удаления номеров)

ПРИМЕРЫ (ОБЯЗАТЕЛЬНО СЛЕДУЙ ЭТОЙ ЛОГИКЕ):

Пример 1 - Пронумерованные дефекты:
Вход: "1Царапины на окне 2Трещина в раме 3Загрязнения"
Выход: {"defects": [
  {"text": "Царапины на окне"},
  {"text": "Трещина в раме"},
  {"text": "Загрязнения"}
]}

Пример 2 - С точками:
Вход: "1. Царапины 2. Трещина 3. Загрязнения"
Выход: {"defects": [
  {"text": "Царапины"},
  {"text": "Трещина"},
  {"text": "Загрязнения"}
]}

Пример 3 - Длинные описания:
Вход: "1Царапины и вмятины на внешних оконных откосах 2Отслоение уплотнительной резинки 3Зазоры в углах"
Выход: {"defects": [
  {"text": "Царапины и вмятины на внешних оконных откосах"},
  {"text": "Отслоение уплотнительной резинки"},
  {"text": "Зазоры в углах"}
]}

Пример 4 - Точка с запятой:
Вход: "Царапины на окне; Трещина в раме"
Выход: {"defects": [
  {"text": "Царапины на окне"},
  {"text": "Трещина в раме"}
]}

Пример 5 - Один дефект:
Вход: "Царапины на окне"
Выход: {"defects": [{"text": "Царапины на окне"}]}

Пример 6 - Нет дефектов:
Вход: "нет замечаний"
Выход: {"defects": []}

Формат ответа (JSON):
{
  "results": [
    {"defects": [{"text": "дефект 1"}, {"text": "дефект 2"}]},
    {"defects": [{"text": "единственный дефект"}]},
    {"defects": []}
  ]
}

Количество элементов в results = количество входных комментариев."""

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
            f"{i+1}. Дефект: \"{item['defect']}\"\n   Варианты категорий:\n   " + 
            "\n   ".join(f"- {c}" for c in item['candidates'])
            for i, item in enumerate(defects_with_candidates)
        )
        
        system_prompt = """Ты - эксперт по классификации строительных дефектов.
Твоя задача - выбрать наиболее подходящую категорию для каждого дефекта из предложенного списка.

ПРАВИЛА:
1. Ты ОБЯЗАН выбрать категорию из предложенного списка
2. Копируй название категории ТОЧНО как оно написано
3. Выбирай категорию которая БЛИЖЕ ВСЕГО по смыслу к дефекту
4. Даже если совпадение не идеальное - выбери наиболее подходящую категорию
5. "НЕ ОПРЕДЕЛЕНО" используй ТОЛЬКО если дефект вообще не относится к строительству

КАК ВЫБИРАТЬ:
- Смотри на ключевые слова: окно, дверь, стена, пол, потолок, электрика, сантехника и т.д.
- Если дефект про окна/стеклопакеты → ищи категории со словами "ПВХ", "Стеклопакет", "Рама"
- Если дефект про двери → ищи "Входная дверь" или "Двери межкомнатные"
- Если дефект про воду/трубы → ищи "Водоснабжение", "Канализация", "Сантехника"
- Если дефект про электричество → ищи "Электрика"
- Если дефект про отделку → ищи "Обои", "Плитка", "Ламинат", "Штукатурка"

Формат ответа (строго JSON):
{
  "results": [
    {"chosen": "ТОЧНОЕ название категории из списка"},
    {"chosen": "ТОЧНОЕ название категории из списка"}
  ]
}"""

        user_prompt = f"""Классифицируй следующие дефекты, выбрав для каждого наиболее подходящую категорию из предложенных вариантов:

{items_text}

Проанализируй каждый дефект и верни JSON с выбранными категориями."""

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
            # Extract JSON from response (handles reasoner's text output)
            json_str = _extract_json_from_text(response)
            
            # Try to parse, if fails try to fix
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("Initial JSON parse failed, attempting to fix...")
                json_str = _fix_json_string(json_str)
                data = json.loads(json_str)
            
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
            logger.error(f"Raw response (first 500 chars): {response[:500]}")
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
            # Extract JSON from response (handles reasoner's text output)
            json_str = _extract_json_from_text(response)
            
            # Try to parse, if fails try to fix
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning("Initial JSON parse failed, attempting to fix...")
                json_str = _fix_json_string(json_str)
                data = json.loads(json_str)
            
            results = data.get("results", [])
            
            if len(results) != expected_count:
                logger.warning(
                    f"Expected {expected_count} results, got {len(results)}. "
                    "Padding with 'НЕ ОПРЕДЕЛЕНО'."
                )
                # Pad with unknown category if needed
                while len(results) < expected_count:
                    results.append({"chosen": "НЕ ОПРЕДЕЛЕНО"})
                # Truncate if too many
                results = results[:expected_count]
            
            return [
                ClassifyResult(chosen=item.get("chosen", "НЕ ОПРЕДЕЛЕНО"))
                for item in results
            ]
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse classify response: {e}")
            logger.error(f"Raw response (first 500 chars): {response[:500]}")
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
