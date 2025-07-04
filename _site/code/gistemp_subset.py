#!/usr/bin/env python

#creates a subset of just the 21st century data for the GISS Surface Temperature Analysis version 4 dataset
#the original dataset can be found at https://data.giss.nasa.gov/pub/gistemp/gistemp1200_GHCNv4_ERSSTv5.nc.gz
#this script was used to prepare the original data, learners do not need to run it.

import xarray as xr
import datetime
ds = xr.open_dataset("gistemp1200_GHCNv4_ERSSTv5.nc")

print(ds)

ds2 = ds.sel(time=slice('2000-01-01', '2023-12-31'), drop=True)

#ds2 = ds.isel(time=slice(1440,1730))
#time_bnds = ds.time_bnds.isel(time=slice(1440,1730))

#da = xr.DataArray(ds2, ds.coords, ds.dims, ds.attrs)
print("new dataset:",ds2)
#print("new dataset:",da)

#print("da.attrs=",da.attrs)
ds2.to_netcdf("gistemp1200-21c.nc")
