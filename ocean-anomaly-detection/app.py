import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Ocean Anomaly Detection", layout="wide")
st.title("🌊 Ocean Anomaly Detection Dashboard")
st.caption("Live NOAA buoy data — powered by Isolation Forest")

@st.cache_data
def load_data():
    return pd.read_csv("data/scored.csv", parse_dates=["timestamp"])

df = load_data()
anomalies = df[df["is_anomaly"] == -1]

# ── Top metrics ──────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Readings", f"{len(df):,}")
col2.metric("Anomalies Flagged", f"{len(anomalies):,}")
col3.metric("Buoys Monitored", df["buoy_id"].nunique())

st.divider()

# ── Buoy map ─────────────────────────────────────────────
BUOY_COORDS = {
    "42001": (25.9, -89.7), "42002": (26.0, -93.6),
    "42003": (26.0, -86.0), "42036": (28.5, -84.5),
    "42055": (22.0, -94.0), "41047": (27.5, -71.5),
    "41048": (31.8, -69.6), "41049": (27.5, -62.9),
    "44025": (40.3, -73.2), "44013": (42.3, -70.7),
}

buoy_summary = df.groupby("buoy_id").agg(
    anomaly_count=("is_anomaly", lambda x: (x == -1).sum()),
    total=("is_anomaly", "count")
).reset_index()
buoy_summary["anomaly_pct"] = (100 * buoy_summary["anomaly_count"] / buoy_summary["total"]).round(1)
buoy_summary["lat"] = buoy_summary["buoy_id"].map(lambda b: BUOY_COORDS.get(b, (0,0))[0])
buoy_summary["lon"] = buoy_summary["buoy_id"].map(lambda b: BUOY_COORDS.get(b, (0,0))[1])

st.subheader("Buoy locations — anomaly rate")
fig_map = px.scatter_mapbox(
    buoy_summary, lat="lat", lon="lon",
    color="anomaly_pct", size="anomaly_count",
    hover_name="buoy_id",
    hover_data={"anomaly_pct": True, "anomaly_count": True},
    color_continuous_scale="RdYlGn_r",
    mapbox_style="open-street-map", zoom=3,
    height=420
)
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ── Per-buoy time series ──────────────────────────────────
st.subheader("Time-series explorer")
selected_buoy = st.selectbox("Select buoy", sorted(df["buoy_id"].unique()))
sensor = st.selectbox("Sensor", ["WTMP", "ATMP", "PRES", "WSPD"])

buoy_df = df[df["buoy_id"] == selected_buoy].sort_values("timestamp")
normal_df = buoy_df[buoy_df["is_anomaly"] == 1]
anom_df   = buoy_df[buoy_df["is_anomaly"] == -1]

if sensor in buoy_df.columns:
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=normal_df["timestamp"], y=normal_df[sensor],
        mode="lines", name="Normal",
        line=dict(color="#3B8BD4", width=1)
    ))
    fig_ts.add_trace(go.Scatter(
        x=anom_df["timestamp"], y=anom_df[sensor],
        mode="markers", name="Anomaly",
        marker=dict(color="#E24B4A", size=7, symbol="x")
    ))
    fig_ts.update_layout(
        height=350, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_ts, use_container_width=True)

st.divider()

# ── Alert feed ───────────────────────────────────────────
st.subheader("Recent anomaly alerts")
alert_cols = ["timestamp", "buoy_id", "anomaly_score"]
sensor_present = [s for s in ["WTMP", "ATMP", "PRES", "WSPD"] if s in anomalies.columns]
display_cols = alert_cols + sensor_present

recent = (anomalies[display_cols]
          .sort_values("anomaly_score")
          .head(15)
          .reset_index(drop=True))
recent["anomaly_score"] = recent["anomaly_score"].round(4)
st.dataframe(recent, use_container_width=True) 
