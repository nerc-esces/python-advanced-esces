#!/usr/bin/env python

#creates a subset of just the 21st century data for the GISS Surface Temperature Analysis version 4 dataset
#the original dataset can be found at https://data.giss.nasa.gov/pub/gistemp/gistemp1200_GHCNv4_ERSSTv5.nc.gz
#this script was used to prepare the original data, learners do not need to run it.

import xarray as xr
import datetime



ds = xr.open_dataset("gistemp1200.nc")

for year in range(2000,2023):
    ds2 = ds.sel(time=slice(str(year) + '-01-01', str(year) + '-12-31'), drop=True)
    ds2.to_netcdf(str(year) + ".nc")
