from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
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
    content: str



class FavoriteRequest(BaseModel):
    user_id: str
    sauna_id: str

class FavoriteResponse(BaseModel):
    id: int
    user_id: str
    sauna_id: str

    class Config:
        orm_mode = True

class RemoveFavoriteRequest(BaseModel):
    user_id: str
    sauna_id: str


# ルートエンドポイント
@app.get("/")
async def root():
    return {"message": "Welcome to the Sauna App API"}


# ユーザー一覧取得
@app.get("/users", response_model=List[UserCreate], tags=["users"])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# ユーザー作成
@app.post("/users", tags=["users"])
def create_or_update_user(user: UserCreate, db: Session = Depends(get_db)):
    print("受け取ったユーザー情報:", user)
    existing_user = db.query(User).filter(User.id == user.id).first()
    if existing_user:
        # ユーザー情報を更新
        existing_user.email = user.email
        existing_user.name = user.name
        db.commit()
        db.refresh(existing_user)
        return existing_user

    # 新しいユーザーを作成
    new_user = User(id=user.id, email=user.email, name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



def fetch_sauna_details_from_google(place_id: str):
    """
    Google Places APIを使用して指定されたplace_idの詳細情報を取得する
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_PLACES_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Google Places API リクエストに失敗しました")
    result = response.json().get("result")
    if not result:
        raise HTTPException(status_code=404, detail="指定されたplace_idに対応するサウナ情報が見つかりません")
    
    # 都道府県を取得 (address_components から "administrative_area_level_1" を検索)
    address_components = result.get("address_components", [])
    prefecture = None
    for component in address_components:
        if "administrative_area_level_1" in component.get("types", []):
            prefecture = component.get("long_name")
            break

    # デフォルト値を設定
    if not prefecture:
        prefecture = "Unknown Prefecture"

    return {
        "id": place_id,
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "prefecture": prefecture,
        "latitude": result.get("geometry", {}).get("location", {}).get("lat"),
        "longitude": result.get("geometry", {}).get("location", {}).get("lng"),
    }

def insert_sauna_to_db(sauna_data: dict, db: Session):
    """
    サウナ情報をデータベースに挿入する
    """
    existing_sauna = db.query(Sauna).filter(Sauna.id == sauna_data["id"]).first()
    if existing_sauna:
        return existing_sauna
    new_sauna = Sauna(
        id=sauna_data["id"],
        name=sauna_data["name"],
        address=sauna_data["address"],
        prefecture=sauna_data["prefecture"],
        latitude=str(sauna_data["latitude"]),
        longitude=str(sauna_data["longitude"]),
    )
    db.add(new_sauna)
    db.commit()
    db.refresh(new_sauna)
    return new_sauna


# サ活投稿作成
@app.post("/posts", tags=["posts"])
def create_post_with_sauna_registration(post: PostCreate, db: Session = Depends(get_db)):
    # ユーザーが存在するかチェック
    user = db.query(User).filter(User.id == post.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # サウナが存在するか確認
    sauna = db.query(Sauna).filter(Sauna.id == post.sauna_id).first()
    if not sauna:
        # サウナ情報が無ければGoogle Places APIから取得して登録
        sauna_data = fetch_sauna_details_from_google(post.sauna_id)
        sauna = insert_sauna_to_db(sauna_data, db)

    # 投稿作成
    new_post = Post(user_id=post.user_id, sauna_id=sauna.id, content=post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": "Post created successfully", "post": new_post}




# サ活投稿取得
@app.get("/posts", tags=["posts"])
def get_posts(sauna_id: Optional[str] = Query(None), user_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Post).options(joinedload(Post.user), joinedload(Post.sauna))
    
    if sauna_id:
        query = query.filter(Post.sauna_id == sauna_id)
    if user_id:
        query = query.filter(Post.user_id == user_id)

    posts = query.all()

    # 必要なデータのみを返すように変換
    return [
        {
            "id": post.id,
            "content": post.content,
            "created_at": post.created_at,
            "user": {
                "id": post.user.id,
                "name": post.user.name,
            },
            "sauna": {
                "id": post.sauna.id,
                "name": post.sauna.name,
            },
        }
        for post in posts
    ]



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
    
     # 緯度・経度を取得
    location = result.get("geometry", {}).get("location", {})
    latitude = location.get("lat")
    longitude = location.get("lng")

    return {
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "rating": result.get("rating"),
        "photos": result.get("photos", []),
        "latitude": latitude,
        "longitude": longitude,
    }


#サウナ保存
@app.post("/saunas", tags=["saunas"])
def save_sauna(
    id: str,
    name: str,
    address: str,
    prefecture: Optional[str],
    latitude: str,
    longitude: str,
    db: Session = Depends(get_db),
):
    """
    Google Places から取得したサウナをデータベースに保存
    """
    # サウナが既に存在するか確認
    existing_sauna = db.query(Sauna).filter(Sauna.id == id).first()
    if existing_sauna:
        return {"message": "Sauna already exists", "sauna": existing_sauna}

    # 新しいサウナを作成
    new_sauna = Sauna(
        id=id,
        name=name,
        address=address,
        prefecture=prefecture,
        latitude=latitude,
        longitude=longitude,
    )
    db.add(new_sauna)
    db.commit()
    db.refresh(new_sauna)
    return {"message": "Sauna saved successfully", "sauna": new_sauna}



# お気に入り追加・取得・削除
@app.post("/favorites", tags=["favorites"])
def create_favorite_with_sauna_registration(
    favorite_request: FavoriteRequest, db: Session = Depends(get_db)
):
    # ユーザーが存在するか確認
    user = db.query(User).filter(User.id == favorite_request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # サウナが存在するか確認
    sauna = db.query(Sauna).filter(Sauna.id == favorite_request.sauna_id).first()
    if not sauna:
        # サウナ情報が無ければGoogle Places APIから取得して登録
        sauna_data = fetch_sauna_details_from_google(favorite_request.sauna_id)
        sauna = insert_sauna_to_db(sauna_data, db)

    # お気に入りが既に登録されていないか確認
    existing_favorite = (
        db.query(Favorite)
        .filter_by(user_id=favorite_request.user_id, sauna_id=sauna.id)
        .first()
    )
    if existing_favorite:
        raise HTTPException(status_code=400, detail="This sauna is already in favorites")

    # お気に入りを登録
    new_favorite = Favorite(user_id=favorite_request.user_id, sauna_id=sauna.id)
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)

    return {"message": "Favorite created successfully", "favorite": new_favorite}

@app.get("/favorites", tags=["favorites"])
def get_favorites(db: Session = Depends(get_db)):
    favorites = db.query(Favorite).all()
    return {"favorites": favorites}


@app.delete("/favorites/{favorite_id}", tags=["favorites"])
def remove_favorite(favorite_id: int, db: Session = Depends(get_db)):
    favorite = db.query(Favorite).filter(Favorite.id == favorite_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
    return {"message": f"Favorite {favorite_id} removed successfully"}
