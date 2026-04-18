import sys

file_path = r'e:\projects\drought_analysis\thesis_chapter_4_fa.tex'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(file_path, 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines):
        if 'def\\bidi@tabular@init{\\ar@ialign}' in line:
            f.write('% ' + line)
        else:
            f.write(line)
