import xarray as xr
import datetime
import sys

if len(sys.argv) != 3:
    print("Usage: average.py <filename> <output file>")
    sys.exit(1)

ds = xr.open_dataset(sys.argv[1])

outfile = open(sys.argv[2], "w")
outfile.write(str(ds['tempanomaly'].mean().values))
outfile.close()
