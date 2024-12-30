from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# モデル用のBase
Base = declarative_base()

# 接続先DBの設定
DATABASE_URL = "postgresql+psycopg2://postgres:passwd@localhost:5433/sauna_db"

# Engine の作成
engine = create_engine(
    DATABASE_URL,
    echo=True  # ログ出力を有効化
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
