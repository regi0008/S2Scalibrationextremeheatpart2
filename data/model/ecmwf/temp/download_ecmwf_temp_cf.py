#CODE FOR CONTROL FORECAST

import os

#set these environment variables before executing the Python script
os.environ['ECMWF_API_URL'] = "https://api.ecmwf.int/v1"
os.environ['ECMWF_API_KEY'] = "6c37a94e116abf2d13611c4149c584c2"
os.environ['ECMWF_API_EMAIL'] = "regineree@hotmail.com"
#------------------------------------
#This program downloads the ECMWF hindcast data using MARS.
#The example is for April 2016 run for all model output that
#fall within Nov for control forecast ('cf'). 
#Choice of 1997-2016 for download corresponds to ERA-Int data 
#available for the verification later.

from subprocess import call             # This library needed to make system call 
from ecmwfapi import ECMWFDataServer    # Load the ECMWF API library

#put in your key
server = ECMWFDataServer(url="https://api.ecmwf.int/v1",
                         key="6c37a94e116abf2d13611c4149c584c2",
                         email="regineree@hotmail.com")
#or
#server = ECMWFService("mars", url="https://api.ecmwf.int/v1",key="6c37a94e116abf

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
        #"date": "2016-" + init_date[i],
        "date": "2016-04-11",
        "expver": "prod",
        "hdate": "1996-04-11/1997-04-11/1998-04-11/1999-04-11/2000-04-11/2001-04-11/2002-04-11/2003-04-11/2004-04-11/2005-04-11/2006-04-11/2007-04-11/2008-04-11/2009-04-11/2010-04-11/2011-04-11/2012-04-11/2013-04-11/2014-04-11/2015-04-11",
        #"hdate": "2015-" + init_date[i] + "/2014-" + init_date[i] + "/2013-" + init_date[i] + "/2012-" + init_date[i] + "/2011-" + init_date[i] + "/2010-" + init_date[i] + "/2009-" + init_date[i] + "/2008-" + init_date[i] + "/2007-" + init_date[i] + "/2006-" + init_date[i] + "/2005-" + init_date[i] + "/2004-" + init_date[i] + "/2003-" + init_date[i] + "/2002-" + init_date[i] + "/2001-" + init_date[i] + "/2000-" + init_date[i] + "/1999-" + init_date[i] + "/1998-" + init_date[i], "/1997-" + init_date[i] + "/1996-" + init_date[i],
        "levtype": "sfc",
        "model": "glob",
        "origin": "ecmf",
        "param": "167",
        #"step": "0-24",
        "step": "0-24/24-48/48-72/72-96/96-120/120-144/144-168/168-192/192-216/216-240/240-264/264-288/288-312/312-336/336-360/360-384/384-408/408-432/432-456/456-480/480-504/504-528/528-552/552-576/576-600/600-624/624-648/648-672",
        "area": "30/80/-20/150",
        "stream": "enfh",
        "time": "00:00:00",
        "type": "cf",
        "target": dest_dir + "ECMWF_temp_2016-" + init_date[i] + "_cf.grib",
})
    # Convert from grib to netcdf using ECMWF Grib API
    call("grib_to_netcdf -M -I method,type,stream,refdate -T -o " + dest_dir + "ECMWF_temp_2016-" + init_date[i] + "_cf.nc " + dest_dir + "ECMWF_temp_2016-" + init_date[i] + "_cf.grib", shell=True)
    # Remove the grib file after download
    call("rm -rf " + dest_dir + "ECMWF_temp_2016-" + init_date[i] + "_cf.grib", shell=True)