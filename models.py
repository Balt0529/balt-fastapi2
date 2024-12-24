from sqlalchemy import Column, String, Integer, TIMESTAMP, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

# Baseクラスを定義（モデルを定義するためのベースクラス）
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String(255), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(Text, nullable=True)

    # Relationship
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    place_id = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id}, place_id={self.place_id}, content={self.content}, created_at={self.created_at})>"


class Favorite(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    place_id = Column(Text, nullable=False)

    # Relationship
    user = relationship("User", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, place_id={self.place_id})>"
