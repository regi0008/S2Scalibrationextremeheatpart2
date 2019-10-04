#CODE FOR PERTURBED FORECAST

#------------------------------------
#This program downloads the ECMWF hindcast data using MARS.
#The example is for April 2016 run for all model output that
#fall within Nov for control forecast ('cf'). 
#Choice of 1997-2016 for download corresponds to ERA-Int data 
#available for the verification later.

from subprocess import call             # This library needed to make system call 
from ecmwfapi import ECMWFDataServer    # Load the ECMWF API library

#put in your key
server = ECMWFDataServer()

# Define data folder, and create it
dest_dir = 'C:/Users/regin/Desktop/S2Scalibrationextremeheatpart2/data/model/ecmwf/temp/'
call("mkdir -p " + dest_dir, shell=True)

# Remove all *cf.nc files, else grib_to_netcdf will convert with "protocol error"
#call("rm -rf " + dest_dir + "*_cf.nc", shell=True)

#month-date format
init_date = ['03-28', '03-31', '04-04', '04-07', '04-11', '04-14', '04-18', '04-21', '04-25']

#for each initial date
for i in range(0, len(init_date)):               
    server.retrieve({
        "class": "s2",
        "dataset": "s2s",
        "date": "2016-" + init_date[i],
        "expver": "prod",
        "hdate": "2015-" + init_date[i] + "/2014-" + init_date[i] + "/2013-" + init_date[i] + "/2012-" + init_date[i] + "/2011-" + init_date[i] + "/2010-" + init_date[i] + "/2009-" + init_date[i] + "/2008-" + init_date[i] + "/2007-" + init_date[i] + "/2006-" + init_date[i] + "/2005-" + init_date[i] + "/2004-" + init_date[i] + "/2003-" + init_date[i] + "/2002-" + init_date[i] + "/2001-" + init_date[i] + "/2000-" + init_date[i] + "/1999-" + init_date[i] + "/1998-" + init_date[i],
        "levtype": "sfc",
        "model": "glob",
        "number": "1/2/3/4/5/6/7/8/9/10",
        "origin": "ecmf",
        "param": "167",
        "step": "0-24/24-48/48-72/72-96/96-120/120-144/144-168/168-192/192-216/216-240/240-264/264-288/288-312/312-336/336-360/360-384/384-408/408-432/432-456/456-480/480-504/504-528/528-552/552-576/576-600/600-624/624-648/648-672",
        "area": "21/90/-11/141",
        "stream": "enfh",
        "time": "00:00:00",
        "type": "cf",
        "format": "netcdf",
        "target": dest_dir + "ECMWF_temp_2016-" + init_date[i] + "_pf.nc",
})
