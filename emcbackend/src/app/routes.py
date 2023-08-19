from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.db import get_db2
from app.models import DeeplKey, User, UserCreate, FirstLayer, FirstLayerCreate, CoreLayer, CoreLayerCreate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, select
from typing import List

## todo: rewrite search to es, in case functional is not enough
## todo: utilize deepl glossary funcs to enable PERFECT TRANSFUCKINGLATION
router = APIRouter()

## USERS STUFF - DB CRUD ##
@router.post("/users/")
async def create_user(user: UserCreate, db=Depends(get_db2)):
    try:
        query = User.__table__.insert().values(
            username=user.username,
            password=user.password,
            is_admin=user.is_admin,
            is_super_admin=user.is_super_admin,
            added_by=user.added_by,
            liked_words=user.liked_words,
            to_learn=user.to_learn
        )

        result = await db.execute(query)
        user_id = result.inserted_primary_key[0]

        # Fetch the user data from the database using the inserted user_id
        new_user_query = select(User).where(User.id == user_id)
        new_user = await db.execute(new_user_query)
        user_data = new_user.fetchone()._asdict()

        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")

        await db.commit()

        return {"id": user_id, "user_data": user_data}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user")

@router.get("/users/{user_id}")
async def get_user(user_id: int, db=Depends(get_db2)):
    try:
        query = User.__table__.select().where(User.id == user_id)
        print(query)
        result = await db.execute(query)
        user = result.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user._asdict()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch user")

@router.put("/users/{user_id}")
async def update_user(user_id: int, updated_user: UserCreate, db=Depends(get_db2)):
    try:
        query = User.__table__.update().where(User.id == user_id).values(**updated_user.dict())
        await db.execute(query)
        await db.commit()
        return {"message": "User updated successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db=Depends(get_db2)):
    try:
        query = User.__table__.delete().where(User.id == user_id)
        await db.execute(query)
        await db.commit()
        return {"message": "User deleted successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete user")

@router.get("/users/")
async def get_all_users(db=Depends(get_db2)):
    try:
        query = User.__table__.select()
        result = await db.execute(query)
        users = result.fetchall()
        print(users)
        user = users[0]
        return [user._asdict() for user in users]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch users")

## Search functionality ##
@router.get("/users_search")
async def search_users(keyword: str, db=Depends(get_db2)) -> List[str]:
    try:
        query = text(
            "SELECT * FROM users WHERE username LIKE :keyword OR liked_words LIKE :keyword OR to_learn LIKE :keyword"
        ).params(keyword=f"%{keyword}%")
        result = await db.execute(query)
        users = result.fetchall()
        return [user.username for user in users]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to perform search")

## FIRST LAYER STUFF - DB CRUD##
@router.post("/first_layer/")
async def create_record(record: FirstLayerCreate, db=Depends(get_db2)):
    try:
        query = FirstLayer.__table__.insert().values(
            word=record.word,
            meaning=record.meaning,
            is_private=record.is_private,
            who_added=record.who_added,
            who_agreed=record.who_agreed,
            deepl_translation=record.deepl_translation
        )
        result = await db.execute(query)
        record_id = result.inserted_primary_key[0]
        await db.commit()
        return {"id": record_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create record")

@router.get("/first_layer/{pre_id}")
async def get_record(pre_id: int, db=Depends(get_db2)):
    try:
        query = FirstLayer.__table__.select().where(FirstLayer.pre_id == pre_id)
        result = await db.execute(query)
        record = result.fetchone()

        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return record._asdict()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch record")

@router.put("/first_layer/{pre_id}")
async def update_record(pre_id: int, updated_record: FirstLayerCreate, db=Depends(get_db2)):
    try:
        query = FirstLayer.__table__.update().where(FirstLayer.pre_id == pre_id).values(**updated_record.dict())
        await db.execute(query)
        await db.commit()
        return {"message": "Record updated successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update record")

@router.delete("/first_layer/{pre_id}")
async def delete_record(pre_id: int, db=Depends(get_db2)):
    try:
        query = FirstLayer.__table__.delete().where(FirstLayer.pre_id == pre_id)
        await db.execute(query)
        await db.commit()
        return {"message": "Record deleted successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete record")

@router.get("/first_layer/")
async def get_all_records(db=Depends(get_db2)):
    try:
        query = FirstLayer.__table__.select()
        result = await db.execute(query)
        records = result.fetchall()
        return [record._asdict() for record in records]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch records")

## Search functionality ##
@router.get("/first_layer_search")
async def search_first_layer(keyword: str, db=Depends(get_db2)) -> List[str]:
    try:
        query = text(
            "SELECT * FROM first_layer WHERE word LIKE :keyword OR meaning LIKE :keyword OR deepl_translation LIKE :keyword"
        ).params(keyword=f"%{keyword}%")
        result = await db.execute(query)
        records = result.fetchall()
        return [record.word for record in records]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to perform search")

## CORE LAYER STUFF - DB CRUD ##
@router.post("/core_layer/")
async def create_record(record: CoreLayerCreate, db=Depends(get_db2)):
    try:
        query = CoreLayer.__table__.insert().values(
            word=record.word,
            meaning=record.meaning,
            is_private=record.is_private,
            who_added=record.who_added,
            who_agreed=record.who_agreed,
            deepl_translation=record.deepl_translation,
            additional_translation=record.additional_translation
        )
        result = await db.execute(query)
        record_id = result.inserted_primary_key[0]
        await db.commit()
        return {"id": record_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create record")

@router.get("/core_layer/{record_id}")
async def get_record(record_id: int, db=Depends(get_db2)):
    try:
        query = CoreLayer.__table__.select().where(CoreLayer.id == record_id)
        result = await db.execute(query)
        record = result.fetchone()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return record._asdict()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch record")

@router.put("/core_layer/{record_id}")
async def update_record(record_id: int, updated_record: CoreLayerCreate, db=Depends(get_db2)):
    try:
        query = CoreLayer.__table__.update().where(CoreLayer.id == record_id).values(**updated_record.dict())
        await db.execute(query)
        await db.commit()
        return {"message": "Record updated successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update record")

@router.delete("/core_layer/{record_id}")
async def delete_record(record_id: int, db=Depends(get_db2)):
    try:
        query = CoreLayer.__table__.delete().where(CoreLayer.id == record_id)
        await db.execute(query)
        await db.commit()
        return {"message": "Record deleted successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete record")

@router.get("/core_layer/")
async def get_all_records(db=Depends(get_db2)):
    try:
        query = CoreLayer.__table__.select()
        result = await db.execute(query)
        records = result.fetchall()
        return [record._asdict() for record in records]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch records")

## Search functionality ##
@router.get("/core_layer_search")
async def search_core_layer(keyword: str, db=Depends(get_db2)) -> List[str]:
    try:
        query = text(
            "SELECT * FROM core_layer WHERE word LIKE :keyword OR meaning LIKE :keyword OR deepl_translation LIKE :keyword OR additional_translation LIKE :keyword"
        ).params(keyword=f"%{keyword}%")
        result = await db.execute(query)
        records = result.fetchall()
        return [record.word for record in records]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to perform search")

## DEEPL KEYS STUFF - CRUD DB ##
@router.post("/deepl_keys/")
async def create_deepl_key(key: str, db=Depends(get_db2)):
    try:
        query = DeeplKey.__table__.insert().values(key=key)
        result = await db.execute(query)
        key_id = result.inserted_primary_key[0]
        await db.commit()
        return {"id": key_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create deepl key")

@router.get("/deepl_keys/{key_id}")
async def read_deepl_key(key_id: int, db=Depends(get_db2)):
    try:
        query = DeeplKey.__table__.select().where(DeeplKey.id == key_id)
        result = await db.execute(query)
        db_key = result.fetchone()
        if db_key is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return db_key._asdict()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch deepl key")

@router.put("/deepl_keys/{key_id}")
async def update_deepl_key(key_id: int, key: str, accessible: bool, db=Depends(get_db2)):
    try:
        query = DeeplKey.__table__.update().where(DeeplKey.id == key_id).values(key=key, accessible=accessible)
        await db.execute(query)
        await db.commit()
        return {"message": "Deepl key updated successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update deepl key")

@router.delete("/deepl_keys/{key_id}")
async def delete_deepl_key(key_id: int, db=Depends(get_db2)):
    try:
        query = DeeplKey.__table__.delete().where(DeeplKey.id == key_id)
        await db.execute(query)
        await db.commit()
        return {"message": "Deepl key deleted successfully"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete deepl key")

@router.get("/deepl_keys/")
async def get_all_deepl_keys(db=Depends(get_db2)):
    try:
        query = DeeplKey.__table__.select()
        result = await db.execute(query)
        keys = result.fetchall()
        return [key._asdict() for key in keys]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch deepl keys")
