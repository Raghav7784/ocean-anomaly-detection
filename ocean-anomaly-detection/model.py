import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle

FEATURE_COLS = [c for c in [] if True]  # populated dynamically below

def get_feature_cols(df):
    exclude = {"timestamp", "buoy_id"}
    return [c for c in df.columns if c not in exclude]

def train(path="data/features.csv"):
    df = pd.read_csv(path)
    feature_cols = get_feature_cols(df)

    print(f"Training on {len(feature_cols)} features, {len(df)} samples...")

    X = df[feature_cols].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,   # assume ~5% of readings are anomalous
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_scaled)

    # Score: more negative = more anomalous
    df["anomaly_score"] = model.decision_function(X_scaled)
    df["is_anomaly"] = model.predict(X_scaled)  # -1 = anomaly, 1 = normal

    df.to_csv("data/scored.csv", index=False)

    # Save model and scaler
    with open("models/isolation_forest.pkl", "wb") as f:
        pickle.dump({"model": model, "scaler": scaler, "features": feature_cols}, f)

    n_anomalies = (df["is_anomaly"] == -1).sum()
    print(f"Done. {n_anomalies} anomalies flagged ({100*n_anomalies/len(df):.1f}%)")
    print("Saved scored data → data/scored.csv")
    print("Saved model       → models/isolation_forest.pkl")

if __name__ == "__main__":
    train() 
