
# Thanks https://rpubs.com/boyerag/297592

prof_name <- commandArgs(trailingOnly=T)[1]

library(ncdf4) # package for netcdf manipulation
library(raster) # package for raster manipulation
library(lubridate)
library(ini)


mega_df = data.frame(date = character(),
           value = numeric(),
           type = character(),
           stringsAsFactors = FALSE)

config <- read.ini("../dl/magic_config.ini")

for (name in names(config)) {
  if (name == prof_name) {
    
    the_lat = as.numeric(unname(unlist(config[[name]]["lat"])))
    
    the_lon = as.numeric(unname(unlist(config[[name]]["lon"])))
    
    if(the_lon < 0) {
      the_lon <- 360+ the_lon
    }
  }
}

for (var_name in c("hgt","t850","t2m")) {
for (year in seq(1991,2020)) {
    file_var_name = var_name
    if (var_name != "hgt") {
    file_var_name = "air"}
nc_data <- nc_open(sprintf("../../assets/norms_%s/%s_%s.nc",prof_name,var_name,year))


lon <- ncvar_get(nc_data, "lon", verbose = F)
lat <- ncvar_get(nc_data, "lat", verbose = F)


the_var.array <- ncvar_get(nc_data, file_var_name) # store the data in a 3-dimensional array



fillvalue <- ncatt_get(nc_data, file_var_name, "_FillValue")

nc_close(nc_data)

the_var.array[the_var.array == fillvalue$value] <- NA

# the_var.slice <- the_var.array[, , 1]

r_brick <- brick(the_var.array, xmn=min(lat), xmx=max(lat), ymn=min(lon), ymx=max(lon),
                 crs=CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs+ towgs84=0,0,0"))

# note that you may have to play around with the transpose (the t() function) and flip() before the data are oriented correctly.
r_brick = t(r_brick)


our_list <- t(extract(r_brick, SpatialPoints(cbind(the_lon,the_lat)), method='simple'))

if (file_var_name == "air") {
  our_list = our_list - 273.15
}
 
if (var_name == "hgt") {
  our_list = our_list / 10
} 

end_count = 365*4

if (leap_year(year)) {
  end_count = end_count + 4
}


date_range = c()
date = as_datetime(sprintf("%s-01-01 00:00:00",year))
while(date < as_datetime(sprintf("%s-01-01 00:00:00",year)) + years(1)) {
  date_range = c(date_range, date)
  date = date + hours(6)
}

results_df <- data.frame(date= as_datetime(date_range), value=our_list)
row.names(results_df) <- NULL
results_df$type = rep(var_name,nrow(results_df))




mega_df <-
  merge(mega_df,
        results_df,
        all.x = TRUE,
        all.y = TRUE)
}}

norms_df = data.frame(subdate = character(),
                      type = character(),
                      value = numeric(),
                      stringsAsFactors = FALSE)


mega_df$subdate <- substr(mega_df$date, 6,23)
for (elem in unique(mega_df$type)) {
  lil_df <- mega_df[which(mega_df$type == elem),]
for (i in unique(mega_df$subdate)){
  small_df <- lil_df[which(lil_df$subdate == i),]
  norms_df[nrow(norms_df) +1,] <- c(i, elem, mean(small_df$value))
}
}






nc_data <- nc_open(sprintf("../../assets/norms_%s/pp.nc",prof_name))


lon <- ncvar_get(nc_data, "lon")
lat <- ncvar_get(nc_data, "lat", verbose = F)


the_var.array <- ncvar_get(nc_data, "prate") # store the data in a 3-dimensional array



fillvalue <- ncatt_get(nc_data, "prate", "_FillValue")


nc_close(nc_data)


the_var.array[the_var.array == fillvalue$value] <- NA


r_brick_orig <- brick(the_var.array, xmn=min(lat), xmx=max(lat), ymn=min(lon), ymx=max(lon), 
                      crs=CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs+ towgs84=0,0,0"))

r_brick <- flip(flip(t(r_brick_orig),direction="x"),direction="x")



our_list <- t(extract(r_brick, SpatialPoints(cbind(the_lon,the_lat)), method='simple'))
our_list <- our_list * 3600 * 24 * 30

row.names(our_list) <- NULL

norms_pp = data.frame(date = sprintf("%02d", seq(1,12)),
                      total = our_list)


write.csv(
  norms_df,
  sprintf("../../assets/norms_%s/norms_df_%s.csv", prof_name, prof_name),
  row.names = FALSE
)

write.csv(
  norms_pp,
  sprintf("../../assets/norms_%s/norms_pp_%s.csv", prof_name, prof_name),
  row.names = FALSE
)
