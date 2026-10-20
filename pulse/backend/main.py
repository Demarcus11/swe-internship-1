from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from backend.models import Service, ServicePublic, ServiceCreate, ServiceUpdate, Status

app = FastAPI()

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
@app.get("/api/services", response_model=list[ServicePublic])
async def get_services():
    return services

@app.get("/api/services/{service_id}", response_model=ServicePublic)
async def get_service(service_id: int):
    for s in services:
        if s.id == service_id:
            return s
    raise HTTPException(status_code=404, detail="Service not found")
       
@app.post("/api/services", response_model=ServicePublic, status_code=201)
async def create_service(new_service: ServiceCreate):
    now = datetime.now(timezone.utc)
    service = Service(
        id=max((s.id for s in services if s.id is not None), default=0) + 1,
        **new_service.model_dump(),
        created_at=now,
        updated_at=now
    )
    services.append(service)
    return service

@app.patch("/api/services/{service_id}", response_model=ServicePublic)
async def update_service(service_id: int, updated_service: ServiceUpdate):
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
    
