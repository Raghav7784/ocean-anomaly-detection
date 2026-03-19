import requests
import pandas as pd
import os

# 10 active NOAA buoys across Gulf of Mexico & Atlantic
BUOY_IDS = ["42001", "42002", "42003", "42036", "42055",
            "41047", "41048", "41049", "44025", "44013"]

def fetch_buoy(buoy_id):
    url = f"https://www.ndbc.noaa.gov/data/realtime2/{buoy_id}.txt"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        lines = r.text.strip().split("\n")

        # First line = column names, second = units (skip), rest = data
        cols = lines[0].lstrip("#").split()
        rows = [l.split() for l in lines[2:] if not l.startswith("#")]

        df = pd.DataFrame(rows, columns=cols)
        df["buoy_id"] = buoy_id
        return df
    except Exception as e:
        print(f"  Could not fetch buoy {buoy_id}: {e}")
        return None

def fetch_all():
    os.makedirs("data", exist_ok=True)
    all_frames = []

    for bid in BUOY_IDS:
        print(f"Fetching buoy {bid}...")
        df = fetch_buoy(bid)
        if df is not None:
            all_frames.append(df)
            df.to_csv(f"data/buoy_{bid}.csv", index=False)
            print(f"  Saved {len(df)} rows")

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined.to_csv("data/all_buoys_raw.csv", index=False)
        print(f"\nDone. Combined dataset: {len(combined)} rows saved to data/all_buoys_raw.csv")
    else:
        print("No data fetched. Check your internet connection.")

if __name__ == "__main__":
    fetch_all()