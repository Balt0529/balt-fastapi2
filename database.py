from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import models

# 接続先DBの設定
DATABASE = 'postgresql+psycopg2://postgres:passwd@localhost:5433/sauna_db'

# Engine の作成
Engine = create_engine(
  DATABASE,
  echo=True
)

# Sessionの作成
session = Session(
  autocommit = False,
  autoflush = True,
  bind = Engine
)

def read_users():
    return session.query(models.User).all()

def read_posts():
    return session.query(models.Post).all()

def read_favorites():
    return session.query(models.Favorite).all()

def add_users(id,email,name):
    db_posts=models.User(id=id,email=email,name=name)
    session.add(db_posts)
    session.commit()
    session.refresh(db_posts)
    return db_posts

def add_posts(id,user_id,place_id,content,created_at):
    db_posts=models.Post(id=id,user_id=user_id,place_id=place_id,content=content,created_at=created_at)
    session.add(db_posts)
    session.commit()
    session.refresh(db_posts)
    return db_posts

def delete_posts(id):
    db_posts=session.query(models.Post).filter(models.Post.id==id).delete()
    return db_posts

