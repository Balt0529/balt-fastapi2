from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import init_db, get_db
from models import User, Post, Favorite, Sauna
from pydantic import BaseModel
from typing import List, Optional
import requests, os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーとデータベースURLを取得
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not GOOGLE_PLACES_API_KEY:
    raise ValueError("Google Places APIキーが設定されていません")
if not DATABASE_URL:
    raise ValueError("データベースURLが設定されていません")

# アプリケーション初期化
app = FastAPI()

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# アプリ起動時の処理
@app.on_event("startup")
def startup_event():
    init_db()

# Pydanticスキーマ定義
class UserCreate(BaseModel):
    id: str
    email: str
    name: str


class PostCreate(BaseModel):
    user_id: str
    sauna_id: str
    content: Optional[str]


class PostResponse(BaseModel):
    id: int
    user_id: str
    sauna_id: str
    content: Optional[str]
    created_at: str

    class Config:
        orm_mode = True


class FavoriteRequest(BaseModel):
    user_id: str
    sauna_id: str

class FavoriteResponse(BaseModel):
    id: int
    user_id: str
    sauna_id: str

    class Config:
        orm_mode = True


# ルートエンドポイント
@app.get("/")
async def root():
    return {"message": "Welcome to the Sauna App API"}


# ユーザー一覧取得
@app.get("/users", response_model=List[UserCreate], tags=["users"])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# ユーザー作成
@app.post("/users", tags=["users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(id=user.id, email=user.email, name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# サ活投稿作成
@app.post("/posts", tags=["posts"])
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    sauna = db.query(Sauna).filter(Sauna.id == post.sauna_id).first()
    if not sauna:
        raise HTTPException(status_code=404, detail="サウナが見つかりません")
    new_post = Post(user_id=post.user_id, sauna_id=post.sauna_id, content=post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post



# サ活投稿取得
@app.get("/posts", tags=["posts"])
def get_posts(sauna_id: str = Query(...), db: Session = Depends(get_db)):
    # sauna_id を文字列としてそのまま扱う
    posts = db.query(Post).filter(Post.sauna_id == sauna_id).all()
    return posts




# サ活投稿削除
@app.delete("/posts/{post_id}", tags=["posts"])
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": f"Post {post_id} deleted successfully"}


# サウナ検索
@app.get("/saunas", tags=["saunas"])
def search_saunas(
    prefecture: str = Query(None),
    keyword: str = Query(None),
):
    
    # クエリログを出力
    print(f"Received prefecture: {prefecture}, keyword: {keyword}")

    if not (prefecture or keyword):
        raise HTTPException(status_code=400, detail="検索条件が指定されていません。")

    # Google Places API リクエストの準備
    location = "35.6895,139.6917"  # デフォルトの中心座標（東京駅付近）
    radius = 50000  # 半径50km
    search_keyword = f"{prefecture or ''} {keyword or ''} サウナ".strip()

    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "key": GOOGLE_PLACES_API_KEY,
        "query": search_keyword,
        "radius": radius,
        "location": location,
    }

    # Google Places APIのリクエスト送信
    response = requests.get(url, params=params)
    print(f"Google API Request URL: {response.url}")  # 確認用ログ

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Google Places APIのリクエストに失敗しました。")

    # レスポンスの処理
    google_results = response.json().get("results", [])
    print(f"Google API Results: {google_results}")  # 確認用ログ

    if not google_results:
        return {"message": "該当するサウナが見つかりませんでした。"}

    # 結果を加工して返す
    saunas = [
        {
            "id": result.get("place_id"),
            "name": result.get("name"),
            "address": result.get("formatted_address", result.get("vicinity", "住所不明")),
            "rating": result.get("rating"),
        }
        for result in google_results
    ]

    return saunas

#サウナ詳細
@app.get("/saunas/{place_id}")
def get_sauna_details(place_id: str):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_PLACES_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Google Places API リクエストに失敗しました。")
    
    result = response.json().get("result")
    if not result:
        raise HTTPException(status_code=404, detail="サウナが見つかりません。")

    return {
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "rating": result.get("rating"),
        "photos": result.get("photos", []),
    }


@app.post("/favorites/")
async def add_favorite(favorite_request: FavoriteRequest, db: Session = Depends(get_db)):
    user_id = favorite_request.user_id
    sauna_id = favorite_request.sauna_id

    # 重複確認
    favorite = db.query(Favorite).filter_by(user_id=user_id, sauna_id=sauna_id).first()
    if favorite:
        raise HTTPException(status_code=400, detail="This sauna is already in favorites.")
    
    new_favorite = Favorite(user_id=user_id, sauna_id=sauna_id)
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return {"message": "Favorite added successfully.", "favorite": new_favorite}

@app.delete("/favorites/")
async def remove_favorite(user_id: str, sauna_id: str, db: Session = Depends(get_db)):
    favorite = db.query(Favorite).filter_by(user_id=user_id, sauna_id=sauna_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found.")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Favorite removed successfully."}

@app.get("/favorites/{user_id}")
async def get_favorites(user_id: str, db: Session = Depends(get_db)):
    favorites = db.query(Favorite).filter_by(user_id=user_id).all()
    saunas = [db.query(Sauna).filter_by(id=f.sauna_id).first() for f in favorites]
    return {"favorites": saunas}