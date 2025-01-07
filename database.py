import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# モデル用のBase
Base = declarative_base()


# 環境変数からデータベースURLを取得
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("データベースURLが設定されていません")

# Engine の作成
engine = create_engine(
    DATABASE_URL,
    echo=True,  # ログ出力を有効化
)

# Sessionの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Scoped session (スレッドセーフ)
ScopedSession = scoped_session(SessionLocal)


# データベース初期化
def init_db():
    Base.metadata.create_all(bind=engine)


# データベースセッションを取得する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
