import netCDF4 as nc
import numpy as np
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='summary',
                    description='Produces a summary of the data from the GISS Surface Temperature Analysis version 4. You will need a copy of the dataset in NetCDF format from https://data.giss.nasa.gov/pub/gistemp/gistemp1200_GHCNv4_ERSSTv5.nc.gz')

    parser.add_argument('filename')

    args = parser.parse_args()

    ds = nc.Dataset(args.filename, "r")

    print("Summary for", args.filename)
    print("min",np.min(ds.variables['tempanomaly']))
    print("max",np.max(ds.variables['tempanomaly']))
    print("standard deviation",np.std(ds.variables['tempanomaly']))
    print("mean",np.mean(ds.variables['tempanomaly']))
    print()
