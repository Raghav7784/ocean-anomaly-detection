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

@router.get("/buoy_stats")
async def get_buoy_stats():
    buoys = await buoy_collection.distinct("buoy_id")
    result = []
    for b in buoys:
        total = await buoy_collection.count_documents({"buoy_id": b})
        anomalies = await anomaly_collection.count_documents({"buoy_id": b})
        pct = round((anomalies / total * 100), 1) if total > 0 else 0
        result.append({"buoy_id": b, "total": total, "anomalies": anomalies, "anomaly_pct": pct})
    return {"buoy_stats": result}

@router.get("/heatmap")
async def get_heatmap():
    result = []
    for hour in range(0, 24, 2):
        count = await anomaly_collection.count_documents({
            "$expr": {"$eq": [{"$hour": "$timestamp"}, hour]}
        })
        result.append({"hour": hour, "count": count})
    return {"heatmap": result}

@router.get("/test_alert")
async def test_alert():
    from backend.alerts import send_anomaly_alert
    from datetime import datetime
    result = send_anomaly_alert(
        buoy_id="42001",
        timestamp=datetime.now(),
        anomaly_score=-0.1523,
        sensor_data={"WTMP": 28.5, "ATMP": 26.1, "PRES": 1008.3, "WSPD": 15.2}
    )
    return {"email_sent": result}