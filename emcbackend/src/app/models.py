from sqlalchemy import Column, Integer, String, DateTime, Text, func, TIMESTAMP, Boolean
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from datetime import datetime

Base = declarative_base()
## deepl_keys db
class DeeplKey(Base):
    __tablename__ = 'deepl_keys'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(255), index=True, unique=True, nullable=False)
    accessible = Column(Boolean, default=True)
    ts = Column(TIMESTAMP, default=datetime.utcnow)

class DeeplKeyResponse(BaseModel):
    id: int
    key: str
    accessible: bool
    ts: datetime

## users db
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=True, unique=True)
    password = Column(String(255), nullable=True)
    is_admin = Column(Boolean, nullable=True)
    is_super_admin = Column(Boolean, nullable=True)
    timestamp_added = Column(TIMESTAMP, nullable=True)
    added_by = Column(Integer, nullable=True)
    liked_words = Column(String(255), nullable=True)
    to_learn = Column(String(255), nullable=True)

## users db
class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool
    is_super_admin: bool
    added_by: int
    liked_words: str
    to_learn: str

# SQLAlchemy Model for the first_layer table
class FirstLayer(Base):
    __tablename__ = "first_layer"
    pre_id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(Text, nullable=True)
    meaning = Column(Text, nullable=True)
    is_private = Column(Boolean, nullable=True)
    who_added = Column(Integer, nullable=True)
    who_agreed = Column(Integer, nullable=True)
    deepl_translation = Column(Text, nullable=True)

# Pydantic Model for the response
class FirstLayerCreate(BaseModel):
    pre_id: int
    word: str
    meaning: str
    is_private: bool
    who_added: int
    who_agreed: int
    deepl_translation: str

# SQLAlchemy Model for the core_layer table
class CoreLayer(Base):
    __tablename__ = "core_layer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(Text, nullable=True)
    meaning = Column(Text, nullable=True)
    is_private = Column(Boolean, nullable=True)
    who_added = Column(Integer, nullable=True)
    who_agreed = Column(Integer, nullable=True)
    deepl_translation = Column(Text, nullable=True)
    additional_translation = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)

# Pydantic Model for input validation
class CoreLayerCreate(BaseModel):
    word: str
    meaning: str
    is_private: bool
    who_added: int
    who_agreed: int
    deepl_translation: str
    additional_translation: str