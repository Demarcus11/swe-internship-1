from fastapi import FastAPI
from app.routes import services
from contextlib import asynccontextmanager
from app.database import create_db_and_tables

# Runs once when the server starts (checks if the DB already exists first)
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()  
    yield        

app = FastAPI(lifespan=lifespan)
app.include_router(services.router)
           
                            
