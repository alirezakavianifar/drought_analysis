# Research Plan: Drought Monitoring Using GRACE / GRACE-FO
### Thesis: *Evaluating the Strengths and Weaknesses of Drought Monitoring Based on Data from the GRACE and GRACE-FO Gravimetry Missions*

---

## 🔷 1. Core Objective

The thesis evaluates the capability of GRACE/GRACE-FO satellite gravimetry missions to monitor drought, and compares results against conventional meteorological approaches. Per the approved proposal, three hypotheses must be tested:

1. **H1** — GRACE-measured groundwater storage changes are directly related to drought intensity and extent.
2. **H2** — GRACE-based drought indices are effective tools for drought prediction.
3. **H3** — Integrating GRACE data with hydrological/climate data improves the accuracy and spatial resolution of drought monitoring models.

> ⚠️ **H3 is non-negotiable.** The proposal's methodology section explicitly requires collecting rainfall, temperature, runoff, and ET data from meteorological stations. A GRACE-only analysis cannot satisfy the approved proposal.

---

## 🔷 2. Dataset Reality Check (Based on Actual Files)

### ✅ 2.1 GRACEbasins.xlsx — Fully Usable

| Property | Value |
|---|---|
| Variable | TWSA (Total Water Storage Anomaly), cm |
| Time range | **Aug-2002 → Dec-2022** (245 monthly records) |
| Basins | `caspiansea`, `eastern`, `qaraqom`, `markazi`, `persiangolf`, `urmia` |
| Format | 1 header row + 245 data rows, 7 columns |

**Known preprocessing issue:** The `date` column has leading whitespace (e.g., `"   Aug-2002"`). Always apply `.str.strip()` before parsing.

---

### ⚠️ 2.2 synopticdatanew2.xlsx — Station Metadata Only

This file contains **no temporal data**. It is a spatial registry of 180 synoptic stations.

| Column | Content |
|---|---|
| `station_na` | English station name |
| `station_fn` | Persian station name |
| `Latitude` / `lat_decimal` | DMS and decimal lat |
| `Longitude` / `lon_decimal` | DMS and decimal lon |
| `elevation` | Station elevation (m) |
| `watershed_name` | Assigned watershed (links to GRACE basins) |

**Watershed-to-basin mapping:**

| `watershed_name` in synoptic file | GRACE column |
|---|---|
| `Caspian Sea` | `caspiansea` |
| `eastern` | `eastern` |
| `markazi` | `markazi` |
| `persiangolf` | `persiangolf` |
| `qaraqom` | `qaraqom` |
| `urmia` | `urmia` |
| `خارج از حوزه‌ها` | ❌ outside basins — **exclude from analysis** |

**This file's role:** Provides the station list and their basin assignments. Use it to know *which stations to download precipitation data for* — it does **not** supply that data itself.

---

### ❌ 2.3 Missing Data — REQUIRED to Acquire

You must download monthly precipitation and temperature data for the 180 stations from one or more of these sources (all listed in the proposal's own reference section):

| Source | Data | URL |
|---|---|---|
| **GPCC** | Monthly gridded precipitation | https://www.dwd.de/EN/ourservices/gpcc/gpcc.html |
| **CRU TS** | Monthly temp + precip rasters | https://crudata.uea.ac.uk/cru/data/hrg/ |
| **GHCN** | Station-level daily/monthly records | https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-monthly |

**Workflow after download:**
1. Extract values at each station's lat/lon coordinates.
2. Filter out stations with `watershed_name = خارج از حوزه‌ها`.
3. Average station values per basin → basin-level monthly precipitation time series.
4. Trim to GRACE time range: **Aug-2002 – Dec-2022**.

---

## 🔷 3. Phased Workflow

### ─── PHASE 1: GRACE-Only Analysis (Start Immediately) ───

#### Step 1 — Data Loading & Cleaning
```python
import pandas as pd

df = pd.read_excel('GRACEbasins.xlsx')
df['date'] = df['date'].str.strip()            # fix leading whitespace
df['date'] = pd.to_datetime(df['date'], format='%b-%Y')
df = df.set_index('date').sort_index()
```

#### Step 2 — GRACE Drought Index (GRACE-DSI)
Standardize TWSA per basin using z-score:
```
GRACE-DSI(t) = (TWSA(t) - mean(TWSA)) / std(TWSA)
```
- DSI < -1.0 → moderate drought
- DSI < -1.5 → severe drought
- DSI < -2.0 → extreme drought

#### Step 3 — GRACE Trend Analysis (per basin)
- Linear regression slope + p-value
- Mann-Kendall test for monotonic trend significance
- Output: trend magnitude (cm/year) per basin

#### Step 4 — Temporal Pattern Detection (per basin)
- 12-month moving average to remove seasonality
- Time-series decomposition (seasonal + trend + residual)
- Identify repeated drought episodes and their duration

#### Step 5 — Spatial / Basin Comparison
- Which basin shows fastest storage decline?
- Which has most severe drought events?
- Use the synoptic station registry to describe geographic coverage (province names, number of stations per basin)

#### Step 6 — Short-Term Forecasting (GRACE only)
- ARIMA on each basin's TWSA time series
- Linear extrapolation of trend
- Markov chain drought state transitions (cite proposal reference: *"پایش و پیش‌بینی خشکسالی ماهانه با استفاده از زنجیره مارکوف"*)
- Output: probability of drought in next 12–24 months per basin

---

### ─── PHASE 2: Climate Data Integration (After Acquiring Precipitation) ───

#### Step 7 — SPI Calculation (Standardized Precipitation Index)
- Compute SPI-3, SPI-6, SPI-12 per basin
- Use gamma distribution fitting on monthly basin-average precipitation

> *Note: SPEI requires evapotranspiration data (not yet available). Prioritise SPI first.*

#### Step 8 — GRACE vs. SPI Correlation
- Pearson correlation: GRACE-DSI vs SPI per basin
- **Lag correlation (0–6 months):** does GRACE respond after rainfall deficits? (common in hydrology; expected 1–3 month lag)
- Output: correlation matrix + lag plot

#### Step 9 — Precipitation Trend Analysis
- Linear regression + Mann-Kendall per basin
- Cross-compare with GRACE trend direction (both declining?)

#### Step 10 — Full Hypothesis Testing
- H1: correlation coefficients GRACE-DSI vs SPI (confirm statistical significance)
- H2: Validate ARIMA/Markov forecasts against held-out SPI data
- H3: Compare GRACE standalone vs GRACE+climate integrated basin drought assessment

---

## 🔷 4. Python Requirements

```python
# Core libraries
pandas          # time series handling
numpy           # calculations
scipy.stats     # Pearson correlation, Mann-Kendall
statsmodels     # ARIMA forecasting, OLS trend
matplotlib      # plots
seaborn         # heatmaps, lag plots
pymannkendall   # Mann-Kendall test (pip install pymannkendall)
```

**Script structure:**
| Script | Purpose |
|---|---|
| `01_grace_cleaning.py` | Load, strip dates, check missing values |
| `02_grace_dsi.py` | Compute GRACE-DSI per basin |
| `03_trend_analysis.py` | Linear + Mann-Kendall trends |
| `04_pattern_detection.py` | Decomposition, moving average, drought episodes |
| `05_forecasting.py` | ARIMA + Markov chain |
| `06_spi_calculation.py` | SPI-3/6/12 (Phase 2 — needs precip data) |
| `07_correlation_analysis.py` | GRACE-DSI vs SPI, lag correlation (Phase 2) |

---

## 🔷 5. Chapter 4 Structure

### 4.1 Data Description
- GRACE data: time range, basins, variable
- Station metadata: 180 stations, 6 watersheds, geographic distribution
- Acquired climate data: source, resolution, time range

### 4.2 Preprocessing
- Date parsing fix (leading whitespace in GRACE)
- Station filtering (exclude `خارج از حوزه‌ها`)
- Basin aggregation method for precipitation

### 4.3 GRACE Drought Index Results
- GRACE-DSI time series plots per basin
- Drought event table (date, duration, severity)

### 4.4 Trend Analysis
- TWSA trend per basin (slope, p-value, Mann-Kendall τ)
- Precipitation trend per basin (Phase 2)
- Joint trend interpretation

### 4.5 Drought Pattern Analysis
- Seasonal decomposition results
- Recurrence and frequency of droughts
- Markov chain state transition matrix

### 4.6 Spatial Comparison
- Basin-level ranking: drought severity, trend magnitude
- Map of station coverage (using synoptic metadata)

### 4.7 Correlation Analysis *(Phase 2)*
- GRACE-DSI vs SPI table
- Lag correlation plots
- Interpretation: GRACE as a delayed/integrated drought signal

### 4.8 Prediction Results
- ARIMA 24-month forecast per basin
- Drought risk probability (Markov chain)

### 4.9 Discussion — Strengths & Weaknesses of GRACE
*(Core of your thesis title)*

**Strengths:**
- Basin-wide coverage without ground stations
- Captures subsurface/groundwater component invisible to rainfall gauges
- Consistent 20-year record across all basins

**Weaknesses:**
- Coarse spatial resolution (~300 km) — cannot distinguish sub-basin variability
- Monthly temporal resolution — misses flash droughts
- 1–3 month lag vs. meteorological drought onset
- Accuracy depends on mass redistribution assumptions
- Data gap between GRACE (2002–2017) and GRACE-FO (2018–present)

---

## 🔷 6. Deliverables Checklist

- [ ] Cleaned GRACE time series (CSV)
- [ ] GRACE-DSI values per basin per month (CSV)
- [ ] Trend analysis table (slope, p-value, Mann-Kendall result per basin)
- [ ] Time series plots (all 6 basins overlaid)
- [ ] Drought episode classification plots
- [ ] ARIMA forecast plots (24 months)
- [ ] SPI time series (after data acquisition)
- [ ] Lag correlation plots (after data acquisition)
- [ ] Full Chapter 4 document (ready to paste into thesis, ~5,000–8,000 words)
- [ ] All Python scripts (well-commented, reproducible)
