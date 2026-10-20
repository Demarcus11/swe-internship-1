from enum import StrEnum

class Status(StrEnum):
    operational = "operational"
    degraded = "degraded"
    outage = "outage"
    maintenance = "maintenance"