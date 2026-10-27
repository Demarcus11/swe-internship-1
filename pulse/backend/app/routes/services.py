from fastapi import APIRouter, HTTPException, Query
from app.models import Service, ServicePublic, ServiceCreate, ServiceUpdate
from datetime import datetime, timezone
from app.database import SessionDep
from typing import Annotated
from sqlmodel import select

router = APIRouter(prefix="/api/services", tags=["services"])

# Endpoints
@router.get("/", response_model=list[ServicePublic])
async def get_services(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    services = session.exec(select(Service).offset(offset).limit(limit)).all()
    return services

@router.get("/{service_id}", response_model=ServicePublic)
async def get_service(service_id: int, session: SessionDep):
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
    
       
@router.post("/", response_model=ServicePublic, status_code=201)
async def create_service(new_service: ServiceCreate, session: SessionDep):
    service = Service(**new_service.model_dump())
    session.add(service)
    session.commit()
    session.refresh(service)
    return service

@router.patch("/{service_id}", response_model=ServicePublic)
async def update_service(service_id: int, updated_service: ServiceUpdate, session: SessionDep):
    service = session.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    # Extract only properties provided by the client
    service_data = updated_service.model_dump(exclude_unset=True)
    if not service_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    # Update exisiting service with supplied fields
    service.sqlmodel_update(service_data)
    service.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(service)
    return service


@router.delete("/{service_id}", status_code=204)
async def delete_service(service_id: int, session: SessionDep):
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    session.delete(service)
    session.commit()
    return
    
