import xarray as xr
import datetime
import sys

if len(sys.argv) != 2:
    print("Usage: mean_tempanomly.py <filename> <output file>")
    sys.exit(1)

ds = xr.open_dataset(sys.argv[1])

print(ds['tempanomaly'].mean().values)
