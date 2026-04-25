# Bird Species Observation Analysis

Analysis of bird species observed across Forest and Grassland ecosystems using data collected from 11 national parks in the USA (2018).

---

## Dataset

Two Excel files with 11 sheets each (one per park):
- Bird_Monitoring_Data_FOREST.XLSX
- Bird_Monitoring_Data_GRASSLAND.XLSX

Combined total: 17,077 records, 126 unique species

---

## Tools

- Python, Pandas - data cleaning and analysis
- Streamlit - web dashboard
- Plotly - charts
- SQLite - SQL explorer
- Jupyter Notebook - EDA

---

## How to Run

```bash
pip install streamlit plotly pandas openpyxl sqlalchemy
streamlit run app.py
```

---

## Files

```
app.py                               - Streamlit dashboard
Forestbirds.csv                      - Cleaned forest data
grasslandbirds.csv                   - Cleaned grassland data
Bird_Monitoring_Data_FOREST.XLSX     - Raw forest data
Bird_Monitoring_Data_GRASSLAND.XLSX  - Raw grassland data
forest_analysis.ipynb                - Forest EDA
grassland_analysis.ipynb             - Grassland EDA
```

---

## Dashboard Tabs

- Overview - species count and habitat comparison
- Temporal - monthly and daily observation trends
- Spatial - admin unit and plot level analysis
- Species - top species, ID method, sex ratio
- Environment - temperature, humidity, sky, wind
- Distance and Behaviour - how far birds were spotted, flyovers
- Observers - which observer recorded what
- Conservation - at-risk species from PIF watchlist
- SQL - write custom queries on the dataset
