library(calibratoR)
library(downscaleR)
library(transformeR)
library(visualizeR)
library(ncdf4)
library(abind)
library(easyVerification)
library(SpecsVerification)
library(s2dverification)
library(RColorBrewer)

########## USE HYFO PACKAGE ##########
loadNcdf <- function(filePath, varname, tz = 'GMT', ...) {
  nc <- nc_open(filePath)
  var <- nc$var
  # Use name to locate the variable
  call_1 <- as.call(c(
    list(as.name('$'), var, varname)
  ))
  var <- eval(call_1)
  if(is.null(var)) stop('No such variable name, check source file.')
  
  dimNames <- unlist(lapply(1:length(var$dim), function(x) var$dim[[x]]$name))
  print(dimNames)
  
  # Only deals with the most common dimensions, futher dimensions will be added in future.
  dimIndex <- grepAndMatch(c('lon', 'lat', 'time', 'member'), dimNames)
  #dimIndex <- grepAndMatch(c('member', 'time', 'lat', 'lon'), dimNames)
  print(dimIndex)
  if (length(dimIndex) < 3) stop('Your file has less than 3 dimensions.')
  
  # First needs to identify the variable name, load the right data
  message('Loading data...')
  nc_data <- ncvar_get(nc, var)
  message('Processing...')
  
  gridData <- list()
  gridData$Variable$varName <- varname
  gridData$xyCoords$x <- var$dim[[dimIndex[1]]]$vals
  attributes(gridData$xyCoords$x)$name <- dimNames[dimIndex[1]]
  
  gridData$xyCoords$y <- var$dim[[dimIndex[2]]]$vals
  attributes(gridData$xyCoords$y)$name <- dimNames[dimIndex[2]]
  
  # Time part needs to be taken seperately
  timeUnit <- strsplit(var$dim[[dimIndex[3]]]$units, split = ' since')[[1]][1]
  timeDiff <- var$dim[[dimIndex[3]]]$vals
  # To get real time, time since when has to be grabbed from the dataset.
  timeSince <- as.POSIXlt(strsplit(var$dim[[dimIndex[3]]]$units, split = 'since')[[1]][2], tz = tz)
  
  #  Date <- rep(timeSince, length(timeDiff))
  unitDic <- data.frame(weeks = 'weeks', days = 'days', hours = 'hours',
                        minutes = 'mins', seconds = 'secs')
  
  timeDiff <- as.difftime(timeDiff, units = as.character(unitDic[1, timeUnit]))
  
  #   if (grepl('day', timeUnit)) {
  #     Date$mday <- Date$mday + timeDiff
  #   } else if (grepl('second', timeUnit)) {
  #     Date$sec <- Date$sec + timeDiff
  #   }
  Date <- timeSince + timeDiff
  
  # data directly loaded from ncdf4 will drop the dimension with only one value.
  # the varsize shows the real dimension, without any dropping.
  dim(nc_data) <- var$varsize
  
  # Right now there is no need to add end Date, in furture, may be added as needed.
  gridData$Dates$start <- as.character(Date)
  
  # Adding data to grid data
  # At leaset should be 3 dimensions, lon, lat, time.
  gridData$Data <- nc_data
  
  attributes(gridData$Data)$dimensions <- dimNames
  
  if (!is.na(dimIndex[4])) 
    gridData$Members <- var$dim[[dimIndex[4]]]$vals
  nc_close(nc)
  
  output <- gridData
  
  return(output)
  
}

# in order to first grep than match.
# match only provides for exactly match, 
# dimIndex <- grepAndMatch(c('lon', 'lat', 'time', 'member'), dimNames)
grepAndMatch <- function(x, table) {
  index <- unlist(lapply(x, function(x) {
    a <- grep(x, table)
  }))
  return(index)
}

###################################################################

#LOADING OF FILES FOR CALIBRATED HINDCAST AND OBSERVATIONS

#test for one date and one particular week first!
dir_1 <- "C:/Users/regin/Desktop/S2Scalibrationextremeheatpart2/data/calibrated_weekly_temp"
dir_2 <- "C:/Users/regin/Desktop/S2Scalibrationextremeheatpart2/data/obs"

#fcst_cal is in format: (member : time : lat : lon)
#obs is in format: (time : lat : lon)
fcst_cal <- loadNcdf(file.path(dir_1, "fcst_cal_MVA_20160411_week1.nc"), "tas")
obs <- loadNcdf(file.path(dir_2, "era5_tas_20160411_week1_format.nc"), "tas")

###################################################################
#COMPUTE FAIR CONTINUOUS RANKED PROBABILITY SCORE (FairCRPS)

calculate_crps_fcst_cal <- veriApply(verifun = "FairCrps",
                                     fcst = fcst_cal$Data,
                                     obs = obs$Data,
                                     tdim = 3,
                                     ensdim = 4)

#Output array calculate_crps_fcst_cal to netcdf file
metadata <- list(calculate_crps_fcst_cal = list(units = 'unit'))
attr(calculate_crps_fcst_cal, 'variables') <- metadata
names(dim(calculate_crps_fcst_cal)) <- c('lon', 'lat', 'time')

lon <- seq(90, 141, 1.5)
dim(lon) <- length(lon)
metadata <- list(lon = list(units = 'degrees_east'))
attr(lon, 'variables') <- metadata
names(dim(lon)) <- 'lon'

lat <- seq(-10.5, 21, 1.5)
dim(lat) <- length(lat)
metadata <- list(lat = list(units = 'degrees_north'))
attr(lat, 'variables') <- metadata
names(dim(lat)) <- 'lat'

faircrps_fcst_cal_fileName <- "cal_MVA_FairCrps_20160411_week1.nc"
#ArrayToNetCDF(list(lon, lat, calculate_crps_fcst_cal), faircrps_fcst_cal_fileName)
ArrayToNetCDF(list(calculate_crps_fcst_cal, lat, lon), faircrps_fcst_cal_fileName)
###################################################################
