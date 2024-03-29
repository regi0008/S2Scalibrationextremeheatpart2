library(CSTools)
fcst1 <- c(27.13, 26.8, 26.93, 26.92, 27.32, 26.91, 27.14, 26.93, 26.87, 26.83, 26.98, 27.2, 26.81, 27.26, 26.69, 26.87, 27.02, 26.7, 26.94, 27.23, 27.16, 27.12, 26.91, 27.26, 26.9, 27.0, 26.96, 26.77, 26.96, 27.24, 26.99, 26.85, 26.7, 27.16, 27.12, 27.11, 26.99, 27.03, 26.94, 26.97, 26.88, 26.96, 27.23, 26.86, 27.42, 27.4, 26.97, 27.3, 27.09, 27.16, 27.17)
fcst2 <- c(28.56, 28.03, 28.24, 28.22, 28.86, 28.2, 28.57, 28.24, 28.15, 28.08, 28.32, 28.67, 28.04, 28.77, 27.86, 28.15, 28.39, 27.87, 28.25, 28.72, 28.61, 28.54, 28.21, 28.76, 28.18, 28.35, 28.28, 27.99, 28.28, 28.73, 28.33, 28.11, 27.87, 28.6, 28.54, 28.52, 28.33, 28.39, 28.25, 28.3, 28.15, 28.29, 28.71, 28.12, 29.01, 28.99, 28.3, 28.83, 28.5, 28.61, 28.61)
fcst3 <- c(28.18, 27.87, 27.99, 27.98, 28.36, 27.96, 28.19, 27.99, 27.93, 27.89, 28.04, 28.25, 27.87, 28.31, 27.76, 27.93, 28.08, 27.76, 28.0, 28.28, 28.21, 28.17, 27.97, 28.3, 27.96, 28.05, 28.01, 27.84, 28.01, 28.28, 28.05, 27.91, 27.77, 28.21, 28.17, 28.16, 28.04, 28.08, 27.99, 28.03, 27.94, 28.02, 28.27, 27.92, 28.45, 28.44, 28.02, 28.34, 28.14, 28.21, 28.21)
fcsts <- data.frame(fcst1, fcst2 , fcst3)
fname <- c('ECMWF S2S Raw','ECMWF S2S Raw, Calibrated MVA','ECMWF S2S MVA, Calibrated MVA')
ts <- c(27.35,27.79)
es <- c(27.03,28.4)
obs_list <- c(28.04)
PlotForecastPDF(fcsts,tercile.limits= ts, extreme.limits= es,
                title = "[Start 11 Apr 2016] Weekly Mean 2-m Temperature forecasts - Week 3, Singapore", var.name = "Temperature (Celsius)",
                fcst.names = fname, obs = obs_list)