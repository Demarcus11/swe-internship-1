# Engineering Notes

# 10/20/2026

- Project structure:
  - removed base.py since I only had the Status enum in there currently. Added Stats enum declaration inside schemas.py.
  - created backend/routes/services.py to put endpoints inside and removed them from backend/main.py.

- FastAPI APIRouter:
  - APIRouter allows for better organization of endpoint resources. Currently, we only have one resource, services, but if we had more resources such as users, services, etc then the benefits of APIRouter would be more visible, but we still get some benefits with one resource. First benefit is, we don't have to use the full endpoint path in our endpoints. The tag allows the /docs to group the endpoints into a section so all services endpoints will appear under the services section:

  ```python
  # services.py

  router = APIRouter(prefix="/api/services", tags=["services"])

  @router.get("/", response_model=list[ServicePublic])
  async def get_services():
      return services

  # main.py
  from fastapi import FastAPI
  from app.routes import services

  app = FastAPI()
  app.include_router(services.router)
  ```

- File paths in python:
  - Instead of making pulse/ the root, which would force us to type `from pulse.backend.app.main import app` we flag the app/ folder as our code package by putting an empty `__init__.py file` inside of it. Now, as long as our terminal is open in the backend/ folder, we can just type `from app.main import app`

  - Inside the models/ directory, we use another `__init__.py` to bundle our files and make importing easier. Rather than having to reach deep into sub-files and write `from app.models.schemas import ServiceBase`, we can simply pull it straight from the folder models directory `from app.models import ServiceBase`

- Database explained:
  - A database is a program that stores data in files on some computer's disk. The program (Postgres) sits and waits for requests such as "save this row", "give me all services" and reads and writes to files in response. Which computer Postgres is running on determines which computer's disk the files are stored on:
    - Locally: using Docker which runs Postgres on your computer so the DB files are stored on your computer's disk. Pros is, its free, cons is is your computer turns off then the DB turns off so any deployed apps using data from the database won't load, and if your disk breaks then all DB data is lost.

    - Cloud: using a cloud service such as Neon which runs Postgres on Neon's servers which stores the DB files on their computer's disks. Pros, DB data has 24/7 uptime because its determined by the cloud service servers not your computer being on so deployed apps will always have access to DB data, data is protected because cloud services usually store the data in more than one place so if a drive dies all Db data isnt lost, cons is it can cost money, but for small practice projects most cloud services have a free tier.

- Postgres setup & Sqlmodel intergration
  1. Install postgres driver and a .env loader from pulse/backend run: "uv add "psycopg[binary]" python-dotenv"
  2. Start a Postgres server: We are going the cloud way with Neon. Create new Neon project and get DATABASE_URL connection string. Change the beginning to "postgresql+psycopg://" so SQLAlchemy uses the installed driver.
  3. Add it to a .env file inside backend/
  4. Inside database.py paste:

  ```python
  import os

  from dotenv import load_dotenv
  from sqlmodel import create_engine

  load_dotenv() # makes .env variable available

  DATABASE_URL = os.environ["DATABASE_URL"]

  engine = create_engine(DATABASE_URL, pool_pre_ping=True)
  ```

- Updating endpoint functions with DB functions

  ```python
  @router.post("/", response_model=ServicePublic, status_code=201)
  async def create_service(new_service: ServiceCreate, session: SessionDep):
      service = Service(**new_service.model_dump())
      session.add(service)
      session.commit()
      session.refresh(service)
      return service
  ```

  1.  FastAPI validates the client's JSON body against the ServiceCreate schema.
  2.  `service = Service(**new_service.model_dump())` dumps the client's JSON body into a Service object. It will look like this:

           ```JSON
            Service(
              id=None, <-- set as default in Service table
              name="Web Hosting",
              description="Static and dynamic site hosting",
              owner="platform-team",
              status=<Status.operational: "operational">,
              created_at=datetime.datetime( <-- set as default in Service table
                  2026, 10, 20, 20, 54, 0,
                  tzinfo=datetime.timezone.utc
              ),
              updated_at=datetime.datetime( <-- set as default in Service table
                  2026, 10, 20, 20, 54, 0,
                  tzinfo=datetime.timezone.utc
              )
            ```

  3.  Stage changes to DB session

      ```python
      session.add(service)
      ```

  4.  Commit transaction (saves new record to DB)

      ```python
      session.commit()
      ```

  5.  Refresh the object (reloads the object from the database, allowing it to reflect DB-generated values such as the primary key when the object is returned to the client)

      ```python
      session.refresh(service)
      ```

  6.  The returned service object will be stripped to match ServicePublic (response_model=ServicePublic)

      ```python
      @router.post("/", response_model=ServicePublic, status_code=201)
      ```

- To start server, from inside pulse/backend: `uv run uvicorn app.main:app --reload`, this will also start up the DB because we have the line:

  ```python
  # Runs once when the server starts (checks if the DB already exists first)
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      create_db_and_tables()
      yield
  ```

- To test API CRUD operations: `http://127.0.0.1:8000/docs`

## 10/19/2026

- New project structure:
  - `models/__init__.py`: for making importing from files in the models directory for files outside the models directory.

    ```python
    # main.py
    from backend.models.base import Status # messy file path
    from backend.models import Status #  __init__.py allows this cleaner file path
    ```

  - models/base.py: holds shared parent classes.
  - models/schemas.py: holds DTOs.
  - models/tables.py: holds ORM tables.

- How do we represent entities? Pydantic models. In python, objects are created with classes. They inherit from the SQLModel class e.g.

  ```python
  class ServiceBase(SQLModel):
    name: str
  ```

- How does the server validate data being sent to the client? For example, I retrieve an object from the database to send to the client, how does the server ensure all properties are client-safe properties? DTOs. Data Transfer Objects are contracts with client-safe properties used to ensure the objects send to the client by the server matching the contract. e.g.

  ```python
  # DTO - holds client-safe properties only such as name, description, id, etc. Doesn't include dangerous properties such as is_admin or password_hash
  class ServicePublic(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime
  ```

  To use a DTO, we it into an endpoint function `response_model=DTO` param. FastAPI will strip any properties in the database returned object that aren't in the DTO then send it to the client to ensure only properties reach the client:

  ```python
  @app.get("/api/services/{service_id}", response_model=ServicePublic)
  ```

- How does the server validate incoming data from the client? For example, client makes a POST request and sends an object to the server, how does the server let the user know if there's any errors? DTOs. DTOs can also be used to validate data coming into the server. e.g.

  ```python
  async def create_service(new_service: ServiceCreate):
  ```

  When the client sends an object, it will be passed into the function as new_service. The type of new_service is ServiceCreate which is a DTO. If new_service doesn't match the type then the client will recieve an error telling them which properties are invalid.

- How do we map ORM objects to database tables? sqlmodel. Sqlmodel uses pydantic under the hood, so to create a table we create a pydantic object, but we pass in table=True as a param. A property in the table will need a primary key, usually the id (Primary keys have a rule that the property can't contain duplicates and can't be NULL which is perfect for something such as the id in a Services table because no two Services should have the same id and no Service should have NULL for an id.). e.g.

  ```python
  class Service(ServiceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  ```

## 10/15/2026

Database Setup

- uv add sqlmodel: sqlmodel is an ORM that intergrates well with FastAPI.

Project Restructure

- created models.py to better seperate concerns.
  - main.py holds app initialization and api endpoints
  - models.py holds sqlmodel tables and pydantic types/models

- to reduce code, we created a base pydantic model that other models can inherit properties from when needed. We created a ServiceBase which is used for other models to inherit properties from.

- we created a client-safe Service model 'ServicePublic' which is used to safely send Service objects to the client. For example, the client made a GET request for a Service. We search the DB and return the searched Service model and return it to the client. This is unsafe because we should never directly send Service objects from the DB because it could contain DB-only properties that shouldn't be sent to the client. To fix this, we create a ServicePublic model that will contain only client-safe properties and we can tell fastapi to strip the return Service DB object to match the shape of the client-safe ServicePublic object and send that object to the client. ServicePublic and Service will look almost identical in models.py but they serve different purposes because if the DB table properties update, we can just not add those properties to ServicePublic and the api stays safe. NEVER SEND RAW DB models directly to the client, ALWAYS map them to safe models e.g. Service (RAW DB model) -> ServicePublic then send ServicePublic to client. This is also commonly called DTOs (Data Transfer Objects). ServicePublic would be the DTO in this case.

- inside main.py, we changed '-> Service' to response_model=list[ServicePublic] because the type checker will flag the Service object returned by the endpoints because each endpoint either returns a list of Service DB objects or a Service DB object but the endpoints should be returning the client safe ServicePublic object instead. Using response_model=list[ServicePublic] will allow fastapi to strip the returned unsafe Service DB objects to match the ServicePublic shape making it client safe.

## 10/13/2026

Project Setup & Package Management

- "uv init --bare": Initialized a minimal Python project using 'uv', a Rust-backed package manager. The --bare flag creates only a pyproject.toml file, omitting sample code and boilerplate.

Data Validation & Flow (Pydantic Models)

- Inbound Validation (Client data coming into server): Enforces data contracts (models) on client payloads (e.g. endpoint param type: new_service: ServiceClientCreate). This catches validation errors. E.g. client sends { "random_property": "random" } while the model doesn't have that property. Client will get a validation error.

- Outbound Validation (Server data going to client): Formats data leaving the server (e.g. return type: -> Service). It handles data masking (stripping out sensitive internal database fields) and automated serialized. Serialization is the process of flattening live, complex memory structures (like datetime objects) into transportable plain text strings (like JSON payloads).

Dictionary Unpack Operator

Calling model_dump() extracts a model's data into a raw Python dictionary. The `**` operator acts as a formatting bridge to pour that dictionary into its next destination. In almost every case, you will need to use the `**` when using model_dump(). E.g. we need to dump the client's data into a Service object. Service object holds key=value pairs and model_dump() returns a dict so we have a format mismatch. We grab the client's data using model_dump() and format it into key=value pairs using `**`. It can also format into a dict inside another dict. E.g. We need to update an exisiting entry with properties the client sent (e.g. PATCH request). We use model_copy() to copy the exisiting entry and use model_dump(exclude_unset=True) inside model_copy(update=) to overwrite only the the properties the client sent and `**` to format it into the exisiting entry.

Data Mutation

- enumerate(): Used over basic for-in loops when traversing in-memory lists to gain access to the item's index, making it possible to safely target and replace entries inline.

## 10/08/2026

- Initialized the repository and established the Git branching/PR workflow.
- Learned how GitHub PR diffs are reviewed before merging.
