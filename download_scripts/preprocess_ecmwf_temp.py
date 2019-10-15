#This program processes the downloaded perturbed forecast (pf) and control
#forecast dataset (cf). It combines the 10 ensembles members of ECMWF's pf 
#with the 1 ECMWF's cf. 
#The temperature forecast for each week (lead time) is calculated by
#averaging all the time steps in that week. The files are then saved to an
#output netCDF file for the next stage of processing. 

#saved together using s2s_utils_comm library

import netCDF4
import numpy as np
import datetime
import os
import sys

def save_netcdf(dest_dir, var_name, init_date, var_lon, var_lat, lead_times, var_hd, var_st, var_units, var_longname, arr_wkly, week_no, var_number):
###-------------------------------------

    # var_number represents the "number" ("member") variable.
    # week_no represents the n-th week (n = 1, 2, 3, 4) of the initialized date.
    week_str = '_week' + str(week_no)
    ds_out = netCDF4.Dataset(dest_dir + "ecmwf_" + var_name + "_2016" + init_date + week_str + '.nc', 'w', format='NETCDF4_CLASSIC')
    
    longitude = ds_out.createDimension('lon', len(var_lon))
    latitude = ds_out.createDimension('lat', len(var_lat))
    time = ds_out.createDimension('time', len(var_hd))
    step = ds_out.createDimension('step', 1)
    
    longitudes = ds_out.createVariable('lon', 'f4', ('lon',))
    latitudes = ds_out.createVariable('lat', 'f4', ('lat',))
    times = ds_out.createVariable('time', 'f8', ('time',))
    steps = ds_out.createVariable('step', 'f4', ('step',))
    
    # Create a new dimension and variable for ensemble member (represented by 'number')
    number = ds_out.createDimension('member', len(var_number))
    numbers = ds_out.createVariable('member', 'i4', ('member',))
    
    # Create the 4-d variable
    #nc_var = ds_out.createVariable(var_name, 'f4', ('time','step','member','lat','lon',),)
    nc_var = ds_out.createVariable(var_name, 'f4', ('time','member','lat','lon',),)
    
    # split init_date = "XXXX" into "XX-XX" to follow date formatting in Panoply(?)
    # month-day
    times.units = 'hours since 2016-' + init_date[0:2] + '-' + init_date[2:4] + ' 00:00:00.0';
    
    longitudes.units= 'degrees_east'
    latitudes.units= 'degrees_north'
    times.calendar = 'standard';
    nc_var.units = var_units
    nc_var.missing_value= -32767
    nc_var.long_name = var_longname
    
    var_time = [];
    for i in range(0,len(var_hd)):
        var_time.append(datetime.datetime(year=int(str(var_hd[i])[0:4]), month=int(str(var_hd[i])[4:6]), day=int(str(var_hd[i])[6:8])))
    
    # Populate the variables
    longitudes[:] = var_lon
    latitudes[:] = var_lat             
    times[:] = netCDF4.date2num(var_time, units=times.units, calendar=times.calendar)
    steps[:] = var_st
    # Assign for members ('numbers') too
    numbers[:] = var_number[:]
    
    nc_var[:,:,:,:] = arr_wkly[:,:,:,:]
    
    # File is saved to .nc once closed
    ds_out.close()

###-------------------------------------
# Define data folder
dest_dir = 'C:/Users/regin/Desktop/regine_s2s_data/model/'
#dest_dir = ''

#run for one date first
#init_date = '0411'

# All the initial dates with complete 7-day week in Mar-April-May for the 2016 runs
init_date = ['0328', '0331', '0404', '0407', '0411', '0414', '0418', '0421', '0425']

# For each initial date file
for i_date in range(0,len(str(init_date))):

    print("Processing initial date:", init_date)
    ds_pf = netCDF4.Dataset(dest_dir + "ecmwf_t2m_2016" + init_date[i_date] + '_pf.nc')
    ds_cf = netCDF4.Dataset(dest_dir + "ecmwf_t2m_2016" + init_date[i_date] + '_cf.nc')
    
    # Read in the variables from pf (extracting data from netCDF file)
    temp_lon = ds_cf.variables['longitude'][:]
    temp_lat = ds_cf.variables['latitude'][:]
    temp_lat = temp_lat[::-1]         #reverse latitude axis from desc. to asc. order for axis shown in Panoply(?) when double-checking
    temp_hd = ds_cf.variables['hdate'][:]
    temp_st = ds_cf.variables['step'][:]
    # Need to read the member ('number') variable
    temp_number = ds_pf.variables['number'][:]
    
    # temp_number[-1] = 10
    # Append another "member" by taking the last one and adding 1 since arr_comb will have one more member from ds_cf
    # Without this step, error message shows
    #ValueError: cannot reshape array of size 169400 (20 x 11 x 22 x 35) into shape (20,10,22,35)
    temp_number = np.append(temp_number, temp_number[-1]+1)
    
    # Read in the array from pf's sfctemp ('t2m') variable
    arr_pf = ds_pf.variables['t2m'][:]
    # Read in the cf's total sfctemp ('t2m') variable
    arr_cf = ds_cf.variables['t2m'][:]
    # print out shape of arr_pf
    arr_shp = arr_pf.shape
    
    # Create a new EMPTY array called "arr_comb" to accommodate the 10 pf and 1 cf members
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
    
    # print(arr_comb), and arr_comb takes the shape (20, 28, 11, 22,35)
    
    # All the weekly data need to follow the same array shape as arr_comb
    #arr_wkly_shape = np.array(arr_comb.shape)
    
    #print(arr_wkly_shape)
    
    ###-------------------------------------
    lead_times = 4
    
    for i in range(lead_times):
        
        #arr_wkly[:,i,:,:,:] = np.mean(arr_comb[:,(i*7):(i*7+7),:,:,:], axis=1)
        
        # arr_wkly takes on a different value for each week.
        # For every i, arr_wkly is the averaged row of values for Week i+1
        # So for every i, we need to define a new arr_wkly by averaging over the 7 days in that week
        arr_wkly = np.mean(arr_comb[:,(i*7):(i*7+7),:,:,:], axis=1) # Average over the week
        
        #print on console (arr_wkly.shape), it shows (20,11,22,35)
        
        #when we split temp_st array into four equal parts, each week is allocated 144 hours.
        #e.g. i = 0, this_weeks_st = temp_st[6] - temp_st[0] = 144
        this_weeks_st = temp_st[i*7+7-1] - temp_st[i*7]
        
        #(time,member,lat,lon)
        arr_wkly = arr_wkly[:,:,::-1,:]    #reverse latitude axis from desc. to asc. order for hyfo package suitability in R
        
        #need to change to (lon,lat,time,member)
        
        # var_st is defined as "this_week_st" below
        # For week_no below, since i goes from 0 to 3, so week_no goes from 1 to 4
        save_netcdf(dest_dir, 'tas', init_date[i_date], temp_lon, temp_lat, lead_times, temp_hd, this_weeks_st, 'K', '2 metre temperature', arr_wkly, week_no=i+1, var_number=temp_number)
    
    ds_pf.close()
    ds_cf.close()
