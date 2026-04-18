import sys
import re

file_path = r'e:\projects\drought_analysis\thesis_chapter_4_fa.tex'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Comment out includegraphics and safefig
content = re.sub(r'\\includegraphics', r'% \\includegraphics', content)
content = re.sub(r'\\safefig', r'% \\safefig', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
