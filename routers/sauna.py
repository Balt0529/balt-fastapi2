from fastapi import APIRouter, Query
from supabase import create_client, Client

router = APIRouter()

# Supabaseクライアントの初期化
url = "https://your-supabase-url.supabase.co"
key = "your-supabase-key"
supabase: Client = create_client(url, key)

@router.get("/search-saunas")
async def search_saunas(lat: float, lng: float, radius: int = 50000):
    """
    指定した座標と半径でサウナを検索
    """
    # サンプル：サウナ情報をSupabaseから取得
    response = supabase.table("saunas").select("*").execute()
    return response.data
