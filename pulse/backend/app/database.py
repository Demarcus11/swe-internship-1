import os

from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session
from .models import tables  # registers table models with SQLModel.metadata

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create tables from tables inside models.tables.py
def create_db_and_tables(): 
    SQLModel.metadata.create_all(engine)

# Stores DB changes to be ready for when session.commit() is called to push changes to the DB    
def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)]


