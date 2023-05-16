import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.db import get_db
from app.models import User, LoginRequest, Dictionary, UserCreate, AddUser, WordCreate, WordDelete
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

security = HTTPBasic()

########## USER FUNCTIONS
#works
@router.post("/login")
def login(request_body: LoginRequest, response: Response, db: Session = Depends(get_db),):
    user = db.query(User).filter(User.username == request_body.login).first()
    if not user or user.password != request_body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    response.set_cookie(key="session", value="my_session_value", expires=datetime.utcnow() + timedelta(hours=1),
                        secure=True)
    return {"username": user.username}

#works
@router.get("/words/{word}")
def get_word_by_name(word: str, db: Session = Depends(get_db)):
    result = db.query(Dictionary).filter_by(word=word).all()
    return result
#works
@router.get("/users/{username}")
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content={"id": user.id, "username": user.username, "name": user.name, "savedwords": user.savedwords, "timestamp": user.timestamp})

## ADMIN ENDPOINTS
#works
@router.get("/all_users/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": users}

#works
@router.post("/add_user")
def create_user(request_body: AddUser, db: Session = Depends(get_db)):
    # Check if the username already exists
    if db.query(User).filter(User.username == request_body.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    # Create a new user and add it to the database session
    new_user = User(username=request_body.username, password=request_body.password, name=request_body.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

#works
@router.delete("/delete_users")
def delete_users(usernames: List[str], db: Session = Depends(get_db)):
    deleted_users = []
    for username in usernames:
        user = db.query(User).filter(User.username == username).first()
        if user:
            db.delete(user)
            deleted_users.append(username)
    db.commit()
    return {"deleted_users": deleted_users}

@router.post("/users/create/batch/")
def create_users(users: List[UserCreate], db : Session = Depends(get_db)):
    added_users = []
    for user in users:
        if db.query(User).filter(User.username == user['username']).first():
            pass
        # Create a new user and add it to the database session
        new_user = User(username=user['username'], password=user['password'])
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    # Return a message indicating the users were added successfully
    return {"message": f"{len(added_users)} Users added successfully"}

#working
@router.post("/add_dictionary")
def create_word(request_body: WordCreate, request: Request, db: Session = Depends(get_db)):
    # Check if the word already exists in the database
    db_word = db.query(Dictionary).filter(Dictionary.word == request_body.word).first()
    if db_word:
        raise HTTPException(status_code=400, detail="Word already exists")

    # Create a new word in the database
    new_word = Dictionary(word=request_body.word, description=request_body.description, id=random.randint(1, 9999999))
    db.add(new_word)
    db.commit()
    db.refresh(new_word)
    request.app.state.trie.insert(request_body.word)

    return {"message": "Word added successfully"}

#working
@router.delete("/delete_dictionary")
def delete_word(request_body: List[str], request: Request, db: Session = Depends(get_db)):
    # Check if the word already exists in the database
    deleted_words = []
    for word in request_body:
        db_word = db.query(Dictionary).filter(Dictionary.word == word).first()
        if db_word:
            db.delete(db_word)
            deleted_words.append(word)

    return {"message": f"{deleted_words} deleted successfully"}

#working
@router.get("/all_words")
def read_words(db: Session = Depends(get_db)):
    words = db.query(Dictionary).all()
    return {"words": words}

@router.get("/search")
async def search(word: str, request: Request) -> List[str]:
    results = request.app.state.trie.search(word)
    return results[:10]