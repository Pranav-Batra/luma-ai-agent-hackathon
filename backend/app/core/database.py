import os
from functools import lru_cache

from supabase import Client, create_client


@lru_cache
def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (service role, server-side only)."
        )
    return create_client(url, key)
