import sys
import re

file_path = r'e:\projects\drought_analysis\thesis_chapter_4_fa.tex'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace booktabs commands with standard hline for testing
content = content.replace('\\toprule', '\\hline')
content = content.replace('\\midrule', '\\hline')
content = content.replace('\\bottomrule', '\\hline')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
