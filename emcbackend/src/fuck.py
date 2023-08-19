import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.db import get_db2
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, select
from typing import List
from elasticsearch import Elasticsearch

from src.app.models import DeeplKeyResponse

router = APIRouter()

security = HTTPBasic()

# ... SQLAlchemy Core table definitions ...

# ... Elasticsearch setup ...
es = Elasticsearch("localhost:9200")

## USERS STUFF - DB CRUD ##
@router.post("/users/")
async def create_user(user: UserCreate, db=Depends(get_db2)):
    try:
        new_user = users_table.insert().values(
            username=user.username,
            password=user.password,
            is_admin=user.is_admin,
            is_super_admin=user.is_super_admin,
            added_by=user.added_by,
            liked_words=user.liked_words,
            to_learn=user.to_learn
        )
        result = await db.execute(new_user)
        await db.commit()

        # Index the user in Elasticsearch
        user_id = result.lastrowid
        es.index(index="users", id=user_id, body={"username": user.username, "is_admin": user.is_admin})
        return user_id
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.get("/users/{user_id}")
async def get_user(user_id: int, db=Depends(get_db2)):
    try:
        # Retrieve the user from the database
        query = users_table.select().where(users_table.c.id == user_id)
        result = await db.execute(query)
        user = await result.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Get additional user information from Elasticsearch
        es_user = es.get(index="users", id=user_id)
        user["is_admin"] = es_user["_source"]["is_admin"]
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch user")

# Update an existing user
@router.put("/users/{user_id}")
async def update_user(user_id: int, updated_user: UserCreate, db=Depends(get_db2)):
    try:
        query = users_table.update().where(users_table.c.id == user_id).values(
            username=updated_user.username,
            password=updated_user.password,
            is_admin=updated_user.is_admin,
            is_super_admin=updated_user.is_super_admin,
            added_by=updated_user.added_by,
            liked_words=updated_user.liked_words,
            to_learn=updated_user.to_learn
        )
        result = await db.execute(query)
        await db.commit()

        # Update the user in Elasticsearch
        es.update(index="users", id=user_id, body={"doc": {"username": updated_user.username, "is_admin": updated_user.is_admin}})
        return result.rowcount
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user")

# Delete a user
@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db=Depends(get_db2)):
    try:
        query = users_table.delete().where(users_table.c.id == user_id)
        result = await db.execute(query)
        await db.commit()

        # Delete the user from Elasticsearch
        es.delete(index="users", id=user_id)
        return result.rowcount
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete user")

# Get all users
@router.get("/users/")
async def get_all_users(db=Depends(get_db2)):
    try:
        query = users_table.select()
        result = await db.execute(query)
        users = await result.fetchall()

        # Fetch additional user information from Elasticsearch
        user_ids = [user.id for user in users]
        es_users = es.mget(index="users", body={"ids": user_ids}, _source=["username", "is_admin"])
        es_users = {user["_id"]: user["_source"] for user in es_users["docs"]}

        for user in users:
            es_user = es_users.get(user.id)
            if es_user:
                user["is_admin"] = es_user.get("is_admin")

        return users
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch users")

# ... Repeat the same pattern for FirstLayer and CoreLayer CRUD operations ...

## DEEPL KEYS STUFF - CRUD DB ##
@router.post("/deepl_keys/", response_model=DeeplKeyResponse)
async def create_deepl_key(key: str, db=Depends(get_db2)):
    try:
        query = deepl_key_table.insert().values(key=key, accessible=True)
        result = await db.execute(query)
        await db.commit()

        # Index the Deepl Key in Elasticsearch
        key_id = result.lastrowid
        es.index(index="deepl_keys", id=key_id, body={"key": key, "accessible": True})
        return {"id": key_id, "key": key, "accessible": True}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create Deepl Key")

# ... Continue with other CRUD operations for DeeplKey ...

## Search functionality ##
@router.get("/search")
async def search(word: str, request: Request, db=Depends(get_db2)) -> List[str]:
    try:
        # Use Elasticsearch for searching
        search_results = es.search(index="your_index", body={"query": {"match": {"your_field": word}}})
        hits = search_results["hits"]["hits"]
        return [hit["_source"]["your_field"] for hit in hits]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to perform search")

## Login functionality (not implemented) ##
@router.post("/login")
async def login(request_body: LoginRequest, response: Response, db=Depends(get_db2)):
    # Implement your login functionality here using raw SQL queries
    # You can use raw SQL queries to fetch and authenticate users
    pass

