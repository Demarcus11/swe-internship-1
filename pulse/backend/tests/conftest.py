
import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

from app.database import get_session
from app.main import create_app
from app.models import tables  


TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

def override_get_session():
    # FastAPI uses this dependency for requests made by the test client.
    with Session(test_engine) as session:
        yield session


app = create_app(initialize_database=False)
app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    # Create missing tables in pulse_test before running tests.
    SQLModel.metadata.create_all(test_engine)
    yield

@pytest.fixture
def db_session():
    # Provide a session for test DB
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client():
    # Manage the HTTP client's startup and shutdown lifecycle.
    with TestClient(app) as test_client:
        yield test_client
