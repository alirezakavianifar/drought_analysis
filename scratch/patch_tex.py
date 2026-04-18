import sys

file_path = r'e:\projects\drought_analysis\thesis_chapter_4_fa.tex'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Comment out lines 3 to 47
with open(file_path, 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines):
        if 2 <= i <= 46: # 1-indexed 3 to 47 is 0-indexed 2 to 46
            f.write('% ' + line)
        else:
            f.write(line)
