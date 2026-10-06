from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class NodeIn(BaseModel):
    node_id: str
    latitude: float
    longitude: float
    status: str = "ONLINE"
    signal: int = Field(80, ge=0, le=100)
    battery: int = Field(100, ge=0, le=100)
    hops: int = Field(0, ge=0)

class EmergencyIn(BaseModel):
    message_id: str
    node_id: str
    hazard: str
    severity: str | None = None
    latitude: float
    longitude: float
    timestamp: datetime | None = None
    ttl: int = Field(5, ge=0, le=20)
    hops: int = Field(0, ge=0, le=20)
    smoke: int = 0
    sound: int = 0
    rain: int = 0
    flame: int = 0
    details: str = ""

class RouteRequest(BaseModel):
    latitude: float
    longitude: float
    shelter_id: Optional[int] = None

class AdminLogin(BaseModel):
    username: str
    password: str
