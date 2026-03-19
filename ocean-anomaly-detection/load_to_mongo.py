import pandas as pd
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["ocean_anomaly"]

async def load_data():
    print("Loading scored data into MongoDB...")
    df = pd.read_csv("data/scored.csv")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    records = df.to_dict("records")
    for r in records:
        r["timestamp"] = r["timestamp"].to_pydatetime()

    await db["buoy_readings"].delete_many({})
    await db["buoy_readings"].insert_many(records)
    print(f"Inserted {len(records)} readings into buoy_readings")

    anomalies = [r for r in records if r.get("is_anomaly") == -1]
    await db["anomalies"].delete_many({})
    await db["anomalies"].insert_many(anomalies)
    print(f"Inserted {len(anomalies)} anomalies into anomalies collection")

    client.close()
    print("Done!")

asyncio.run(load_data())