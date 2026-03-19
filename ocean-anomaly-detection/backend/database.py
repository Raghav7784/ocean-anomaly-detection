from motor.motor_asyncio import AsyncIOMotorClient
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
