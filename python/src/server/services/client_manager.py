"""
Client Manager Service

Manages database and API client connections.
"""

import os
import re

from supabase import Client, create_client

from ..config.logfire_config import search_logger

# Module-level client cache to avoid recreating clients
_client_cache = None


def get_supabase_client() -> Client:
    """
    Get a cached Supabase client instance.

    NOTE: This uses the synchronous client which can block the event loop.
    For optimal performance, this should be migrated to AsyncClient.

    Returns:
        Supabase client instance
    """
    global _client_cache

    # Return cached client if available
    if _client_cache is not None:
        return _client_cache

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables"
        )

    try:
        # Create and cache client for reuse
        _client_cache = create_client(url, key)

        # Extract project ID from URL for logging purposes only
        match = re.match(r"https://([^.]+)\.supabase\.co", url)
        if match:
            project_id = match.group(1)
            search_logger.debug(f"Supabase client initialized - project_id={project_id}")

        return _client_cache
    except Exception as e:
        search_logger.error(f"Failed to create Supabase client: {e}")
        raise
