import xarray as xr
import datetime
import sys

if len(sys.argv) != 3:
    print("Usage: average.py <filename> <variable>")
    sys.exit(1)

ds = xr.open_dataset(sys.argv[1])
print(ds[sys.argv[2]].mean().values)
