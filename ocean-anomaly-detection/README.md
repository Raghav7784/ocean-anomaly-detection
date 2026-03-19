# Ocean Anomaly Detection System

An end-to-end ML pipeline that ingests **live NOAA ocean buoy data**, engineers 27 sensor features, and uses **Isolation Forest** to detect anomalous ocean conditions in real time.

## Live Results
- 38,458 sensor readings across 7 buoys
- 1,923 anomalies flagged (5%)
- Interactive dashboard with buoy map, time-series explorer and alert feed

## Tech Stack
| Layer | Tools |
|---|---|
| Data ingestion | Python requests, NOAA NDBC API |
| Processing | Pandas, NumPy |
| ML Model | Scikit-learn Isolation Forest |
| Dashboard | Streamlit, Plotly |

## Run It
\\ash
python data_fetch.py
python preprocess.py
python model.py
streamlit run app.py
\
## Real-World Application
Mirrors subsea monitoring systems used for offshore pipeline integrity, early warning of oceanographic anomalies, and equipment failure detection on marine platforms.
