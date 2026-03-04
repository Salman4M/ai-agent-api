from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True,nullable=False)
    email = Column(String, unique=True,nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    refresh_tokens = relationship("RefreshToken",back_populates="user")
    conversations = relationship("Conversation",back_populates="user")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True,nullable=False)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    expires_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=datetime.utcnow)

    user = relationship("User",back_populates="refresh_tokens")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    steps = Column(JSON, default=list)
    created_at = Column(DateTime, default = datetime.utcnow)

    user = relationship("User",back_populates="conversations")

