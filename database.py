from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = "sqlite:///./dbfile.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread":False})

#postgresql
#DB_URL = "postgresql://dbuser:password@localhost/dbname"
#mysql
#DB_URL = "mysql://dbuser:password@localhost/dbname"
#engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db():
    return Base.metadata.create_all(bind=engine)





