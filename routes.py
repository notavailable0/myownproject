import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.db import get_db2
from app.models import DeeplKey, DeeplKeyResponse, User, UserCreate, FirstLayer, FirstLayerCreate, CoreLayer, CoreLayerCreate
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from typing import List

router = APIRouter()
security = HTTPBasic()

## USERS STUFF - DB CRUD ##
@router.post("/users/")
async def create_user(user: UserCreate, db=Depends(get_db2)):
    try:
        new_user = User(
            username=user.username,
            password=user.password,
            is_admin=user.is_admin,
            is_super_admin=user.is_super_admin,
            added_by=user.added_by,
            liked_words=user.liked_words,
            to_learn=user.to_learn
        )
        db.add(new_user)
        await db.commit()

        # Index the user in Elasticsearch
        user_id = new_user.id
        es.index(index="users", id=user_id, body={"username": user.username})
        return {"id": user_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.get("/users/{user_id}")
async def get_user(user_id: int, db=Depends(get_db2)):
    try:
        user = await db.get(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch user")

@router.put("/users/{user_id}")
async def update_user(user_id: int, updated_user: UserCreate, db=Depends(get_db2)):
    try:
        user = await db.get(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        for key, value in updated_user.dict().items():
            setattr(user, key, value)

        await db.commit()

        # Update the user in Elasticsearch
        es.update(index="users", id=user_id, body={"doc": {"username": updated_user.username}})
        return {"message": "User updated successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db=Depends(get_db2)):
    try:
        user = await db.get(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        await db.delete(user)
        await db.commit()

        # Delete the user from Elasticsearch
        es.delete(index="users", id=user_id)
        return {"message": "User deleted successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete user")

@router.get("/users/")
async def get_all_users(db=Depends(get_db2)):
    try:
        users = await db.get(User).all()
        return users
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch users")

## Search functionality ##
@router.get("/users/search")
async def search_users(keyword: str, db=Depends(get_db2)) -> List[str]:
    try:
        # Use Elasticsearch for searching
        search_body = {
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["username", "liked_words", "to_learn"]
                }
            }
        }
        search_results = es.search(index="users", body=search_body)
        hits = search_results["hits"]["hits"]
        return [hit["_source"]["username"] for hit in hits]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to perform search")

## FIRST LAYER STUFF - DB CRUD##
@router.post("/first_layer/")
async def create_record(record: FirstLayerCreate, db=Depends(get_db2)):
    try:
        new_record = FirstLayer(
            word=record.word,
            meaning=record.meaning,
            is_private=record.is_private,
            who_added=record.who_added,
            who_agreed=record.who_agreed,
            deepl_translation=record.deepl_translation
        )
        db.add(new_record)
        await db.commit()

        # Index the record in Elasticsearch
        record_id = new_record.pre_id
        es.index(index="first_layer", id=record_id, body={"word": record.word})
        return {"id": record_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create record")

@router.get("/first_layer/{pre_id}")
async def get_record(pre_id: int, db=Depends(get_db2)):
    try:
        record = await db.get(FirstLayer).filter(FirstLayer.pre_id == pre_id).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch record")

@router.put("/first_layer/{pre_id}")
async def update_record(pre_id: int, updated_record: FirstLayerCreate, db=Depends(get_db2)):
    try:
        record = await db.get(FirstLayer).filter(FirstLayer.pre_id == pre_id).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")

        for key, value in updated_record.dict().items():
            setattr(record, key, value)

        await db.commit()

        # Update the record in Elasticsearch
        es.update(index="first_layer", id=pre_id, body={"doc": {"word": updated_record.word}})
        return {"message": "Record updated successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update record")

@router.delete("/first_layer/{pre_id}")
async def delete_record(pre_id: int, db=Depends(get_db2)):
    try:
        record = await db.get(FirstLayer).filter(FirstLayer.pre_id == pre_id).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")

        await db.delete(record)
        await db.commit()

        # Delete the record from Elasticsearch
        es.delete(index="first_layer", id=pre_id)
        return {"message": "Record deleted successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete record")

@router.get("/first_layer/")
async def get_all_records(db=Depends(get_db2)):
    try:
        records = await db.get(FirstLayer).all()
        return records
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch records")

@router.get("/first_layer/search")
async def search_first_layer(querrying: str, db=Depends(get_db2)) -> List[str]:
    try:
        # Use Elasticsearch for searching
        search_body = {
            "query": {
                "multi_match": {
                    "query": querrying,
                    "fields": ["word", "meaning", "deepl_translation"]
                }
            }
        }
        search_results = es.search(index="first_layer", body=search_body)
        hits = search_results["hits"]["hits"]
        return [hit["_source"]["word"] for hit in hits]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to perform search")

## CORE LAYER STUFF - DB CRUD ##
@router.post("/core_layer/")
async def create_record(record: CoreLayerCreate, db=Depends(get_db2)):
    try:
        new_record = CoreLayer(
            word=record.word,
            meaning=record.meaning,
            is_private=record.is_private,
            who_added=record.who_added,
            who_agreed=record.who_agreed,
            deepl_translation=record.deepl_translation,
            additional_translation=record.additional_translation
        )
        db.add(new_record)
        await db.commit()

        # Index the record in Elasticsearch
        record_id = new_record.id
        es.index(index="core_layer", id=record_id, body={"word": record.word})
        return {"id": record_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create record")

@router.get("/core_layer/{record_id}")
async def get_record(record_id: int, db=Depends(get_db2)):
    try:
        record = await db.get(CoreLayer).filter(CoreLayer.id == record_id).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch record")

@router.put("/core_layer/{record_id}")
async def update_record(record_id: int, updated_record: CoreLayerCreate, db=Depends(get_db2)):
    try:
        record = await db.get(CoreLayer).filter(CoreLayer.id == record_id).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")

        for key, value in updated_record.dict().items():
            setattr(record, key, value)

        await db.commit()

        # Update the record in Elasticsearch
        es.update(index="core_layer", id=record_id, body={"doc": {"word": updated_record.word}})
        return {"message": "Record updated successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update record")

@router.delete("/core_layer/{record_id}")
async def delete_record(record_id: int, db=Depends(get_db2)):
    try:
        record = await db.get(CoreLayer).filter(CoreLayer.id == record_id).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")

        await db.delete(record)
        await db.commit()

        # Delete the record from Elasticsearch
        es.delete(index="core_layer", id=record_id)
        return {"message": "Record deleted successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete record")

@router.get("/core_layer/")
async def get_all_records(db=Depends(get_db2)):
    try:
        records = await db.get(CoreLayer).all()
        return records
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch records")

## Search functionality ##
@router.get("/core_layer/search")
async def search_core_layer(keyword: str, db=Depends(get_db2)) -> List[str]:
    try:
        # Use Elasticsearch for searching
        search_body = {
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["word", "meaning", "deepl_translation", "additional_translation"]
                }
            }
        }
        search_results = es.search(index="core_layer", body=search_body)
        hits = search_results["hits"]["hits"]
        return [hit["_source"]["word"] for hit in hits]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to perform search")

## DEEPL KEYS STUFF - CRUD DB ##
@router.post("/deepl_keys/")
async def create_deepl_key(key: str, db=Depends(get_db2)):
    try:
        db_key = DeeplKey(key=key)
        db.add(db_key)
        await db.commit()
        return db_key
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create deepl key")

@router.get("/deepl_keys/{key_id}")
async def read_deepl_key(key_id: int, db=Depends(get_db2)):
    try:
        db_key = await db.get(DeeplKey).filter(DeeplKey.id == key_id).first()
        if db_key is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return db_key
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch deepl key")

@router.put("/deepl_keys/{key_id}")
async def update_deepl_key(key_id: int, key: str, accessible: bool, db=Depends(get_db2)):
    try:
        db_key = await db.get(DeeplKey).filter(DeeplKey.id == key_id).first()
        if db_key is None:
            raise HTTPException(status_code=404, detail="Key not found")

        db_key.key = key
        db_key.accessible = accessible
        await db.commit()
        return db_key
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update deepl key")

@router.delete("/deepl_keys/{key_id}")
async def delete_deepl_key(key_id: int, db=Depends(get_db2)):
    try:
        db_key = await db.get(DeeplKey).filter(DeeplKey.id == key_id).first()
        if db_key is None:
            raise HTTPException(status_code=404, detail="Key not found")

        await db.delete(db_key)
        await db.commit()
        return db_key
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete deepl key")

@router.get("/deepl_keys/")
async def get_all_deepl_keys(db=Depends(get_db2)):
    try:
        keys = await db.get(DeeplKey).all()
        return keys
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch deepl keys")

## rework search functional ##
# @router.get("/search")
# async def search(word: str, request: Request, db = Depends(get_db2)) -> List[str]:
#     results = await db.get(Dictionary).filter(Dictionary.word.like(f'{word}%')).all()
#     r = []
#     for row in results:
#         r.append(row.word)
#     if isinstance(results, bool):
#         raise HTTPException(status_code=400, detail=request.app.state.trie)
#     return r[:10]
#
#
# ## todo: do something about fucking login cause idk you will have to login blyat
# @router.post("/login")
# async def login(request_body: LoginRequest, response: Response, db = Depends(get_db2)):
#     user = await db.get(User).filter(User.username == request_body.login).first()
#     if not user or user.password != request_body.password:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid login or password",
#             headers={"WWW-Authenticate": "Basic"},
#         )
#     response.set_cookie(
#         key="session",
#         value="my_session_value",
#         expires=datetime.utcnow() + timedelta(hours=1),
#         secure=True
#     )
#     return {"username": user.username}
