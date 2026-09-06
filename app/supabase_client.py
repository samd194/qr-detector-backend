"""
Supabase client singleton initializer.
Import `supabase` from here anywhere you need Storage access.
"""
from supabase import create_client, Client

from app.config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)