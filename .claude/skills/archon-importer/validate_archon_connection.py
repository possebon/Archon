#!/usr/bin/env python3
"""
Archon Connection Validator

Validates Archon backend connectivity and required configurations.
Implements health checks before attempting import.
"""

import aiohttp
from typing import Any


class ArchonValidator:
    """Validates Archon backend prerequisites."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.backend_url = config["archon_backend_url"]

    async def validate(self) -> dict[str, Any]:
        """Run all validation checks."""
        result = {
            "backend_reachable": False,
            "llm_provider_configured": False,
            "embedding_provider_configured": False,
            "errors": [],
        }

        # Check backend connectivity
        try:
            backend_status = await self._check_backend_health()
            result["backend_reachable"] = backend_status["healthy"]

            if not backend_status["healthy"]:
                result["errors"].append(
                    f"Backend unhealthy: {backend_status.get('error', 'Unknown error')}"
                )
        except Exception as e:
            result["errors"].append(f"Cannot reach backend: {str(e)}")
            return result

        # Check LLM provider configuration
        try:
            llm_status = await self._check_llm_provider()
            result["llm_provider_configured"] = llm_status["configured"]
        except Exception as e:
            result["errors"].append(f"Failed to check LLM provider: {str(e)}")

        # Check embedding provider configuration
        try:
            embedding_status = await self._check_embedding_provider()
            result["embedding_provider_configured"] = embedding_status["configured"]

            if not embedding_status["configured"]:
                result["errors"].append(
                    "Embedding provider not configured - required for knowledge base"
                )
        except Exception as e:
            result["errors"].append(f"Failed to check embedding provider: {str(e)}")

        return result

    async def _check_backend_health(self) -> dict[str, Any]:
        """Check if Archon backend is healthy."""
        health_url = f"{self.backend_url}/api/health"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "healthy": data.get("status") == "healthy",
                            "service": data.get("service"),
                        }
                    else:
                        return {
                            "healthy": False,
                            "error": f"HTTP {response.status}",
                        }
            except aiohttp.ClientError as e:
                return {
                    "healthy": False,
                    "error": str(e),
                }

    async def _check_llm_provider(self) -> dict[str, Any]:
        """Check if LLM provider is configured."""
        # Check settings endpoint for active LLM provider
        settings_url = f"{self.backend_url}/api/settings"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    settings_url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Check if any LLM provider has an API key
                        providers = ["openai", "anthropic", "google", "ollama"]
                        for provider in providers:
                            key = data.get(f"{provider}_api_key")
                            if key and key.strip():
                                return {
                                    "configured": True,
                                    "provider": provider,
                                }

                        return {"configured": False}
                    else:
                        return {"configured": False, "error": f"HTTP {response.status}"}
            except Exception as e:
                # If we can't check, assume not configured
                return {"configured": False, "error": str(e)}

    async def _check_embedding_provider(self) -> dict[str, Any]:
        """Check if embedding provider is configured."""
        # Similar to LLM check but for embedding providers
        settings_url = f"{self.backend_url}/api/settings"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    settings_url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Check for embedding provider configuration
                        # OpenAI and Ollama can provide embeddings
                        providers = ["openai", "ollama"]
                        for provider in providers:
                            key = data.get(f"{provider}_api_key")
                            if key and key.strip():
                                return {
                                    "configured": True,
                                    "provider": provider,
                                }

                        return {"configured": False}
                    else:
                        return {"configured": False, "error": f"HTTP {response.status}"}
            except Exception as e:
                return {"configured": False, "error": str(e)}
