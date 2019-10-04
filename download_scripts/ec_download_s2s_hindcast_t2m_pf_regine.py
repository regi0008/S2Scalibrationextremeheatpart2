#!/usr/bin/env python
'''
This program downloads the ECMWF SFC T2m hindcast data (10 pf) using MARS, from the
S2S dataset. It is based on the forecast start date (centre) and also downloads 4 start dates
before and after the centred start date, for a total of 4+4+1=9 samples
'''
import os
import time
import timeit
import datetime
import numpy as np

import ecmwfapi_public # Load the ECMWF API library
server = ecmwfapi_public.ECMWFDataServer()

start = timeit.default_timer()
#cur_datetime = datetime.datetime.now() # based on SYSTEM time
cur_datetime = datetime.datetime(2016,4,11)  # manual download. change year/month/day
cur_year = "%04d"%cur_datetime.year
cur_month = "%02d"%cur_datetime.month
cur_day = "%02d"%cur_datetime.day
date_centered = np.array(cur_year + '-' + cur_month + '-' + cur_day, dtype=np.datetime64)

if cur_datetime.strftime('%A') == 'Monday':
    date_array = date_centered + np.hstack([-14,-11,-7,-4,0,3,7,10,14]) #-4 for last Thursday, 0 for current Monday, 3 for next Thursday
if cur_datetime.strftime('%A') == 'Thursday':
        date_array = date_centered + np.hstack([-14,-10,-7,-3,0,4,7,11,14]) #-3 for last Thursday, 0 for current Monday, 4 for next Thursday

# Create the saved path
ecmwf_path = "/nas44/rkang/ecmwf_hindcast_data_s2s_verification_regine/"
if os.path.exists(ecmwf_path) == False:
   os.makedirs(ecmwf_path)

# Generate hindcast_date_str String running from past 20 years from date_str
# To handle leap year with Monday/Thursday falls on Feb 29
for index_date in range(len(date_array)):
    cur_year = "%04d"%date_array[index_date].astype(object).year
    cur_month = "%02d"%date_array[index_date].astype(object).month
    cur_day = "%02d"%date_array[index_date].astype(object).day
    date_str = cur_year + cur_month + cur_day

    if cur_month == '02' and cur_day == '29':
        first_year = int(cur_year) - 20
        cur_day = int(cur_day) - 1 #get 02-28 instead
        hindcast_date_str = str(first_year) + str(cur_month) + str(cur_day) #First entry
        for year in range(first_year+1,first_year+20):
            hindcast_date_str += "/" + str(year) + str(cur_month) + str(cur_day) #add the rest of the years
    else:
        first_year = int(cur_year) - 20
        hindcast_date_str = str(first_year) + str(cur_month) + str(cur_day) #First entry
        for year in range(first_year+1,first_year+20):
            hindcast_date_str += "/" + str(year) + str(cur_month) + str(cur_day) #add the rest of the years

    # Download the .cf file
    server.retrieve({
        "class": "s2",
        "dataset": "s2s",
        "date": date_str,
        "expver": "prod",
        "hdate": hindcast_date_str,
        "levtype": "sfc",
        "model": "glob",
        "number": "1/to/10",
        "origin": "ecmf",
        "param": "167",
        "step": "0-24/24-48/48-72/72-96/96-120/120-144/144-168/168-192/192-216/216-240/240-264/264-288/288-312/312-336/336-360/360-384/384-408/408-432/432-456/456-480/480-504/504-528/528-552/552-576/576-600/600-624/624-648/648-672",
        "area": "21/90/-11/141",
        "stream": "enfh",
        "time": "00:00:00",
        "type": "pf",
		"target": ecmwf_path + "ecmwf_t2m_" + date_str + "_pf.grib",
    })
    print 'done! Downloaded the .pf file.' + '\n'

    os.system('/grib_to_netcdf -M -I method,type,stream,refdate -T -o ' + ecmwf_path + 'ecmwf_t2m_' + date_str + '_pf.nc ' + ecmwf_path + "ecmwf_t2m_" + date_str + "_pf.grib")
    print 'done! Convert .grib to .nc file' + '\n'

# Remove all '.grib' files
os.system('rm -rf ' + ecmwf_path + 'ecmwf_t2m*.grib')
print 'done! Remove all (grib) files' + '\n'

# Calculate Program RunTime
stop = timeit.default_timer()
total_time = stop - start
mins, secs = divmod(total_time, 60)
hours, mins = divmod(mins, 60)

print ('Total running time %02d hr :%02d min :%02d sec\n' % (hours, mins, secs))
print '---------------------------------------------------------------------------------------------\n'
