from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

JST = timezone(timedelta(hours=+9), "JST")


def get_jst_now():
    return datetime.now(JST)


class User(Base):
    __tablename__ = "users"

    id = Column(String(255), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(Text, nullable=True)

    # Relationship
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class Sauna(Base):
    __tablename__ = "saunas"

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    prefecture = Column(String(255), nullable=False)  # 都道府県名
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Relationship
    posts = relationship("Post", back_populates="sauna", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="sauna", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sauna(id={self.id}, name={self.name}, address={self.address}, prefecture={self.prefecture})>"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False)
    sauna_id = Column(String(255), ForeignKey("saunas.id"), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_jst_now)

    # Relationship
    user = relationship("User", back_populates="posts")
    sauna = relationship("Sauna", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id}, sauna_id={self.sauna_id}, content={self.content}, created_at={self.created_at})>"


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False)
    sauna_id = Column(String(255), ForeignKey("saunas.id"), nullable=False)

    # Relationship
    user = relationship("User", back_populates="favorites")
    sauna = relationship("Sauna", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, sauna_id={self.sauna_id})>"
