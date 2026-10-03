from typing import Optional
import logging

import httpx

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qualiprompt-engine",
        timeout: int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        format: Optional[str] = None,
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        if format == "json":
            payload["format"] = "json"

        try:
            response = await self._client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

        except httpx.ConnectError:
            logger.error(f"Nao foi possivel conectar ao Ollama em {self.base_url}")
            raise ConnectionError(
                f"Ollama nao esta respondendo em {self.base_url}. "
                "Execute 'ollama serve' primeiro."
            )
        except httpx.TimeoutException:
            logger.error(f"Timeout ao comunicar com Ollama (limite: {self.timeout}s)")
            raise TimeoutError(
                f"Ollama nao respondeu em {self.timeout} segundos."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama retornou erro HTTP {e.response.status_code}: {e.response.text}")
            raise

    async def generate_json(self, prompt: str, **kwargs) -> dict:
        result = await self.generate(prompt, format="json", **kwargs)
        import json

        try:
            return json.loads(result)
        except json.JSONDecodeError as e:
            logger.error(f"Resposta nao e JSON valido: {e}")
            raise ValueError(f"Ollama retornou resposta invalida (nao-JSON): {result[:200]}")

    async def health_check(self) -> bool:
        try:
            response = await self._client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            tags = response.json().get("models", [])
            models = [m["name"] for m in tags]
            if self.model not in models:
                logger.warning(
                    f"Modelo '{self.model}' nao encontrado. "
                    f"Disponiveis: {', '.join(models) if models else 'nenhum'}"
                )
                return False
            return True
        except Exception:
            return False
