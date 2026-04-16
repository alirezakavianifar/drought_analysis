"""
Memory-efficient Phase 2 Execution Script.
Processes 245 months.
Deletes each temporary TIF immediately after sampling.
"""
import pandas as pd
import numpy as np
import rasterio
import gzip
import shutil
import os
from pathlib import Path
from scipy.stats import gamma, norm

DATA_DIR = Path('data/chirps')
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Setup Stations
stations_all = pd.read_excel('synopticdatanew2.xlsx', engine='openpyxl')
stations = stations_all[stations_all['watershed_name'] != 'خارج از حوزه‌ها'].copy()
MAP = {'Caspian Sea':'caspiansea','eastern':'eastern','markazi':'markazi',
       'persiangolf':'persiangolf','qaraqom':'qaraqom','urmia':'urmia'}
stations['basin'] = stations['watershed_name'].map(MAP)

# 2. Extract Data
grace = pd.read_csv(OUTPUT_DIR / 'grace_cleaned.csv', index_col=0, parse_dates=True)
dates = grace.index
precip_basin_data = {b: [] for b in MAP.values()}

print(f"Sampling {len(dates)} months...")

for d in dates:
    fname = f'chirps-v2.0.{d.year}.{d.month:02d}.tif.gz'
    gz_path = DATA_DIR / fname
    
    # Check if gz exists (if not, append NaNs)
    if not gz_path.exists():
        for b in MAP.values(): precip_basin_data[b].append(np.nan)
        continue
        
    temp_tif = DATA_DIR / f"temp_{d.year}_{d.month}.tif"
    
    try:
        # Stream decompress
        with gzip.open(gz_path, 'rb') as f_in, open(temp_tif, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            
        with rasterio.open(temp_tif) as src:
            vals = [float(v[0]) for v in src.sample(zip(stations['lon_decima'], stations['lat_decima']))]
            df_tmp = pd.DataFrame({'basin': stations['basin'], 'p': vals})
            df_tmp['p'] = df_tmp['p'].where(df_tmp['p'] >= 0, np.nan)
            means = df_tmp.groupby('basin')['p'].mean()
            for b in MAP.values():
                precip_basin_data[b].append(means.get(b, np.nan))
    except Exception as e:
        print(f"Error processing {d}: {e}")
        for b in MAP.values(): precip_basin_data[b].append(np.nan)
    finally:
        if temp_tif.exists():
            os.remove(temp_tif)

precip_df = pd.DataFrame(precip_basin_data, index=dates)
precip_df.to_csv(OUTPUT_DIR / 'basin_precipitation.csv')

# 3. Compute SPI
def compute_spi(series, timescale=12):
    acc = series.rolling(timescale).sum().dropna()
    if len(acc) < 30: return pd.Series(np.nan, index=series.index)
    pos = acc[acc > 0]
    if len(pos) < 30: return pd.Series(np.nan, index=series.index)
    params = gamma.fit(pos, floc=0)
    cdf = gamma.cdf(acc, *params)
    # Correct for zeros (very few in monthly sum but good practice)
    p_zero = (acc == 0).sum() / len(acc)
    cdf = p_zero + (1-p_zero) * cdf
    spi_vals = norm.ppf(np.clip(cdf, 0.001, 0.999))
    return pd.Series(spi_vals, index=acc.index).reindex(series.index)

for ts in [3, 6, 12]:
    spi_df = pd.DataFrame({b: compute_spi(precip_df[b], ts) for b in MAP.values()})
    spi_df.to_csv(OUTPUT_DIR / f'spi_{ts}.csv')

print("Phase 2 Analysis Complete (Space-Efficient).")
