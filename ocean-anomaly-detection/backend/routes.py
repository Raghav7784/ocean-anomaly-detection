from fastapi import APIRouter
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
