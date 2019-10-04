#!/usr/bin/env python
'''
This program downloads the daily ECMWF Temperature ERA5 data using CDS API, from the C3S dataset.
'''
import os
import time
import timeit
import datetime

import cdsapi
c = cdsapi.Client()

start = timeit.default_timer();

# Specify the time period for which to download
years = ["1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", \
"2004","2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012",  "2013", "2014", "2015"]

# Create the saved path
ecmwf_path = "/nas44/rkang/ecmwf_era5_data_c3s_regine/daily_temp";
if os.path.exists(ecmwf_path) == False:
   os.makedirs(ecmwf_path);

# Download the file
for i in range(len(years)):
    c.retrieve("reanalysis-era5-single-levels",
    {
    "format": "netcdf",
    "product_type": "reanalysis",
    "variable": ["2m_temperature"],
    "year": years[i],
    "month": ["03","04","05"],
    "day": ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31"],
    "area": "21.5/90/-10.5/141",
    "grid": "1.5/1.5",
    "time": ["00:00","01:00","02:00","03:00","04:00","05:00","06:00","07:00","08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00","21:00","22:00","23:00"],
    },
    ecmwf_path+"/2t_era5_"+years[i]+".nc")

# Calculate Program RunTime
stop = timeit.default_timer();
total_time = stop - start;
mins, secs = divmod(total_time, 60)
hours, mins = divmod(mins, 60)

print ('Total running time %02d hr :%02d min :%02d sec\n' % (hours, mins, secs));
print '---------------------------------------------------------------------------------------------\n';
