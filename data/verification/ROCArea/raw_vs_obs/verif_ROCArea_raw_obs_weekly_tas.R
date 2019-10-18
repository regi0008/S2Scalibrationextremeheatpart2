library(calibratoR)
library(downscaleR)
library(transformeR)
library(visualizeR)
library(ncdf4)
library(abind)
library(easyVerification)
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

writeNcdf_verf <- function(gridData, filePath, missingValue = 1e20, tz = 'GMT', units = NULL, version = 3) {
  
  name <- gridData$Variable$varName
  # First defines dimensions.
  dimLon <- ncdim_def('lon', 'degrees_east', gridData$xyCoords$x)
  dimLat <- ncdim_def('lat', 'degrees_north', gridData$xyCoords$y)
  dimMem <- NULL
  dimTime <- NULL
  
  #---------------------------------------  
  # default list
  dimList <- list(dimLat, dimLon)
  
  # In order to keep the dim list exactly the same with the original one, it needs to be changed.
  dimIndex <- grepAndMatch(c('lat', 'lon', 'time'), attributes(gridData$Data)$dimensions)
  #---------------------------------------  
  # Then defines data
  var <- ncvar_def(name, "units", dimList, missingValue)
  
  # Here for ncdf4, there is an option to create version 4 ncdf, in future, it
  # may added here.
  if (version == 3) {
    nc <- nc_create(filePath, var) 
  } else if (version == 4) {
    nc <- nc_create(filePath, var, force_v4 = TRUE)
  } else {
    stop("Which ncdf version you want? Only 3 and 4 can be selected!")
  }
  
  ncatt_put(nc, 'lat', "standard_name","latitude")
  ncatt_put(nc, 'lat', "_CoordinateAxisType","Lat")
  ncatt_put(nc, 'lon', "standard_name","longitude")
  ncatt_put(nc, 'lon', "_CoordinateAxisType","Lon")
  
  # This part has to be put
  ncatt_put(nc, 0, "Conventions","CF-1.4")
  ncatt_put(nc, 0, 'WrittenBy', 'CCRS SSP Team, adapted from hyfo package')
  
  data <- aperm(gridData$Data, dimIndex)
  ncvar_put(nc, name, data)
  nc_close(nc)
  
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

#LOADING OF FILES FOR RAW HINDCAST AND OBSERVATIONS

#test for one date and one particular week first!
dir_1 <- "C:/Users/regin/Desktop/S2Scalibrationextremeheatpart2/data/model/ecmwf/temp"
dir_2 <- "C:/Users/regin/Desktop/S2Scalibrationextremeheatpart2/data/obs"

fcst <- loadNcdf(file.path(dir_1, "ecmwf_tas_20160425_week4.nc"), "tas")
obs <- loadNcdf(file.path(dir_2, "era5_tas_20160425_week4.nc"), "tas")

###################################################################

#VERIFY BETWEEN RAW AND OBS USING ROC AREA

#compute area under the ROC Curve via easyVerification package.
#EnsRoca computes the area under the ROC curve given the observations.
#tercile probabilities: let prob = 1:2/3
#need to state tdim = index of dimension with the different forecasts (fcst date index) = 2
#need to state ensdim = index of dimension with the different ensemble members (fcst member index) = 1
#how to check: print out dim(fcst$Data), check the index positions for time and members
roc <- veriApply(verifun = "EnsRoca",
                 fcst = fcst$Data,
                 obs = obs$Data,
                 prob = 1:2/3,
                 tdim = 2,
                 ensdim = 1)

# plot ROC AREA for each tercile category.
# obs.grid = the grid containing the verifying reference used.
# easyVeri2grid returns a climatological grid.

# ABOVE NORMAL TERCILE
upper.tercile <- easyVeri2grid(easyVeri.mat = roc$cat3,
                               obs.grid = obs,
                               verifun = "EnsRoca")
str(upper.tercile)

#to generate a R-plot of ROCA diagram (for upper tercile)
#spatialPlot(upper.tercile,
#            backdrop.theme= "countries",
#            main = "ROC AREA (Above-normal)",
#            color.theme = "YlOrRd")

fcst_fileName <- "raw_ROCA_AN_20160425_week4.nc"
writeNcdf_verf(upper.tercile, fcst_fileName)
#--------------------------------------------------
# NEAR NORMAL TERCILE
#middle.tercile <- easyVeri2grid(easyVeri.mat = roc$cat2,
#                               obs.grid = obs,
#                               verifun = "EnsRoca")
#str(middle.tercile)

#fcst_fileName <- "raw_ROCA_NN_2016" + init_date + "_week" + week_no + ".nc"
#writeNcdf_verf(middle.tercile, fcst_fileName)
#--------------------------------------------------
# BELOW NORMAL TERCILE
lower.tercile <- easyVeri2grid(easyVeri.mat = roc$cat1,
                               obs.grid = obs,
                               verifun = "EnsRoca")
str(lower.tercile)

fcst_fileName <- "raw_ROCA_BN_20160425_week4.nc"
writeNcdf_verf(lower.tercile, fcst_fileName)
