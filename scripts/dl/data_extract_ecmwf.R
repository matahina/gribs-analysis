#!/usr/bin/env Rscript

args = commandArgs(trailingOnly = TRUE)

# args[1] Day Ago

library(rNOMADS)
library(stringr)
library(assertthat)
library(ini)
library(collapse)


north <- function(lat) {
  result = ceiling(as.numeric(lat) + 2)
  if (result > 90) {
    result = 90
  }
  return (result)
}

south <- function(lat) {
  result = floor(as.numeric(lat) - 2)
  if (result < -90) {
    result = -90
  }
  return (result)
}


west_east <- function(lon, we) {
  result_west = floor(as.numeric(lon) - 2)
  if (result_west < -180) {
    result_west = -180
  }
  result_east = ceiling(as.numeric(lon) + 2)
  if (result_east > 180) {
    result_east = 180
  }
  
  if (we == "w") {
    return (result_west)
  }
  if (we == "e") {
    return (result_east)
  }
}





config <- read.ini("../../magic_config.ini")

profiles <- data.frame(
  name = character(),
  lat = numeric(),
  lon = numeric(),
  stringsAsFactors = FALSE
)

for (name in names(config)) {
  if (grepl("Profile", name)) {
    if (config[[name]]["use_it"] == "yes") {
      profiles[nrow(profiles) + 1, ] <-
        unname(unlist(c(name, config[[name]]["lat"], config[[name]]["lon"])))
    }
  }
}

extractdate <-
  str_replace_all(Sys.Date() - as.integer(args[1]), "-", "")

the_dates <- c()
geops <- c()
tsols <- c()
talts <- c()
pps <- c()
mems <- c()
locs <- c()



for (z in seq(0, 12, 12)) {
  for (sc in seq (1, 50, 1)) {
      for (location in profiles$name) {
        

        
        
        tada <- tryCatch({
          return(ReadGrib(
            sprintf("../../data/ecmwf/%s%sdata_hgt%s.grib2", extractdate, str_pad(z, 2, pad = "0"),toString(sc)),
            '500 mb',
            'HGT',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"], "w"),
              west_east(profiles[which(profiles$name == location), "lon"], "e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          ))
        }, warning = function(war) {
          return(ReadGrib(
            sprintf("../../data/ecmwf/%s%sdata_hgt%s.grib2", extractdate, str_pad(z, 2, pad = "0"),toString(sc)),
            '500 mb',
            'HGT',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"], "w"),
              west_east(profiles[which(profiles$name == location), "lon"], "e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          ))
        },
        error = function(e) {
          return(data.frame())
        })
        
        
        
        
        
        extra <- BuildProfile(tada,
                              as.numeric(profiles[which(profiles$name == location), "lon"]),
                              as.numeric(profiles[which(profiles$name == location), "lat"]),
                              spatial.average = FALSE)
        
        
        tadb <- tryCatch({
          return(ReadGrib(
            sprintf("../../data/ecmwf/%s%sdata_tsolpp%s.grib2", extractdate, str_pad(z, 2, pad = "0"),toString(sc)),
            '2 m above ground',
            'TMP',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"], "w"),
              west_east(profiles[which(profiles$name == location), "lon"], "e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          ))
        }, warning = function(war) {
          return(ReadGrib(
            sprintf("../../data/ecmwf/%s%sdata_tsolpp%s.grib2", extractdate, str_pad(z, 2, pad = "0"),toString(sc)),
            '2 m above ground',
            'TMP',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"], "w"),
              west_east(profiles[which(profiles$name == location), "lon"], "e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          ))
        },
        error = function(e) {
          return(data.frame())
        })
        
        
        
        
        
        extrb <- BuildProfile(tadb,
                              as.numeric(profiles[which(profiles$name == location), "lon"]),
                              as.numeric(profiles[which(profiles$name == location), "lat"]),
                              spatial.average = FALSE)
        
        
        
        
        tadc <- tryCatch({
          return(ReadGrib(
            sprintf("../../data/ecmwf/%s%sdata_talt%s.grib2", extractdate, str_pad(z, 2, pad = "0"),toString(sc)),
            '850 mb',
            'TMP',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"], "w"),
              west_east(profiles[which(profiles$name == location), "lon"], "e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          ))
        }, warning = function(war) {
          return(ReadGrib(
            sprintf("../../data/ecmwf/%s%sdata_talt%s.grib2", extractdate, str_pad(z, 2, pad = "0"),toString(sc)),
            '850 mb',
            'TMP',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"], "w"),
              west_east(profiles[which(profiles$name == location), "lon"], "e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          ))
        },
        error = function(e) {
          return(data.frame())
        })
        
        
        
        extrc <- BuildProfile(tadc,
                              as.numeric(profiles[which(profiles$name == location), "lon"]),
                              as.numeric(profiles[which(profiles$name == location), "lat"]),
                              spatial.average = FALSE)
        
        
        
        tadd <- tryCatch({
          return(ReadGrib(
            sprintf("../../data/ecmwf/%s%sdata_tsolpp%s.grib2", extractdate, str_pad(z, 2, pad = "0"),toString(sc)),
            'surface',
            'tprate',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"], "w"),
              west_east(profiles[which(profiles$name == location), "lon"], "e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          ))
        }, warning = function(war) {
          return(ReadGrib(
            sprintf("../../data/ecmwf/%s%sdata_tsolpp%s.grib2", extractdate, str_pad(z, 2, pad = "0"),toString(sc)),
            'surface',
            'tprate',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"], "w"),
              west_east(profiles[which(profiles$name == location), "lon"], "e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          ))
        },
        error = function(e) {
          return(data.frame())
        })
        
        
        
        extrd <- BuildProfile(tadd,
                              as.numeric(profiles[which(profiles$name == location), "lon"]),
                              as.numeric(profiles[which(profiles$name == location), "lat"]),
                              spatial.average = FALSE)
        
            print(z)
            print(sc)
            print(location)
            
            
            if ((!is.data.frame(tada)) &
                (!is.null(tada$model.run.date)) &
                (!is.data.frame(tadb)) &
                (!is.null(tadb$model.run.date)) &
                (!is.data.frame(tadc)) &
                (!is.null(tadc$model.run.date)) &
                (!is.data.frame(tadd)) &
                (!is.null(tadd$model.run.date)) ) {
              
              
              
              the_dates <- c(the_dates, extra[[1]]$forecast.date)
              geops <- c(geops, extra[[1]]$profile.data)
              mems <- c(mems, rep(paste(tada$model.run.date[1], sprintf("sc%02d", sc)),length(extra[[1]]$forecast.date)))
              locs <- c(locs, rep(location,length(extra[[1]]$forecast.date)))
              tsols <- c(tsols, extrb[[1]]$profile.data)
              talts <- c(talts, extrc[[1]]$profile.data)
              
              pps_brut <- c(extrd[[1]]$profile.data)
              pps_net <- c(pps_brut[1],diff(pps_brut))*1000
              pps <- c(pps,pps_net)
              
            
            }
        
      }
  }
  }
  
donneesjour <- data.frame (
  runs = mems,
  dates = the_dates,
  profile = locs,
  geop = geops/10,
  tempalt = talts-273.15,
  tempsol = tsols-273.15,
  precs = pps,
  stringsAsFactors = FALSE
)

write.csv(
  donneesjour,
  sprintf("../../data/ecmwf/ecmwf-%s.csv", extractdate),
  row.names = FALSE
)
