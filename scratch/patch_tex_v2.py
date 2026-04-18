import sys

file_path = r'e:\projects\drought_analysis\thesis_chapter_4_fa.tex'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines to uncomment: 3 to 40, and 46 to 47
# 0-indexed: 2 to 39, and 45 to 46
with open(file_path, 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines):
        if (2 <= i <= 39) or (45 <= i <= 46):
            if line.startswith('% '):
                f.write(line[2:])
            else:
                f.write(line)
        else:
            f.write(line)
