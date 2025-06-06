from functools import lru_cache

from supabase import create_client  # type: ignore[attr-defined]
from supabase._sync.client import SyncClient

from app.core.config import settings


@lru_cache
def get_supabase_client() -> SyncClient:
    """Get Supabase client instance (cached)."""
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_key,
    )


@lru_cache
def get_supabase_service_client() -> SyncClient:
    """Get Supabase service role client instance (cached)."""
    if not settings.supabase_service_key:
        raise ValueError("SUPABASE_SERVICE_KEY not configured")

    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_key,
    )
