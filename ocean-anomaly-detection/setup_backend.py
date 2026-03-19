files = {}

files['backend/database.py'] = """from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URL)
db = client["ocean_anomaly"]

buoy_collection = db["buoy_readings"]
anomaly_collection = db["anomalies"]

async def connect_db():
    print("Connected to MongoDB")

async def close_db():
    client.close()
    print("MongoDB connection closed")
"""

files['backend/models.py'] = """from pydantic import BaseModel
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
"""

files['backend/main.py'] = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import connect_db, close_db
from backend.routes import router

app = FastAPI(title="Ocean Anomaly Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Ocean Anomaly Detection API is running"}
"""

files['backend/routes.py'] = """from fastapi import APIRouter
from backend.database import buoy_collection, anomaly_collection

router = APIRouter()

@router.get("/buoys")
async def get_buoys():
    buoys = await buoy_collection.distinct("buoy_id")
    return {"buoys": buoys}

@router.get("/readings/{buoy_id}")
async def get_readings(buoy_id: str, limit: int = 100):
    cursor = buoy_collection.find(
        {"buoy_id": buoy_id}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    readings = await cursor.to_list(length=limit)
    return {"readings": readings}

@router.get("/anomalies")
async def get_anomalies(limit: int = 50):
    cursor = anomaly_collection.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    anomalies = await cursor.to_list(length=limit)
    return {"anomalies": anomalies}

@router.get("/stats")
async def get_stats():
    total = await buoy_collection.count_documents({})
    total_anomalies = await anomaly_collection.count_documents({})
    buoys = await buoy_collection.distinct("buoy_id")
    return {
        "total_readings": total,
        "total_anomalies": total_anomalies,
        "buoys_monitored": len(buoys)
    }
"""

files['backend/__init__.py'] = ""

for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {path}")

print("All files created!")