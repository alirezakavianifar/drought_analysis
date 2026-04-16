import rasterio
import gzip
import shutil
from pathlib import Path
import os
import numpy as np

CACHE_DIR = Path('data/chirps')
# Test one file
test_file = list(CACHE_DIR.glob('*.gz'))[0]
print(f"Testing: {test_file}")

# Decompress temporarily
temp_tif = 'temp_test.tif'
with gzip.open(test_file, 'rb') as f_in:
    with open(temp_tif, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

with rasterio.open(temp_tif) as src:
    print(f"Raster shape: {src.shape}")
    print(f"CRS: {src.crs}")
    # Sample at a known point in Iran (Tehran ~ 35.7, 51.4)
    for val in src.sample([(51.4, 35.7)]):
        print(f"Precipitation at sample point: {val[0]}")

os.remove(temp_tif)
