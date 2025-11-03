"""
Unified OpenRouter API client for WorldWhisperer.
Centralizes all OpenRouter API calls with consistent error handling and configuration.
"""

import os
import requests
from typing import Optional, Dict, List, Union


class OpenRouterClient:
    """Client for making requests to the OpenRouter API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key (defaults to env var)
            model: Default model to use (defaults to env var)
        """
        self.api_key = api_key or os.getenv('openrouter_api_key')
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable.")

        self.default_model = model or os.getenv('openrouter_model', 'anthropic/claude-3.5-sonnet')
        self.site_url = os.getenv('openrouter_site_url', 'http://localhost')
        self.site_name = os.getenv('openrouter_site_name', 'WorldWhisperer')
        self.base_url = 'https://openrouter.ai/api/v1'

    def _make_request(
        self,
        endpoint: str,
        method: str = 'POST',
        payload: Optional[Dict] = None
    ) -> Dict:
        """
        Make a request to the OpenRouter API.

        Args:
            endpoint: API endpoint (e.g., '/chat/completions')
            method: HTTP method
            payload: Request payload

        Returns:
            API response as dictionary

        Raises:
            Exception: If API request fails
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'HTTP-Referer': self.site_url,
            'X-Title': self.site_name,
            'Content-Type': 'application/json'
        }

        url = f"{self.base_url}{endpoint}"

        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=payload, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

        return response.json()

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Create a chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to client's default model)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional API parameters

        Returns:
            Generated text content

        Example:
            >>> client = OpenRouterClient()
            >>> messages = [{"role": "user", "content": "Hello!"}]
            >>> response = client.chat_completion(messages)
        """
        payload = {
            'model': model or self.default_model,
            'messages': messages,
            'temperature': temperature,
            **kwargs
        }

        if max_tokens:
            payload['max_tokens'] = max_tokens

        result = self._make_request('/chat/completions', method='POST', payload=payload)
        return result['choices'][0]['message']['content']

    def simple_prompt(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 1.0,
        system_message: Optional[str] = None
    ) -> str:
        """
        Simple single-turn prompt (convenience method).

        Args:
            prompt: User prompt
            model: Model to use
            temperature: Sampling temperature
            system_message: Optional system message to prepend

        Returns:
            Generated response
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        return self.chat_completion(messages, model=model, temperature=temperature)

    def get_available_models(self) -> List[Dict]:
        """
        Get list of available models from OpenRouter.

        Returns:
            List of model information dictionaries
        """
        result = self._make_request('/models', method='GET')
        return result.get('data', [])

    def check_model_available(self, model_id: str) -> bool:
        """
        Check if a specific model is available.

        Args:
            model_id: Model ID to check (e.g., 'anthropic/claude-3.5-sonnet')

        Returns:
            True if model is available, False otherwise
        """
        try:
            models = self.get_available_models()
            model_ids = [m['id'] for m in models]
            return model_id in model_ids
        except Exception:
            return False


# Global client instance (lazy-loaded)
_global_client: Optional[OpenRouterClient] = None


def get_client() -> OpenRouterClient:
    """
    Get the global OpenRouter client instance (creates if not exists).

    Returns:
        OpenRouterClient instance
    """
    global _global_client
    if _global_client is None:
        _global_client = OpenRouterClient()
    return _global_client


def reset_client():
    """Reset the global client instance (useful for testing or config changes)."""
    global _global_client
    _global_client = None