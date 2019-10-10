#broadcasting error
#ensemble members not showing up

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
def save_netcdf(dest_dir, var_name, init_date, var_lon, var_lat, lead_times, var_hd, var_st, var_units, var_longname, arr_wkly, step_start, step_skip):
    # Define output file destination
    ds_out = netCDF4.Dataset(dest_dir + "ecmwf_" + var_name + "2016" + init_date + '_weekly.nc', 'w', format='NETCDF4_CLASSIC')

    # Create all the required dimensions of the variable 
    #latitude = ds_out.createDimension('latitude', len(var_lat))
    #longitude = ds_out.createDimension('longitude', len(var_lon))
    longitude = ds_out.createDimension('lon', len(var_lon))
    latitude = ds_out.createDimension('lat', len(var_lat))
    time = ds_out.createDimension('time', len(var_hd))
    step = ds_out.createDimension('step', lead_times)

    # Create the variables to store the data
    #times = ds_out.createVariable('time', 'f8', ('time',))
    #steps = ds_out.createVariable('step', 'f4', ('step',))
    #latitudes = ds_out.createVariable('latitude', 'f4', ('latitude',))
    #longitudes = ds_out.createVariable('longitude11', 'f4', ('longitude',))
    longitudes = ds_out.createVariable('Longitude', 'f4', ('lon',))
    latitudes = ds_out.createVariable('Latitude', 'f4', ('lat',))
    times = ds_out.createVariable('Time', 'f8', ('time',))
    steps = ds_out.createVariable('Step', 'f4', ('step',))
    
    # Create the 4-d variable
    #nc_var = ds_out.createVariable(var_name, 'f4', ('time','step','latitude','longitude',),)
    nc_var = ds_out.createVariable(var_name, 'f4', ('lon','lat','time','step',),)

    # Define the properties of the variables
    times.units = 'hours since 2016-' + init_date + ' 00:00:00.0';

    longitudes.units= 'degrees_east'
    latitudes.units= 'degrees_north'
    times.calendar = 'standard';
    nc_var.units = var_units
    nc_var.missing_value= -32767
    nc_var.long_name = var_longname

    # Format the time variable
    var_time = [];
    for i in range(0,len(var_hd)):
        #appending the hindcast date from 1996-init_date, 1997-init_date, ..., 2015-init_date
        var_time.append(datetime.datetime(year=int(str(var_hd[i])[0:4]), month=int(str(var_hd[i])[4:6]), day=int(str(var_hd[i])[6:8])))
    
    # Populate the variables
    longitudes[:] = var_lon
    latitudes[:] = var_lat
    times[:] = netCDF4.date2num(var_time, units=times.units, calendar=times.calendar);
    steps[:] = var_st[step_start::step_skip]        #[start=6:stop:step=7] slicing of the time-step.
    nc_var[:,:,:,:] = arr_wkly[:,:,:,:]
    
    # File is saved to .nc once closed
    ds_out.close()
###-------------------------------------
# Define data folder
dest_dir = 'C:/Users/regin/Desktop/regine_s2s_data/model/'
lead_times = 4

# All the initial dates with complete 7-day week in Mar-April-May for the 2016 runs
#init_date = ['0328', '0331', '0404', '0407', '0411', '0414', '0418', '0421', '0425']

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

# Read in the variables from cf
temp_lon = ds_cf.variables['longitude'][:]
temp_lat = ds_cf.variables['latitude'][:]
temp_hd = ds_cf.variables['hdate'][:]
temp_st = ds_cf.variables['step'][:]

# Read in the array from pf's sfctemp ('t2m') variable
arr_pf = ds_pf.variables['t2m'][:]
# Read in the cf's total sfctemp ('t2m') variable
arr_cf = ds_cf.variables['t2m'][:]

# arr_shp = (20, 28, 10, 22, 35) = (hdate, steps, members, lat, lon)
arr_shp = arr_pf.shape
    
# Create a new EMPTY array called "arr_comb" to accommodate the 10 pf and 1 cf members
# arr_comb will take the empty form of five dimensions: t2m(hdate, step, member, lat, lon)
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

# Average over the ensemble axis/dimension
arr_ens_avg = np.mean(arr_comb, axis=2)

arr_ens_avg = np.concatenate(arr_comb, axis=2)

#Can we use a code below to add the cf and pf together?
#reshape arr_cf to have the same dimension as arr_pf
#arr_cf_reshaped = arr_cf.reshape(20,28,1,22,35)
#Concatenate arr_cf_reshaped to arr_pf along the 2nd axis
#arr_ens_comb = np.concatenate((arr_pf, arr_cf_reshaped), axis=2)
#from the previous line, arr_ens_comb.shape = (20,28,11,22,35)

#--------------Calculate daily average temperature for each week------------------------

#(hdate, lead_times, member, lat, lon)
#arr_wkly = np.empty([arr_shp[0], lead_times, arr_shp[2], arr_shp[3], arr_shp[4]])

#(hdate, lead_times, lat, lon)
arr_wkly = np.empty([arr_shp[0], lead_times, arr_shp[3], arr_shp[4]])
#for i in range(lead_times):
    #print("Calculating for week: ", i)
#    arr_wkly[:,i,:,:] = np.mean(arr_ens_avg[:,(i*7):(i*7+7),:,:], axis=1) # Average over the week

# this for-loop will loop through lead_times (week) 0,1,2 and 3
# lead time is calculated by averaging all the time steps in that week
for i in range(lead_times):
    print("Calculating for week: ", i)
        #broadcasting same effect throughout every grid point (lat and lon)
        #counted by hours on temp_st, week 1 goes from step 0:7, week 2 goes from step 7:14
        #week 3 goes from step 14:21, week 4 goes from step 21:28.
    
    #arr_wkly[:,i,:,:,:] = (arr_ens_comb[:,(i*7):(i*7+7),:,:,:], axis = 1) # Average over the week
    arr_wkly[:,i,:,:] = np.mean(arr_ens_avg[:,(i*7):(i*7+7),:,:], axis=1) # Average over the week
    #-------------------------------------
    # Output variable to netCDF
    #-------------------------------------
    # Define output file destination
save_netcdf(dest_dir, 't2m_', init_date, temp_lon, temp_lat, lead_times, temp_hd, temp_st, 'K', '2m average weekly temperature', arr_wkly, step_start=6, step_skip=7)

ds_pf.close()
ds_cf.close()