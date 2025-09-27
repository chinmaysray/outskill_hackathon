import asyncio
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
import httpx
from openai import AsyncOpenAI
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

class OpenRouterClient:
    """
    OpenRouter client for accessing multiple LLM models through a unified API.
    Compatible with OpenAI SDK for easy integration.
    """

    def __init__(self):
        self.client = None
        self.http_client = None
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key
        self.default_headers = {
            "HTTP-Referer": "https://multimodal-ai-design-suite.com",
            "X-Title": "Multimodal AI Design Analysis Suite"
        }

    async def initialize(self):
        """Initialize the OpenRouter client."""
        try:
            logger.info("Initializing OpenRouter client")

            # Initialize OpenAI-compatible client
            self.client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                default_headers=self.default_headers,
                timeout=60.0
            )

            # Initialize HTTP client for direct API calls
            self.http_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    **self.default_headers
                },
                timeout=60.0
            )

            # Test connection
            await self._test_connection()

            logger.info("OpenRouter client initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize OpenRouter client", error=str(e))
            raise

    async def cleanup(self):
        """Cleanup client connections."""
        if self.http_client:
            await self.http_client.aclose()
        if self.client:
            await self.client.close()

    async def _test_connection(self):
        """Test OpenRouter API connection."""
        try:
            response = await self.http_client.get("/models")
            if response.status_code != 200:
                raise Exception(f"API test failed with status {response.status_code}")
        except Exception as e:
            logger.error("OpenRouter connection test failed", error=str(e))
            raise

    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request to OpenRouter.

        Args:
            model: Model ID (e.g., 'openai/gpt-4-vision-preview')
            messages: List of message objects
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            Chat completion response
        """
        try:
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }

            if max_tokens:
                params["max_tokens"] = max_tokens

            if stream:
                return await self._stream_chat_completion(params)
            else:
                response = await self.client.chat.completions.create(**params)
                return self._parse_response(response)

        except Exception as e:
            logger.error("Chat completion failed", model=model, error=str(e))
            raise

    async def _stream_chat_completion(self, params: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completion response."""
        try:
            async for chunk in await self.client.chat.completions.create(stream=True, **params):
                if chunk.choices[0].delta.content:
                    yield {
                        "content": chunk.choices[0].delta.content,
                        "finish_reason": chunk.choices[0].finish_reason
                    }
        except Exception as e:
            logger.error("Streaming chat completion failed", error=str(e))
            raise

    async def vision_analysis(
        self,
        image_data: bytes,
        prompt: str,
        model: str = None,
        detail: str = "high"
    ) -> Dict[str, Any]:
        """
        Analyze image using vision-capable model.

        Args:
            image_data: Image bytes
            prompt: Analysis prompt
            model: Vision model to use
            detail: Image detail level ('low', 'high', 'auto')

        Returns:
            Vision analysis response
        """
        try:
            model = model or settings.default_vision_model
            logger.info("Starting vision analysis", model=model, image_size=len(image_data), prompt_length=len(prompt))

            # Convert image to base64 for API
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": detail
                            }
                        }
                    ]
                }
            ]

            logger.info("Sending vision chat completion request", model=model, messages_count=len(messages))
            response = await self.chat_completion(
                model=model,
                messages=messages,
                max_tokens=1500
            )
            
            logger.info("Received vision chat completion response", model=model, response_type=type(response), has_content=bool(response.get("content")))
            return response

        except Exception as e:
            logger.error("Vision analysis failed", model=model, error=str(e))
            raise

    async def text_analysis(
        self,
        prompt: str,
        context: Optional[str] = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Perform text-based analysis.

        Args:
            prompt: Analysis prompt
            context: Additional context
            model: Text model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Text analysis response
        """
        try:
            model = model or settings.default_text_model
            logger.info("Starting text analysis", model=model, prompt_length=len(prompt))

            messages = [
                {"role": "system", "content": "You are an expert design analyst providing detailed, actionable insights."}
            ]

            if context:
                messages.append({"role": "user", "content": f"Context: {context}"})

            messages.append({"role": "user", "content": prompt})

            logger.info("Sending chat completion request", model=model, messages_count=len(messages))
            response = await self.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            logger.info("Received chat completion response", model=model, response_type=type(response), has_content=bool(response.get("content")))
            return response

        except Exception as e:
            logger.error("Text analysis failed", model=model, error=str(e))
            raise

    async def code_analysis(
        self,
        prompt: str,
        code_context: Optional[str] = None,
        model: str = None
    ) -> Dict[str, Any]:
        """
        Perform code-based technical analysis.

        Args:
            prompt: Analysis prompt
            code_context: Code or technical context
            model: Code model to use

        Returns:
            Code analysis response
        """
        try:
            model = model or settings.code_analysis_model

            messages = [
                {"role": "system", "content": "You are a senior software architect specializing in UI/UX implementation and technical feasibility analysis."}
            ]

            if code_context:
                messages.append({"role": "user", "content": f"Technical Context: {code_context}"})

            messages.append({"role": "user", "content": prompt})

            response = await self.chat_completion(
                model=model,
                messages=messages,
                temperature=0.3,  # Lower temperature for technical analysis
                max_tokens=1500
            )

            return response

        except Exception as e:
            logger.error("Code analysis failed", model=model, error=str(e))
            raise

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter."""
        try:
            response = await self.http_client.get("/models")
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error("Failed to fetch models", status_code=response.status_code)
                return []
        except Exception as e:
            logger.error("Failed to get available models", error=str(e))
            return []

    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse OpenAI response format."""
        try:
            content = response.choices[0].message.content
            if not content:
                logger.warning("Empty content in response", finish_reason=response.choices[0].finish_reason)
            
            return {
                "content": content or "",
                "usage": response.usage.dict() if response.usage else {},
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            logger.error("Failed to parse response", error=str(e), response_type=type(response))
            return {"content": "", "error": str(e)}

    async def batch_completion(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Process multiple completion requests concurrently.

        Args:
            requests: List of completion request parameters
            max_concurrent: Maximum concurrent requests

        Returns:
            List of completion responses
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_request(request_params: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    return await self.chat_completion(**request_params)
                except Exception as e:
                    logger.error("Batch request failed", error=str(e))
                    return {"error": str(e)}

        tasks = [process_request(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)
