from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class LoginRequest(BaseModel):
    login: str
    password: str

class AddUser(BaseModel):
    username: str
    password: str
    name: str

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(128))
    name = Column(String(50))
    savedwords = Column(String(500))
    timestamp = Column(DateTime)

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str = None
    
class Dictionary(Base):
    __tablename__ = "dictionary"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(50), unique=True, index=True)
    description = Column(Text)

class WordCreate(BaseModel):
    word: str
    description: str
class WordDelete(BaseModel):
    word: str