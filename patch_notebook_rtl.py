import json
import os
import re

def patch_notebook(nb_path):
    print(f"Patching notebook: {nb_path}")
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # 1. Setup Cell: Add imports and fix_text function
    # Usually the first code cell is index 2 (after a few markdown cells)
    # We'll find the cell containing 'import os, sys'
    setup_cell = None
    for cell in nb['cells']:
        if cell['cell_type'] == 'code' and any('import os, sys' in line for line in cell['source']):
            setup_cell = cell
            break
    
    if setup_cell:
        new_source = []
        # Add imports at the top
        new_source.append("import arabic_reshaper\n")
        new_source.append("from bidi.algorithm import get_display\n")
        new_source.append("\n")
        new_source.append("def fix_text(text):\n")
        new_source.append("    if not text: return text\n")
        new_source.append("    # Handle mixed English/Persian correctly\n")
        new_source.append("    reshaped_text = arabic_reshaper.reshape(text)\n")
        new_source.append("    return get_display(reshaped_text)\n")
        new_source.append("\n")
        
        # Keep original source
        new_source.extend(setup_cell['source'])
        setup_cell['source'] = new_source
        
        # Update BASIN_LABELS in this same cell
        source_str = "".join(setup_cell['source'])
        source_str = source_str.replace("'caspiansea': 'Caspian Sea (دریای خزر)'", "'caspiansea': fix_text('Caspian Sea (دریای خزر)')")
        source_str = source_str.replace("'eastern': 'Eastern (شرقی)'", "'eastern': fix_text('Eastern (شرقی)')")
        source_str = source_str.replace("'qaraqom': 'Qaraqom (قراقوم)'", "'qaraqom': fix_text('Qaraqom (قراقوم)')")
        source_str = source_str.replace("'markazi': 'Markazi (مرکزی)'", "'markazi': fix_text('Markazi (مرکزی)')")
        source_str = source_str.replace("'persiangolf': 'Persian Gulf (خلیج فارس)'", "'persiangolf': fix_text('Persian Gulf (خلیج فارس)')")
        source_str = source_str.replace("'urmia': 'Urmia (ارومیه)'", "'urmia': fix_text('Urmia (ارومیه)')")
        
        # Set font globally for plots
        source_str = source_str.replace("'font.family': 'sans-serif'", "'font.family': 'Tahoma'")
        
        setup_cell['source'] = [line + ("" if line.endswith("\n") else "\n") for line in source_str.splitlines()]

    # 2. Update Plotting Calls throughout the notebook
    # We look for ax.set_title(...) and fig.suptitle(...)
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            new_source = []
            for line in cell['source']:
                # Wrap Persian titles in fix_text()
                # matches ax.set_title('some text') or ax.set_title("some text")
                # but only if not already wrapped
                if ('set_title(' in line or 'suptitle(' in line) and 'fix_text' not in line:
                    # Very simple replacement logic for string literals
                    line = re.sub(r"set_title\((['\"])(.*?)(['\"])", r"set_title(fix_text(\1\2\3)", line)
                    line = re.sub(r"suptitle\((['\"])(.*?)(['\"])", r"suptitle(fix_text(\1\2\3)", line)
                new_source.append(line)
            cell['source'] = new_source

    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Notebook patched successfully.")

if __name__ == "__main__":
    patch_notebook('notebooks/drought_analysis_master.ipynb')
