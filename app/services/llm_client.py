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
    
    # Remove control characters (excluding newlines, tabs, carriage returns)
    # \x00-\x1f includes \n(0a), \r(0d), \t(09)
    # We want to keep structural whitespace
    json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', json_str)
    
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
        # Use a more structured format preserving newlines
        comments_text = "\n\n---\n\n".join(
            f"ID: {i+1}\nCONTENT:\n<<<\n{comment}\n>>>"
            for i, comment in enumerate(comments)
        )
        
        system_prompt = """Ты - эксперт по анализу строительных дефектов.

ЗАДАЧА: Разделить каждый комментарий на ОТДЕЛЬНЫЕ дефекты. Каждый дефект должен быть УНИКАЛЬНЫМ текстом.

ФОРМАТ ВХОДНЫХ ДАННЫХ:
ID: номер
CONTENT:
<<<
текст комментария (может быть многострочным, с переносами строк)
>>>

КРИТИЧЕСКИ ВАЖНО:
- Текст в CONTENT может содержать ПЕРЕНОСЫ СТРОК (\\n)
- Каждая строка с номером (1..., 2..., 3...) - это ОТДЕЛЬНЫЙ дефект
- НЕ ДУБЛИРУЙ текст! Каждый дефект должен быть РАЗНЫМ!
- ИЗВЛЕКАЙ ПОЛНЫЙ текст каждого дефекта, не обрезай!

ПРАВИЛА РАЗДЕЛЕНИЯ:
1. Если текст содержит НУМЕРОВАННЫЙ СПИСОК (каждая строка начинается с цифры):
   - Каждая строка с номером = ОТДЕЛЬНЫЙ дефект
   - Убирай номер из начала (1Царапины → Царапины, 1. Дефект → Дефект)
   - ВАЖНО: извлекай ПОЛНЫЙ текст строки после номера!

2. Форматы нумерации:
   - "1Текст" (цифра слитно с текстом)
   - "1. Текст" (цифра с точкой)
   - "1) Текст" (цифра со скобкой)
   - "1 Текст" (цифра с пробелом)

3. Заголовки типа "Окно 2", "Кухня", "Окно 1 (слева на право)":
   - Если после заголовка идет нумерованный список -> ИГНОРИРОВАТЬ заголовок
   - Извлекать ТОЛЬКО пункты списка
   - Если КРОМЕ заголовка ничего нет -> пустой список []

4. Точка с запятой (;) = разделитель дефектов

5. "нет замечаний" или пустой текст = пустой список []

ПРИМЕРЫ:

Вход:
ID: 1
CONTENT:
<<<
Окно 2
1Царапины и вмятины на внешних оконных откосах и отливе
2Отслоение уплотнительной резинки 1го контура за правой створкой
3Зазоры и уступы в углах стыковки оконных штапиков всех створок оконного блока
>>>

Выход: {"results": [["Царапины и вмятины на внешних оконных откосах и отливе", "Отслоение уплотнительной резинки 1го контура за правой створкой", "Зазоры и уступы в углах стыковки оконных штапиков всех створок оконного блока"]]}

Вход:
ID: 2
CONTENT:
<<<
Стеклопакет ПВХ: поврежден (трещина)
>>>

Выход: {"results": [["Стеклопакет ПВХ: поврежден (трещина)"]]}

Вход:
ID: 3
CONTENT:
<<<
Окно
>>>

Выход: {"results": [[]]}

Вход:
ID: 4
CONTENT:
<<<
Окно 2
1. Царапины на стекле
2. Трещина в раме
3. Зазор между рамой и стеной
4. Отслоение краски
5. Сколы на подоконнике
6. Неплотное прилегание створки
7. Загрязнение профиля
>>>

Выход: {"results": [["Царапины на стекле", "Трещина в раме", "Зазор между рамой и стеной", "Отслоение краски", "Сколы на подоконнике", "Неплотное прилегание створки", "Загрязнение профиля"]]}

ФОРМАТ ОТВЕТА (строго JSON):
{
  "results": [
    ["дефект 1 полный текст", "дефект 2 полный текст", "дефект 3 полный текст"],
    ["единственный дефект"],
    []
  ]
}

ВАЖНО:
- Количество списков в results ДОЛЖНО РАВНЯТЬСЯ количеству входных комментариев!
- Каждый дефект в списке должен быть УНИКАЛЬНЫМ текстом!
- НЕ ПОВТОРЯЙ один и тот же текст несколько раз!"""

        user_prompt = f"""Разделите каждый комментарий на отдельные дефекты.

{comments_text}

Верните JSON. Количество results = {len(comments)}.
ВАЖНО: Каждый дефект должен быть УНИКАЛЬНЫМ текстом! Не дублируй!"""

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

    def _coerce_split_item(self, item: object) -> list[str]:
        """Coerce a single split result item into a list of defect strings."""
        if item is None:
            return []

        if isinstance(item, list):
            return item

        if isinstance(item, str):
            stripped = item.strip()
            if not stripped:
                return []
            try:
                parsed = json.loads(stripped, strict=False)
            except json.JSONDecodeError:
                parsed = None

            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                results = parsed.get("results")
                if isinstance(results, list):
                    return results
                defects = parsed.get("defects")
                if isinstance(defects, list):
                    return defects

            lines = [line.strip() for line in stripped.splitlines() if line.strip()]
            if len(lines) > 1:
                return lines
            return [stripped]

        if isinstance(item, dict):
            defects = item.get("defects")
            if isinstance(defects, list):
                return defects
            results = item.get("results")
            if isinstance(results, list):
                return results
            return [json.dumps(item, ensure_ascii=False)]

        return [str(item)]
    
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
                # Use strict=False to allow control characters (newlines) in strings
                data = json.loads(json_str, strict=False)
            except json.JSONDecodeError:
                logger.warning("Initial JSON parse failed, attempting to fix...")
                json_str = _fix_json_string(json_str)
                data = json.loads(json_str, strict=False)
            
            results = data.get("results", [])
            
            if len(results) != expected_count:
                logger.warning(
                    f"Expected {expected_count} results, got {len(results)}. "
                    "Padding with empty results."
                )
                # Pad with empty results if needed
                while len(results) < expected_count:
                    results.append([])
                # Truncate if too many
                results = results[:expected_count]
            
            parsed_results = []
            for idx, item in enumerate(results):
                # Ensure item is a list of strings
                if not isinstance(item, list):
                    logger.warning(f"Result {idx} is not a list: {item}")
                    item = self._coerce_split_item(item)

                # Filter out empty defects and deduplicate
                seen_defects = set()
                unique_defects = []
                for d in item:
                    text = str(d).strip()
                    if text and text not in seen_defects:
                        seen_defects.add(text)
                        unique_defects.append(text)
                    elif text in seen_defects:
                        logger.warning(f"Result {idx}: Duplicate defect removed: '{text[:50]}...'")
                
                defects = [DefectItem(text=text) for text in unique_defects]
                parsed_results.append(SplitResult(defects=defects))
                
                # Log parsed defects for debugging
                if idx < 5:
                    logger.info(f"Parsed result {idx}: {len(defects)} defects (after dedup)")
                    for d_idx, d in enumerate(defects[:5]):
                        logger.info(f"  Defect {d_idx+1}: '{d.text[:80]}...' " if len(d.text) > 80 else f"  Defect {d_idx+1}: '{d.text}'")
            
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
                data = json.loads(json_str, strict=False)
            except json.JSONDecodeError:
                logger.warning("Initial JSON parse failed, attempting to fix...")
                json_str = _fix_json_string(json_str)
                data = json.loads(json_str, strict=False)
            
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
            logger.info(f"Raw LLM response (first 2000 chars): {response[:2000]}")
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
        
        Processes defects in batches with concurrent API requests for speed.
        
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
        
        import asyncio
        
        batch_size = settings.CLASSIFY_BATCH_SIZE
        concurrent_batches = getattr(settings, 'CLASSIFY_CONCURRENT_BATCHES', 3)
        
        # Split into batches
        batches = []
        for i in range(0, len(defects_with_candidates), batch_size):
            batches.append(defects_with_candidates[i:i + batch_size])
        
        logger.info(f"Processing {len(batches)} classify batches with {concurrent_batches} concurrent requests")
        
        async def process_batch(batch_idx: int, batch: list[dict]) -> tuple[int, list[ClassifyResult]]:
            """Process a single batch and return results with index."""
            logger.info(f"Processing classify batch {batch_idx + 1}/{len(batches)}, size: {len(batch)}")
            messages = self._build_classify_prompt(batch)
            response = await self._call_api(messages)
            batch_results = self._parse_classify_response(response, len(batch))
            logger.info(f"Batch {batch_idx + 1} complete")
            return (batch_idx, batch_results)
        
        # Process batches with concurrency limit
        all_results: list[ClassifyResult] = [None] * len(defects_with_candidates)  # Pre-allocate
        
        for i in range(0, len(batches), concurrent_batches):
            # Process up to concurrent_batches at once
            batch_group = batches[i:i + concurrent_batches]
            tasks = [
                process_batch(i + j, batch) 
                for j, batch in enumerate(batch_group)
            ]
            
            # Wait for all tasks in this group
            results = await asyncio.gather(*tasks)
            
            # Place results in correct positions
            for batch_idx, batch_results in results:
                start_idx = batch_idx * batch_size
                for j, result in enumerate(batch_results):
                    all_results[start_idx + j] = result
        
        return all_results
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
