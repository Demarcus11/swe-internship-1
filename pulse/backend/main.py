from fastapi import FastAPI, HTTPException
from enum import StrEnum
from pydantic import BaseModel
from datetime import datetime, timezone


app = FastAPI()

# Types
class Status(StrEnum):
    operational = "operational"
    degraded = "degraded"
    outage = "outage"
    maintenance = "maintenance"

class Service(BaseModel):
    id: int
    name: str
    description: str
    owner: str
    status: Status
    created_at: datetime
    updated_at: datetime

class ServiceClientCreate(BaseModel):
    name: str
    description: str
    owner: str
    status: Status

class ServiceClientUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    owner: str | None = None
    status: Status | None = None

# Data
services = [
    Service(
        id=1,
        name="Web Hosting",
        description="Static and dynamic site hosting",
        owner="platform-team",
        status=Status.operational,
        created_at=datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 1, 14, 30, tzinfo=timezone.utc),
    ),
]

# Endpoints
@app.get("/api/services")
async def get_services() -> list[Service]:
    return services

@app.get("/api/services/{service_id}")
async def get_service(service_id: int) -> Service:
    for s in services:
        if s.id == service_id:
            return s
    raise HTTPException(status_code=404, detail="Service not found")
       
@app.post("/api/services", status_code=201)
async def create_service(new_service: ServiceClientCreate) -> Service:
    now = datetime.now(timezone.utc)
    service = Service(
        id=max((s.id for s in services), default=0) + 1,
        **new_service.model_dump(),
        created_at=now,
        updated_at=now
    )
    services.append(service)
    return service

@app.patch("/api/services/{service_id}")
async def update_service(service_id: int, updated_service: ServiceClientUpdate) -> Service:
    # Copy exisiting Service instance and overwrite only fields the client updated
    for index, s in enumerate(services):
        if s.id == service_id:
            service = s.model_copy(
                update={
                    **updated_service.model_dump(exclude_unset=True),
                    "updated_at": datetime.now(timezone.utc)
                }
            )
            services[index] = service
            return service
    raise HTTPException(status_code=404, detail="Service not found")

@app.delete("/api/services/{service_id}", status_code=204)
async def delete_service(service_id: int):
    for index, s in enumerate(services):
        if s.id == service_id:
            services.pop(index)
            return
    raise HTTPException(status_code=404, detail="Service not found")
    
