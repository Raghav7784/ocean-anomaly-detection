🌊 Ocean Anomaly Detection System
An end-to-end machine learning pipeline that ingests live NOAA ocean buoy data, engineers 27 sensor features, and uses Isolation Forest to detect anomalous ocean conditions — all visualised in a real-time interactive dashboard.
Built as a demonstration of applied ML for marine technology and subsea monitoring use cases.

📸 Dashboard Preview

Live dashboard running at localhost:8501 — showing 38,458 readings across 6 buoys with 1,923 anomalies flagged.

![Dashboard](dashboard.png)

🚀 What It Does

Pulls live data from 7 NOAA National Data Buoy Center stations across the Gulf of Mexico and Atlantic
Cleans and engineers 27 features — rolling means, standard deviations, z-scores, and rate-of-change per sensor
Trains an Isolation Forest model (200 estimators, 5% contamination) to flag statistically anomalous readings
Visualises results in a Streamlit dashboard with:

Interactive map of buoy locations coloured by anomaly rate
Per-buoy time-series explorer with anomaly markers
Live alert feed of the most anomalous recent readings




🛠 Tech Stack
LayerToolsData ingestionPython requests, NOAA NDBC REST APIData processingpandas, numpyFeature engineeringRolling stats, z-scores, lag/diff featuresML modelscikit-learn Isolation ForestDashboardstreamlit, plotly

📂 Project Structure
ocean-anomaly-detection/
├── data/                    # Raw and processed buoy data (CSV)
├── models/                  # Saved Isolation Forest model (.pkl)
├── data_fetch.py            # Downloads live NOAA buoy data
├── preprocess.py            # Cleans data and engineers features
├── model.py                 # Trains anomaly detection model
├── app.py                   # Streamlit dashboard
└── README.md

⚙️ Setup & Run
1. Clone the repo
bashgit clone https://github.com/YOUR_USERNAME/ocean-anomaly-detection.git
cd ocean-anomaly-detection
2. Create virtual environment
bashpython -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
3. Install dependencies
bashpip install pandas numpy scikit-learn torch streamlit plotly requests
4. Run the pipeline
bashpython data_fetch.py       # Fetch live buoy data
python preprocess.py       # Clean and engineer features
python model.py            # Train anomaly detector
streamlit run app.py       # Launch dashboard
Dashboard opens at http://localhost:8501

📡 Data Source
Live sensor readings from the NOAA National Data Buoy Center — 7 active buoys monitoring:

Water temperature (WTMP)
Air temperature (ATMP)
Atmospheric pressure (PRES)
Wind speed (WSPD)
Wave height (WVHT)


🤖 Model Details
Isolation Forest — an unsupervised anomaly detection algorithm that isolates observations by randomly partitioning data. Points that require fewer splits to isolate are flagged as anomalies.

200 estimators
5% contamination threshold (assumes ~5% of readings are anomalous)
Input: 25 engineered features per reading
Output: anomaly score + binary flag per reading


🌐 Real-World Application
This system mirrors what offshore operators use for:

Subsea pipeline integrity monitoring
Early warning of unusual oceanographic events (temperature spikes, pressure anomalies)
Equipment failure detection on offshore platforms
Environmental monitoring for marine protected areas
