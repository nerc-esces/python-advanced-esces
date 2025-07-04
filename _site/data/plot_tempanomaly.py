#!/usr/bin/env python

import numpy as np
import netCDF4 as nc
import argparse
import matplotlib.pyplot as plt
import matplotlib
import sys
matplotlib.use('agg')


def get_year(year, data):
    '''
    plots data from a given year and saves it as a png file
    '''
    start = (year - 2000) * 12
    plt.clf()

    min_value=data[:,:,:].min()
    max_value=data[:,:,:].max()

    for y in range(0,12):
        print(year,"-",y+1,sep="")
        #flip the data vertically and show the world the northern hemisphere (positive latitudes) on top
        data2 = data[start+y,::-1,:]
        plt.title("%d-%02d" % (year,y+1))
        plt.imshow(data2, vmin=min_value, vmax=max_value)
        plt.colorbar()
        filename="%d-%02d.png" % (year,y+1)
        #plt.show()
        plt.savefig(filename)
        plt.clf()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='plot_tempanomaly',
                    description='Plots the temperature anomaly from the GISS Surface Temperature Analysis version 4. You will need a copy of the dataset in NetCDF format from https://data.giss.nasa.gov/pub/gistemp/gistemp1200_GHCNv4_ERSSTv5.nc.gz')

    parser.add_argument('filename')
    parser.add_argument('--start', default="2000")
    parser.add_argument('--end', default="2024")

    args = parser.parse_args()

    # check date is valid
    if int(args.start)>=int(args.end):
        sys.stderr.write("Error: Start date must be before end date.\n")
        sys.exit(1)

    if int(args.start)<2000:
        sys.stderr.write("Error: Start date must be 2000 or later.\n")
        sys.exit(1)

    if int(args.start)>2023:
        sys.stderr.write("Error: Start date must be before 2023.\n")
        sys.exit(1)

    if int(args.end)<2001:
        sys.stderr.write("Error: End date must be after 2001.\n")
        sys.exit(1)

    if int(args.end)>2024:
        sys.stderr.write("Error: End date must be no later than 2024.\n")
        sys.exit(1)

    ds = nc.Dataset(args.filename, "r")
    tempanomaly = ds.variables['tempanomaly']

    for year in range(int(args.start),int(args.end)):
         get_year(year, tempanomaly)
