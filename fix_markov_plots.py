import json
import os
import arabic_reshaper
from bidi.algorithm import get_display

def fix_text(text):
    if not text: return text
    return get_display(arabic_reshaper.reshape(text))

def patch_notebook():
    nb_path = r'e:\projects\drought_analysis\notebooks\drought_analysis_master.ipynb'
    if not os.path.exists(nb_path):
        print(f"Notebook {nb_path} not found.")
        return

    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        
        new_source = []
        source = cell['source']
        i = 0
        while i < len(source):
            line = source[i]
            
            # 1. Update classify_dsi
            if "return 'Wet'" in line:
                line = line.replace("'Wet'", "fix_text('ترسالی')")
            if "return 'Near-normal'" in line:
                line = line.replace("'Near-normal'", "fix_text('نرمال')")
            if "return 'Moderate'" in line:
                line = line.replace("'Moderate'", "fix_text('خشکسالی متوسط')")
            if "return 'Severe/Extreme'" in line:
                line = line.replace("'Severe/Extreme'", "fix_text('خشکسالی شدید')")
            
            # 2. Update STATES
            if "STATES = ['Wet'" in line:
                line = "    \"STATES = [fix_text('ترسالی'), fix_text('نرمال'), fix_text('خشکسالی متوسط'), fix_text('خشکسالی شدید')]\\n\",\n"

            # 3. Update Axis Labels
            if "ax.set_xlabel('Next state')" in line:
                line = line.replace("'Next state'", "fix_text('وضعیت بعدی')")
            if "ax.set_ylabel('Current state')" in line:
                line = line.replace("'Current state'", "fix_text('وضعیت فعلی')")
            if "ax.set_xlabel('SPI-12')" in line:
                line = line.replace("'SPI-12'", "fix_text('شاخص SPI-12')")
            if "ax.set_ylabel('GRACE-DSI')" in line:
                line = line.replace("'GRACE-DSI'", "fix_text('شاخص GRACE-DSI')")

            # 4. Update Crosstab rownames/colnames
            if "rownames=['GRACE-DSI']" in line:
                line = line.replace("'GRACE-DSI'", "fix_text('GRACE-DSI')")
            if "colnames=['SPI-12']" in line:
                line = line.replace("'SPI-12'", "fix_text('SPI-12')")

            # 5. Update Suptitle in Phase 12
            if "GRACE-DSI vs SPI-12: Categorical Agreement Matrices" in line:
                line = line.replace("GRACE-DSI vs SPI-12: Categorical Agreement Matrices (# months)", 
                                    "ماتریس‌های توافق طبقه‌بندی شده: GRACE-DSI در مقابل SPI-12 (تعداد ماه‌ها)")

            # 6. Update titles in Phase 12
            if "ax.set_title(f'{BASIN_LABELS[b].split(\" (\")[0]} — Agreement Matrix')" in line:
                line = line.replace("ax.set_title(f'{BASIN_LABELS[b].split(\" (\")[0]} — Agreement Matrix')", 
                                    "ax.set_title(fix_text(f'ماتریس توافق - {BASIN_LABELS[b]}'))")

            new_source.append(line)
            i += 1
        
        cell['source'] = new_source

    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Notebook patched with Persian Markov labels.")

if __name__ == "__main__":
    patch_notebook()
