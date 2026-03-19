import pandas as pd
import numpy as np

SENSOR_COLS = ["WTMP", "ATMP", "PRES", "WSPD", "WVHT"]

def load_and_clean(path="data/all_buoys_raw.csv"):
    df = pd.read_csv(path, dtype=str)

    # Build datetime from year/month/day/hour/minute columns
    time_cols = ["#YY", "MM", "DD", "hh", "mm"]
    # Handle alternate header format
    df.columns = df.columns.str.strip()
    if "YY" in df.columns:
        df.rename(columns={"YY": "#YY"}, inplace=True)

    df["timestamp"] = pd.to_datetime(
        df["#YY"] + "-" + df["MM"] + "-" + df["DD"] + " " + df["hh"] + ":" + df["mm"],
        format="%Y-%m-%d %H:%M", errors="coerce"
    )
    df = df.dropna(subset=["timestamp"])

    # Convert sensor columns, replace sentinel values with NaN
    for col in SENSOR_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].replace([99.0, 999.0, 9999.0, 99.00], np.nan)

    df = df[["timestamp", "buoy_id"] + [c for c in SENSOR_COLS if c in df.columns]]
    df = df.sort_values(["buoy_id", "timestamp"]).reset_index(drop=True)
    return df

def engineer_features(df):
    frames = []
    for buoy, group in df.groupby("buoy_id"):
        group = group.set_index("timestamp").sort_index()

        for col in SENSOR_COLS:
            if col not in group.columns:
                continue
            group[col] = group[col].interpolate(method="time", limit=6)
            # Rolling stats (24-observation window)
            group[f"{col}_roll_mean"] = group[col].rolling(24, min_periods=6).mean()
            group[f"{col}_roll_std"]  = group[col].rolling(24, min_periods=6).std()
            # Z-score vs station baseline
            mean = group[col].mean()
            std  = group[col].std()
            group[f"{col}_zscore"] = (group[col] - mean) / (std + 1e-6)
            # Rate of change
            group[f"{col}_diff"] = group[col].diff()

        group["buoy_id"] = buoy
        group = group.dropna()
        frames.append(group.reset_index())

    result = pd.concat(frames, ignore_index=True)
    result.to_csv("data/features.csv", index=False)
    print(f"Feature engineering done. Shape: {result.shape}")
    print(f"Columns: {list(result.columns)}")
    return result

if __name__ == "__main__":
    df = load_and_clean()
    print(f"Loaded {len(df)} rows across {df['buoy_id'].nunique()} buoys")
    engineer_features(df)
