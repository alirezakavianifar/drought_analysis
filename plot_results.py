"""
Plotting script for finalized Phase 2 results.
Generates SPI comparison, Precip-Trend comparison, and Correlation Heatmaps.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

OUTPUT_DIR = Path('outputs')
BASINS = ['caspiansea', 'eastern', 'qaraqom', 'markazi', 'persiangolf', 'urmia']
BASIN_LABELS = {'caspiansea': 'Caspian Sea', 'eastern': 'Eastern', 'qaraqom': 'Qaraqom', 
                'markazi': 'Markazi', 'persiangolf': 'Persian Gulf', 'urmia': 'Urmia'}
BASIN_COLORS = {'caspiansea':'#1f77b4','eastern':'#ff7f0e','qaraqom':'#2ca02c',
                'markazi':'#d62728','persiangolf':'#9467bd','urmia':'#8c564b'}

# Load data
dsi = pd.read_csv(OUTPUT_DIR / 'grace_dsi.csv', index_col=0, parse_dates=True)
spi = pd.read_csv(OUTPUT_DIR / 'spi_12.csv', index_col=0, parse_dates=True)
precip = pd.read_csv(OUTPUT_DIR / 'basin_precipitation.csv', index_col=0, parse_dates=True)

# 1. SPI vs GRACE-DSI Comparison Plot
fig, axes = plt.subplots(3, 2, figsize=(16, 12), sharex=True)
axes = axes.flatten()
for idx, b in enumerate(BASINS):
    ax = axes[idx]
    ax2 = ax.twinx()
    ax.plot(dsi.index, dsi[b], color=BASIN_COLORS[b], linewidth=1.5, label='GRACE-DSI')
    ax2.plot(spi.index, spi[b], color='black', alpha=0.4, label='SPI-12')
    ax.axhline(0, color='gray', alpha=0.3)
    ax.set_title(BASIN_LABELS[b])
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'spi12_vs_grace_dsi.png', dpi=300)

# 2. Correlation Heatmap
corr_matrix = pd.DataFrame(index=BASINS, columns=['SPI-3', 'SPI-6', 'SPI-12'])
for b in BASINS:
    for ts in [3, 6, 12]:
        s = pd.read_csv(OUTPUT_DIR / f'spi_{ts}.csv', index_col=0, parse_dates=True)
        common = dsi.index.intersection(s.index)
        corr_matrix.loc[b, f'SPI-{ts}'] = dsi[b][common].corr(s[b][common])

plt.figure(figsize=(10, 6))
sns.heatmap(corr_matrix.astype(float), annot=True, cmap='RdYlGn', center=0)
plt.title('Correlation: GRACE-DSI vs SPI at Different Timescales')
plt.savefig(OUTPUT_DIR / 'correlation_heatmap.png', dpi=300)

print("Plots regenerated with REAL data.")
