import arabic_reshaper
from bidi.algorithm import get_display

test_text = "مکانی"
reshaped = arabic_reshaper.reshape(test_text)
fixed = get_display(reshaped)

# print(f"Original: {test_text}")
print(f"Reshaped hex: {[hex(ord(c)) for c in reshaped]}")
print(f"Fixed hex: {[hex(ord(c)) for c in fixed]}")
