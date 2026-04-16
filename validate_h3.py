"""
Phase 2 (Supplement): Quantitative Validation for Hypothesis H3.
Compares GRACE-DSI and SPI-12 categorical agreement.
"""
import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = Path('outputs')
BASINS = ['caspiansea', 'eastern', 'qaraqom', 'markazi', 'persiangolf', 'urmia']
BASIN_LABELS = {
    'caspiansea':  'Caspian Sea',
    'eastern':     'Eastern',
    'qaraqom':     'Qaraqom',
    'markazi':     'Markazi',
    'persiangolf': 'Persian Gulf',
    'urmia':       'Urmia',
}

# 1. Load data
dsi = pd.read_csv(OUTPUT_DIR / 'grace_dsi.csv', index_col=0, parse_dates=True)
spi = pd.read_csv(OUTPUT_DIR / 'spi_12.csv', index_col=0, parse_dates=True)

# 2. Categorization logic
def classify(val):
    if pd.isna(val): return np.nan
    if val < -2.0: return 3  # Extreme
    if val < -1.5: return 2  # Severe
    if val < -1.0: return 1  # Moderate
    return 0  # Normal/Wet

kappa_results = []

for b in BASINS:
    common = dsi[b].dropna().index.intersection(spi[b].dropna().index)
    if len(common) < 30: continue
    
    y_dsi = dsi[b][common].apply(classify).astype(int)
    y_spi = spi[b][common].apply(classify).astype(int)
    
    kappa = cohen_kappa_score(y_dsi, y_spi)
    matrix = confusion_matrix(y_dsi, y_spi, labels=[0, 1, 2, 3])
    
    # Drought vs No-Drought accuracy
    d_dsi = (y_dsi > 0).astype(int)
    d_spi = (y_spi > 0).astype(int)
    agreement = (d_dsi == d_spi).mean()
    
    kappa_results.append({
        'Basin': BASIN_LABELS[b],
        'Kappa': round(kappa, 3),
        'Drought Agreement (%)': round(agreement * 100, 1),
        'Total Months': len(common)
    })
    
    # Save Confusion Matrix Plot
    plt.figure(figsize=(6, 5))
    sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Normal', 'Mod', 'Sev', 'Ext'],
                yticklabels=['Normal', 'Mod', 'Sev', 'Ext'])
    plt.title(f'Agreement: GRACE vs SPI-12 ({BASIN_LABELS[b]})')
    plt.ylabel('GRACE-DSI State')
    plt.xlabel('SPI-12 State')
    plt.savefig(OUTPUT_DIR / f'agreement_matrix_{b}.png', dpi=300)
    plt.close()

# 3. Save Summary
kappa_df = pd.DataFrame(kappa_results)
kappa_df.to_csv(OUTPUT_DIR / 'hypothesis_h3_kappa.csv', index=False)
print("H3 Quantitative Validation Summary:")
print(kappa_df.to_string(index=False))
