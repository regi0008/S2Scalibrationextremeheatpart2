#This program processes the downloaded perturbed forecast (pf) and control
#forecast dataset (cf). It combines the 10 ensembles members of ECMWF's pf 
#with the 1 ECMWF's cf. 
#The temperature forecast for each week (lead time) is calculated by
#averaging all the time steps in that week. The files are then saved to an
#output netCDF file for the next stage of processing. 

import netCDF4
import numpy as np
import datetime
import os
import sys
#sys.path is a list of strings that determines the interpreter's search path for modules.
#sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/' + '../../../utils/')
#import s2s_utils_comm
#from s2s_utils_comm import save_netcdf
#import s2s_utils_comm as ucomm
###-------------------------------------
#s2s_utils_comm function
def save_netcdf(dest_dir, var_name, init_date, var_lon, var_lat, var_hd, var_member, var_st, var_units, var_longname, arr_wkly):
    # Define output file destination
    ds_out = netCDF4.Dataset(dest_dir + "ecmwf_" + var_name + "_2016" + init_date + '_weekly' + '.nc', 'w', format='NETCDF4_CLASSIC')
    #ds_out = netCDF4.Dataset(dest_dir + "ecmwf_" + var_name + "_2016" + init_date + '_week' + week_num + '.nc', 'w', format='NETCDF4_CLASSIC')
    
    # Create all the required dimensions of the variable 
    longitude = ds_out.createDimension('lon', len(var_lon))
    latitude = ds_out.createDimension('lat', len(var_lat))
    time = ds_out.createDimension('time', len(var_hd))
    member = ds_out.createDimension('member', len(var_member))
    step = ds_out.createDimension('step', lead_times)

    # Create the variables to store the data
    longitudes = ds_out.createVariable('lon', 'f4', ('lon',))
    latitudes = ds_out.createVariable('lat', 'f4', ('lat',))
    times = ds_out.createVariable('time', 'f8', ('time',))
    members = ds_out.createVariable('member', 'f4', ('member',))
    steps = ds_out.createVariable('step', 'f4', ('step',))
    
    # Create the 4-d variable
    #this 4-d variable represents t2m
    #nc_var = ds_out.createVariable(var_name, 'f4', ('time','step','latitude','longitude',),)
    nc_var = ds_out.createVariable(var_name, 'f4', ('lon','lat','time','member'),)

    # Define the properties of the variables

    #reference time period is based on initializaton date
    #count from initialization date and backwards...

    times.units = 'hours since 2016-' + init_date + ' 00:00:00.0';
    longitudes.units = 'degrees_east'
    latitudes.units = 'degrees_north'
    times.calendar = 'standard';
    nc_var.units = var_units
    nc_var.missing_value= -32767
    nc_var.long_name = var_longname

    # Format the time variable
    var_time = [];
    for i in range(0,len(var_hd)):
        #appending the hindcast date to a list: 1996-init_date, 1997-init_date, ..., 2015-init_date
        var_time.append(datetime.datetime(year=int(str(var_hd[i])[0:4]), month=int(str(var_hd[i])[4:6]), day=int(str(var_hd[i])[6:8])))
    
    # Populate the variables
    longitudes[:] = var_lon
    latitudes[:] = var_lat
    #latitudes[::-1] = var_lat    #remember to reserve from descending to ascending order
    times[:] = netCDF4.date2num(var_time, units=times.units, calendar=times.calendar);
    steps[:] = var_st
    nc_var[:,:,:,:] = arr_wkly[:,:,:,:]
    
    # File is saved to .nc once closed
    ds_out.close()
###-------------------------------------
# Define data folder
dest_dir = 'C:/Users/regin/Desktop/regine_s2s_data/model/'

# All the initial dates with complete 7-day week in Mar-April-May for the 2016 runs
#init_date = ['03-28', '03-31', '04-04', '04-07', '04-11', '04-14', '04-18', '04-21', '04-25']

#run for one date first
init_date = '0411'

# For each initial date file
#for_loop to loop through all 9 initial dates
#for i_date in range(0,len(init_date)):
print("Processing initial date:", init_date)
ds_pf = netCDF4.Dataset(dest_dir + "ecmwf_t2m_2016" + init_date + '_pf.nc') # Load the pf file
ds_cf = netCDF4.Dataset(dest_dir + "ecmwf_t2m_2016" + init_date + '_cf.nc') # Load the cf file

# You may want to uncomment the following lines
# to print out the file and variable information
print(ds_pf.file_format)
print(ds_pf.dimensions.keys())
print(ds_pf.variables)
print(ds_cf.file_format)
print(ds_cf.dimensions.keys())
print(ds_cf.variables)

# Read in the variables from cf (extracting data from netCDF file)
#temp_lon = ds_cf.variables['longitude'][:]
#temp_lat = ds_cf.variables['latitude'][:]
#temp_hd = ds_cf.variables['hdate'][:]
#temp_st = ds_cf.variables['step'][:]

# Read in the variables from pf (extracting data from netCDF file)
temp_lon = ds_pf.variables['longitude'][:]
temp_lat = ds_pf.variables['latitude'][:]
temp_lat = temp_lat[::-1]                 #convert latitude from descending to ascending order
temp_hd = ds_pf.variables['hdate'][:]
temp_st = ds_pf.variables['step'][:]
temp_member = ds_pf.variables['number'][:]

# Read in the array from pf's sfctemp ('t2m') variable
arr_pf = ds_pf.variables['t2m'][:]
# Read in the cf's total sfctemp ('t2m') variable
arr_cf = ds_cf.variables['t2m'][:]

# arr_shp = (20, 28, 10, 22, 35) = (hdate, steps, members, lat, lon)
arr_shp = arr_pf.shape
    
# Create a new EMPTY array called "arr_comb" to accommodate the 10 pf and 1 cf members
# arr_comb is a 5-D array which gives info about t2m:
# arr_shp[0] is for the hdate, arr_shp[1] is for the step
# arr_shp[2] is for the members. #arr_shp[2]+1 is just adding 10 + 1 members
# arr_shp[3] is for the latitudes, arr_shp[4] is for the longitudes
arr_comb = np.empty([arr_shp[0], arr_shp[1], arr_shp[2]+1, arr_shp[3], arr_shp[4]])

# Populate arr_comb with pf and cf data
arr_comb[:,:,0:10,:,:] = arr_pf
#the line above assigns arr_pf to all the rows and columns of arr_comb except in axis = 2,
#the last "row" of the ensemble (aka ensemble member number 11, but index 10).
#This means only ensemble members number 0,1,2,3,4,5,6,7,8,9 is counted here.
arr_comb[:,:,10,:,:] = arr_cf
#the line above assigns arr_cf to all the rows and columns of arr_comb except in axis = 2,
#only for the last "row" of the ensemble.
#This means only ensemble member number 10 is counted here.

#Now with combined pf and cf, print out arr_comb and its shape
print(arr_comb)
#print(arr_comb.shape)
#(20,28,11,22,35)

#--------------Calculate temperature for each week------------------------
lead_times = 4

    #try to make into format readable by hyfo package: (lon, lat, time, member)
    #arr_wkly = np.empty([arr_shp[4], arr_shp[3], arr_shp[0], arr_shp[2]+1])
    #print(arr_wkly.shape) #which is (35, 22, 20, 11)=(lon,lat,time,member)

# this for-loop will loop through lead_times (week) 0,1,2 and 3
# lead time is calculated by averaging all the time steps in that week
for i in range(lead_times):
    print("Calculating for week: ", i)  #i goes from 0,1,2,3
    
    #initialize arr_wkly first as an empty array of dimensions (20,11,22,35)
    #arr_wkly = np.empty([arr_shp[0], arr_shp[1], arr_shp[2]+1, arr_shp[3], arr_shp[4]])
    
    arr_wkly = np.empty([arr_shp[0], lead_times, arr_shp[2]+1, arr_shp[3], arr_shp[4]])
    
    #np.mean here is averaging the 7 days in a week into 1, to represent Week 1, next 7 days into 1, to represent Week 2, etc...
    arr_wkly[:,i,:,:,:] = np.mean(arr_comb[:,(i*7):(i*7+7),:,:,:], axis = 1) # Average over the week
    #arr_wkly[:,i,:,:] = np.mean(arr_comb[:,(i*7):(i*7+7),:,:], axis = 1) # Average over the week

    #-------------------------------------
    # Output variable to netCDF
    #-------------------------------------
    # Define output file destination
    save_netcdf(dest_dir, 'tas', init_date, temp_lon, temp_lat, temp_hd, temp_member, temp_st, 'K', '2 metre temperature', arr_wkly)

ds_pf.close()
ds_cf.close()