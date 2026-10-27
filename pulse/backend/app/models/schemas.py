from sqlmodel import SQLModel
from datetime import datetime
from enum import StrEnum

class Status(StrEnum):
    operational = "operational"
    degraded = "degraded"
    outage = "outage"
    maintenance = "maintenance"

# Properties shared across Service variants
class ServiceBase(SQLModel):
    name: str
    description: str
    owner: str
    status: Status = Status.operational
    
# For Service DB objects sent to client by the server (inherits all properties from ServiceBase)
class ServicePublic(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
# For Service objects created by the client and sent to the server
class ServiceCreate(ServiceBase):
    pass
    
# For Service objects updated by the client and sent to the server
class ServiceUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    owner: str | None = None
    status: Status | None = None
    