from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routes import services
from app.database import create_db_and_tables

def create_app(initialize_database: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if initialize_database:
            create_db_and_tables()
        yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(services.router)

    return app


app = create_app()
                            
