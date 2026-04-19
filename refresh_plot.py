import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import seaborn as sns
from scipy import stats
import arabic_reshaper
from bidi.algorithm import get_display

# Set paths
OUTPUT_DIR = 'outputs'
DSI_MAP = os.path.join(OUTPUT_DIR, 'spatial_drought_map.png')
DSI_TS = os.path.join(OUTPUT_DIR, 'grace_dsi_all_basins.png')
MARKOV_PLOT = os.path.join(OUTPUT_DIR, 'markov_transition_matrices.png')
SCATTER_PLOT = os.path.join(OUTPUT_DIR, 'dsi_spi_scatter.png')
CORR_HEATMAP = os.path.join(OUTPUT_DIR, 'correlation_heatmap.png')
URMIA_COMP = os.path.join(OUTPUT_DIR, 'spi12_vs_grace_dsi.png')

def fix_text(text):
    if not text: return text
    return get_display(arabic_reshaper.reshape(text))

def classify_dsi(val):
    if val >= -0.5: return 'Wet'
    elif val >= -1.0: return 'Near-normal'
    elif val >= -1.5: return 'Moderate'
    else: return 'Severe/Extreme'

STATE_MAP = {
    'Wet': fix_text('ترسالی'),
    'Near-normal': fix_text('نرمال'),
    'Moderate': fix_text('متوسط'),
    'Severe/Extreme': fix_text('شدید')
}
STATES_EN = ['Wet', 'Near-normal', 'Moderate', 'Severe/Extreme']

def refresh_plots():
    print("Starting Comprehensive Plot Refresh with RTL fix...")
    plt.rcParams.update({'font.family': 'Tahoma'})

    # 1. Load Data
    try:
        dsi = pd.read_csv(os.path.join(OUTPUT_DIR, 'grace_dsi.csv'), index_col=0); dsi.index = pd.to_datetime(dsi.index)
        spi12 = pd.read_csv(os.path.join(OUTPUT_DIR, 'spi_12.csv'), index_col=0); spi12.index = pd.to_datetime(spi12.index)
        spi3 = pd.read_csv(os.path.join(OUTPUT_DIR, 'spi_3.csv'), index_col=0); spi3.index = pd.to_datetime(spi3.index)
        spi6 = pd.read_csv(os.path.join(OUTPUT_DIR, 'spi_6.csv'), index_col=0); spi6.index = pd.to_datetime(spi6.index)
        stations = pd.read_excel('synopticdatanew2.xlsx'); stations.columns = [c.strip() for c in stations.columns]
    except Exception as e:
        print(f"Error loading data: {e}"); return

    BASINS = ['caspiansea', 'eastern', 'qaraqom', 'markazi', 'persiangolf', 'urmia']
    BASIN_NAMES_RAW = {'caspiansea': 'دریای خزر', 'eastern': 'شرقی', 'qaraqom': 'قراقوم', 'markazi': 'مرکزی', 'persiangolf': 'خلیج فارس', 'urmia': 'ارومیه'}
    BASIN_COLORS = {'caspiansea': '#1f77b4', 'eastern': '#ff7f0e', 'qaraqom': '#2ca02c', 'markazi': '#d62728', 'persiangolf': '#9467bd', 'urmia': '#8c564b'}

    # --- 1. DSI TIME SERIES ---
    print("  -> DSI Time Series")
    fig, axes = plt.subplots(3, 2, figsize=(16, 12), sharex=True)
    axes = axes.flatten()
    for idx, b in enumerate(BASINS):
        ax = axes[idx]
        ax.fill_between(dsi.index, dsi[b], 0, where=(dsi[b] < -1.0), color='orange', alpha=0.4)
        ax.fill_between(dsi.index, dsi[b], 0, where=(dsi[b] < -1.5), color='red', alpha=0.4)
        ax.plot(dsi.index, dsi[b], color=BASIN_COLORS[b], linewidth=1.2)
        ax.axhline(-1.0, color='orange', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.axhline(-1.5, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.set_title(fix_text(BASIN_NAMES_RAW[b]), fontsize=11)
        ax.set_ylabel('DSI')
    fig.suptitle(fix_text('شاخص شدت خشکسالی GRACE - تمامی حوضه‌های ایران (۲۰۰۲-۲۰۲۲)'), fontsize=13)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(DSI_TS, dpi=300); plt.close()

    # --- 2. MARKOV TRANSITIONS ---
    print("  -> Markov Matrices")
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    for idx, b in enumerate(BASINS):
        seq = dsi[b].dropna().apply(classify_dsi).values
        trans = pd.DataFrame(0, index=STATES_EN, columns=STATES_EN)
        for i in range(len(seq)-1): trans.loc[seq[i], seq[i+1]] += 1
        tp = trans.div(trans.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        tp.index = [STATE_MAP[s] for s in tp.index]; tp.columns = [STATE_MAP[s] for s in tp.columns]
        sns.heatmap(tp, annot=True, fmt='.2f', cmap='Blues', vmin=0, vmax=1, ax=axes[idx], cbar=False)
        axes[idx].set_title(fix_text(BASIN_NAMES_RAW[b])); axes[idx].set_xlabel(fix_text('وضعیت بعدی')); axes[idx].set_ylabel(fix_text('وضعیت فعلی'))
    plt.suptitle(fix_text('احتمالات انتقال وضعیت خشکسالی زنجیره مارکوف'), fontsize=14)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(MARKOV_PLOT, dpi=300); plt.close()

    # --- 3. DSI-SPI SCATTER ---
    print("  -> DSI-SPI Scatter")
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    for idx, b in enumerate(BASINS):
        comb = pd.concat([dsi[b].rename('dsi'), spi12[b].rename('spi12')], axis=1).dropna()
        ax = axes[idx]
        ax.scatter(comb['spi12'], comb['dsi'], c=BASIN_COLORS[b], alpha=0.5, s=20)
        if len(comb) > 5:
            m, c, *_ = stats.linregress(comb['spi12'], comb['dsi'])
            xs = np.linspace(comb['spi12'].min(), comb['spi12'].max(), 50)
            ax.plot(xs, m*xs+c, 'k--', linewidth=1.2)
        ax.set_title(fix_text(BASIN_NAMES_RAW[b])); ax.set_xlabel(fix_text('شاخص SPI-12')); ax.set_ylabel(fix_text('شاخص GRACE-DSI'))
    plt.suptitle(fix_text('نمودار پراکندگی GRACE-DSI در برابر SPI-12'), fontsize=14)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]); plt.savefig(SCATTER_PLOT, dpi=300); plt.close()

    # --- 4. CORRELATION HEATMAP ---
    print("  -> Correlation Heatmap")
    rows = []
    for b in BASINS:
        r_list = []
        for s in [spi3, spi6, spi12]:
            comb = pd.concat([dsi[b], s[b]], axis=1).dropna()
            r_list.append(comb.corr().iloc[0,1])
        rows.append(r_list)
    ct = pd.DataFrame(rows, index=[BASIN_NAMES_RAW[b] for b in BASINS], columns=['SPI-3', 'SPI-6', 'SPI-12'])
    ct.index = [fix_text(i) for i in ct.index]
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(ct, annot=True, cmap='RdYlGn', center=0, fmt='.2f', ax=ax)
    ax.set_title(fix_text('ضریب همبستگی پیرسون: GRACE-DSI در برابر SPI (به تفکیک حوضه و مقیاس زمانی)'))
    plt.savefig(CORR_HEATMAP, dpi=300); plt.close()

    # --- 5. SPATIAL MAP ---
    print("  -> Spatial Map")
    basin_vals = dsi.loc['2021-01-01':].mean()
    fig, ax = plt.subplots(figsize=(12, 9)); cmap = plt.cm.RdBu; norm = plt.Normalize(vmin=-1.5, vmax=1.5)
    name_map = {'caspian sea': 'caspiansea', 'خزر': 'caspiansea', 'urmia': 'urmia', 'ارومیه': 'urmia', 'persian gulf': 'persiangolf', 'خلیج فارس': 'persiangolf', 'central': 'markazi', 'مرکزی': 'markazi', 'eastern': 'eastern', 'شرقی': 'eastern', 'qaraqom': 'qaraqom', 'قراقوم': 'qaraqom'}
    def get_c(name):
        n = str(name).lower().strip(); b = name_map.get(n)
        if not b:
            for k,v in name_map.items():
                if k in n: b = v; break
        return cmap(norm(basin_vals[b])) if b in basin_vals else (0.8,0.8,0.8,1)
    x, y = pd.to_numeric(stations['lon_decima'], errors='coerce'), pd.to_numeric(stations['lat_decima'], errors='coerce')
    colors = [get_c(b) for b in stations['watershed_name']]; valid = ~(x.isna() | y.isna())
    ax.scatter(x[valid], y[valid], c=[colors[i] for i in range(len(colors)) if valid[i]], s=50, edgecolors='black', linewidth=0.3, zorder=3)
    ax.set_title(fix_text("توزیع مکانی شدت خشکسالی (میانگین ۲۰۲۱-۲۰۲۲)"), size=16, weight='bold')
    ax.set_xlabel(fix_text("طول جغرافیایی")); ax.set_ylabel(fix_text("عرض جغرافیایی"))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([]); cbar = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label(fix_text('شدت شاخص GRACE-DSI (قرمز=خشکسالی، آبی=ترسالی)'), size=12)
    plt.savefig(DSI_MAP, dpi=300); plt.close()

    print("DONE: All thesis figures refreshed and RTL-corrected.")

if __name__ == "__main__":
    refresh_plots()
