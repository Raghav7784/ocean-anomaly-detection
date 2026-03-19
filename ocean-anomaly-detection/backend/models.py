from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BuoyReading(BaseModel):
    buoy_id: str
    timestamp: datetime
    WTMP: Optional[float] = None
    ATMP: Optional[float] = None
    PRES: Optional[float] = None
    WSPD: Optional[float] = None
    WVHT: Optional[float] = None
    anomaly_score: Optional[float] = None
    is_anomaly: Optional[int] = None

class AnomalyAlert(BaseModel):
    buoy_id: str
    timestamp: datetime
    sensor: str
    value: float
    anomaly_score: float
    message: str
