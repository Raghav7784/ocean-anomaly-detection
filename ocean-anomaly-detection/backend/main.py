from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import connect_db, close_db
from backend.routes import router
from backend.scheduler import start_scheduler

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
    start_scheduler()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Ocean Anomaly Detection API is running"}
