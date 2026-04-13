import os
from functools import lru_cache
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL", "NOT_SET")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "NOT_SET")
print(f"SUPABASE_URL={url}")
print(f"KEY_LENGTH={len(key)}")
print(f"KEY_START={key[:10]}")

@lru_cache
def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (service role, server-side only)."
        )
    return create_client(url, key)
