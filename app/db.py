from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:Ruttur321$@localhost:3306/emcdb"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_db2():
    db = SessionLocal()
    return db
