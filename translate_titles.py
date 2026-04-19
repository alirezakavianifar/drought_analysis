import json
import os
import arabic_reshaper
from bidi.algorithm import get_display
import re

def fix_text(text):
    if not text: return text
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def patch_notebook():
    nb_path = r'e:\projects\drought_analysis\notebooks\drought_analysis_master.ipynb'
    if not os.path.exists(nb_path):
        print(f"Notebook {nb_path} not found.")
        return

    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    translations = {
        'GRACE Drought Severity Index - All Iranian Basins (2002-2022)': 'شاخص شدت خشکسالی GRACE - تمامی حوضه‌های ایران (۲۰۰۲-۲۰۲۲)',
        'GRACE TWSA Annual Trend by Basin (OLS, 2002-2022)': 'روند سالانه ذخیره آب GRACE به تفکیک حوضه (OLS، ۲۰۰۲-۲۰۲۲)',
        'Markov Chain Drought State Transition Probabilities': 'احتمالات انتقال وضعیت خشکسالی زنجیره مارکوف',
        'Standardized Precipitation Index (SPI-12) - CHIRPS (2002-2022)': 'شاخص بارش استاندارد (SPI-12) - داده‌های CHIRPS (۲۰۰۲-۲۰۲۲)',
        'GRACE TWSA Trend (cm/yr)': 'روند ذخیره آب GRACE (سانتی‌متر در سال)',
        'Precipitation Trend (mm/yr)': 'روند بارش (میلی‌متر در سال)',
        'Trend': 'روند',
        'Seasonal': 'فصلی',
        'Residual': 'باقی‌مانده',
        'Original TWSA': 'داده‌های اصلی TWSA',
        'Long-term Trend Component': 'مولفه روند بلندمدت',
        'Annual Seasonal Cycle': 'چرخه فصلی سالانه',
        'Residual (noise + sub-seasonal signal)': 'باقی‌مانده (نویز + سیگنال زیرفصلی)',
        'Next state': 'وضعیت بعدی',
        'Current state': 'وضعیت فعلی'
    }

    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        
        new_source = []
        source = cell['source']
        for line in source:
            # Apply translations to string literals inside fix_text()
            for eng, per in translations.items():
                if f"fix_text('{eng}')" in line:
                    line = line.replace(f"fix_text('{eng}')", f"fix_text('{per}')")
                elif f'fix_text("{eng}")' in line:
                    line = line.replace(f'fix_text("{eng}")', f'fix_text("{per}")')
            
            # Special case for split titles in Phase 12 (line 1449 and 1851)
            if "ax.set_title(BASIN_LABELS[b].split(' (')[0]" in line:
                line = line.replace("BASIN_LABELS[b].split(' (')[0]", "BASIN_LABELS[b]")
            
            # Handle axis labels that might be English
            if "ax.set_xlabel('Next state')" in line:
                line = line.replace("'Next state'", "fix_text('وضعیت بعدی')")
            if "ax.set_ylabel('Current state')" in line:
                line = line.replace("'Current state'", "fix_text('وضعیت فعلی')")

            new_source.append(line)
        
        cell['source'] = new_source

    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Notebook titles translated and patched.")

if __name__ == "__main__":
    patch_notebook()
