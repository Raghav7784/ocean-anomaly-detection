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
python data_fetch.py    # fetch live buoy data
python preprocess.py    # clean and engineer features
python model.py         # train anomaly detector
streamlit run app.py    # launch dashboard
\\n
## Project Structure
\\nocean-anomaly-detection/
├── data_fetch.py      # Downloads NOAA buoy data
├── preprocess.py      # Feature engineering
├── model.py           # Isolation Forest training
├── app.py             # Streamlit dashboard
└── data/              # Raw + processed CSVs
\\n
## Real-World Application
Mirrors subsea monitoring systems used for offshore pipeline integrity, early warning of oceanographic anomalies, and equipment failure detection on marine platforms.
