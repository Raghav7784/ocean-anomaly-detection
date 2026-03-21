import asyncio
import pandas as pd
import numpy as np
import pickle
import requests
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.database import buoy_collection, anomaly_collection

BUOY_IDS = ["42001", "42002", "42036", "42055", "41049", "44025", "44013"]
SENSOR_COLS = ["WTMP", "ATMP", "PRES", "WSPD", "WVHT"]

def fetch_buoy(buoy_id):
    url = f"https://www.ndbc.noaa.gov/data/realtime2/{buoy_id}.txt"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = r.text.strip().split("\n")
        cols = lines[0].lstrip("#").split()
        rows = [l.split() for l in lines[2:] if not l.startswith("#")]
        df = pd.DataFrame(rows, columns=cols)
        df["buoy_id"] = buoy_id
        return df
    except Exception as e:
        print(f"Could not fetch buoy {buoy_id}: {e}")
        return None

def preprocess(df):
    if "YY" in df.columns:
        df.rename(columns={"YY": "#YY"}, inplace=True)
    try:
        df["timestamp"] = pd.to_datetime(
            df["#YY"] + "-" + df["MM"] + "-" + df["DD"] + " " + df["hh"] + ":" + df["mm"],
            format="%Y-%m-%d %H:%M", errors="coerce"
        )
    except:
        return None
    for col in SENSOR_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].replace([99.0, 999.0, 9999.0], np.nan)
    return df

def engineer_features(df):
    df = df.set_index("timestamp").sort_index()
    for col in SENSOR_COLS:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = df[col].interpolate(method="time", limit=6)
        df[f"{col}_roll_mean"] = df[col].rolling(24, min_periods=1).mean()
        df[f"{col}_roll_std"] = df[col].rolling(24, min_periods=1).std().fillna(0)
        mean = df[col].mean()
        std = df[col].std()
        df[f"{col}_zscore"] = (df[col] - mean) / (std + 1e-6)
        df[f"{col}_diff"] = df[col].diff().fillna(0)
    return df.reset_index()

async def fetch_and_store():
    print(f"[{datetime.now()}] Fetching fresh buoy data...")
    try:
        with open("models/isolation_forest.pkl", "rb") as f:
            saved = pickle.load(f)
        model = saved["model"]
        scaler = saved["scaler"]
        feature_cols = saved["features"]
    except Exception as e:
        print(f"Could not load model: {e}")
        return

    for bid in BUOY_IDS:
        df = fetch_buoy(bid)
        if df is None:
            continue
        df = preprocess(df)
        if df is None or df.empty:
            continue
        df = df.dropna(subset=["timestamp"])
        df = engineer_features(df)
        df = df.fillna(0)

        available = [c for c in feature_cols if c in df.columns]
        if len(available) < 20:
            print(f"Not enough features for buoy {bid}, skipping")
            continue

        X = df[available].values
        try:
            X_scaled = scaler.transform(X)
            df["anomaly_score"] = model.decision_function(X_scaled)
            df["is_anomaly"] = model.predict(X_scaled)
        except Exception as e:
            print(f"Model error for buoy {bid}: {e}")
            continue

        records = []
        for _, row in df.iterrows():
            rec = {
                "buoy_id": bid,
                "timestamp": row["timestamp"].to_pydatetime() if pd.notna(row["timestamp"]) else None,
                "anomaly_score": float(row["anomaly_score"]) if "anomaly_score" in row else None,
                "is_anomaly": int(row["is_anomaly"]) if "is_anomaly" in row else None,
            }
            for col in SENSOR_COLS:
                if col in row and pd.notna(row[col]):
                    rec[col] = float(row[col])
            if rec["timestamp"]:
                records.append(rec)

        if records:
            for rec in records:
                await buoy_collection.update_one(
                    {"buoy_id": rec["buoy_id"], "timestamp": rec["timestamp"]},
                    {"$set": rec},
                    upsert=True
                )
            anomalies = [r for r in records if r.get("is_anomaly") == -1]
            for rec in anomalies:
                if anomalies:
                  from backend.alerts import send_anomaly_alert
                  worst = min(anomalies, key=lambda x: x.get("anomaly_score", 0))
                  send_anomaly_alert(
                    buoy_id=worst["buoy_id"],
                    timestamp=worst["timestamp"],
                    anomaly_score=worst.get("anomaly_score", 0),
                    sensor_data={
                        "WTMP": worst.get("WTMP"),
                        "ATMP": worst.get("ATMP"),
                        "PRES": worst.get("PRES"),
                        "WSPD": worst.get("WSPD")
                    }
                )
                await anomaly_collection.update_one(
                    {"buoy_id": rec["buoy_id"], "timestamp": rec["timestamp"]},
                    {"$set": rec},
                    upsert=True
                )
            print(f"  Buoy {bid}: {len(records)} records, {len(anomalies)} anomalies stored")

    print(f"[{datetime.now()}] Fetch complete!")

scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.add_job(fetch_and_store, "interval", hours=1, id="fetch_buoy_data")
    scheduler.start()
    print("Scheduler started — fetching every hour")