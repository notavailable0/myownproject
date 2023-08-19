from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, selectinload
from dogpile.cache import make_region

DATABASE_URL = "mysql+aiomysql://root:Ruttur321$@localhost:3306/emcdb"

# Create the asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Create a dictionary-based cache region
cache_region = make_region().configure("dogpile.cache.memory")

# Create the sessionmaker using the AsyncSession class
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Bind the engine to the Base class
Base = declarative_base()
Base.metadata.bind = engine

async def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        await db.close()

async def get_db2():
    db = SessionLocal()
    return db