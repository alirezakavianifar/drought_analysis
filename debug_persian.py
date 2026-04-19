import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
import os

def fix_text(text):
    if not text: return text
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

plt.rcParams.update({'font.family': 'Segoe UI'})

test_text = "توزیع مکانی شدت خشکسالی"
fixed = fix_text(test_text)

# print(f"Original: {test_text}")
# print(f"Fixed (raw bytes): {fixed.encode('utf-8')}")

fig, ax = plt.subplots()
ax.text(0.5, 0.5, fixed, size=20)
ax.set_title(fixed)
plt.savefig('debug_persian.png')
print("Saved debug_persian.png")
