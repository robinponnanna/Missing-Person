from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class LocationSignal(BaseModel):
    signal_id: str
    person_id: str
    source: Literal["mobile", "cctv", "transaction", "wifi"]
    latitude: float
    longitude: float
    timestamp: datetime
    confidence: float
    metadata: Optional[dict] = None


class LocationEstimate(BaseModel):
    person_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    confidence: float
    radius_m: float
    sources_used: list[str]


class Person(BaseModel):
    person_id: str
    name: str
    last_known_lat: float
    last_known_lon: float
    last_seen: datetime
    status: Literal["missing", "found", "searching"] = "missing"


class TrackingUpdate(BaseModel):
    person_id: str
    estimates: list[LocationEstimate]
    predicted_location: Optional[LocationEstimate] = None
    overall_confidence: float