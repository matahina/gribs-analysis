#!/usr/bin/env Rscript

args = commandArgs(trailingOnly = TRUE)

# args[1] Day Ago
# args[2] Model

library(rNOMADS)
library(stringr)
library(assertthat)
library(ini)
library(collapse)


north <- function(lat) {
  result = ceiling(as.numeric(lat) + 2)
if (result > 90){
  result = 90}
return (result)
}

south <- function(lat) {
  result = floor(as.numeric(lat) - 2)
  if (result < -90){
    result = -90}
    return (result)
}


west_east <- function(lon,we) {
  result_west = floor(as.numeric(lon) - 2)
if (result_west < -180){
  result_west = -180
}
result_east = ceiling(as.numeric(lon) + 2)
if (result_east > 180){
  result_east = 180 
}

if (we == "w"){
  return (result_west)}
if (we == "e"){
  return (result_east)}
}





config <- read.ini("magic_config.ini")

profiles <- data.frame(
  name = character(),
  lat = numeric(),
  lon = numeric(),
  stringsAsFactors = FALSE
)

for (name in names(config)) {
  if (grepl("Profile", name)) {
    if (config[[name]]["use_it"] == "yes") {
      profiles[nrow(profiles) + 1,] <-
        unname(unlist(c(name, config[[name]]["lat"], config[[name]]["lon"])))
    }
  }
}

extractdate <-
  str_replace_all(Sys.Date() - as.integer(args[1]), "-", "")

donneesrun <- data.frame(
  dates = character(),
  runs = character(),
  profile = character(),
  stringsAsFactors = FALSE
)

donneesjour <- data.frame(
  dates = character(),
  runs = character(),
  profile = character(),
  stringsAsFactors = FALSE
)

last_z = 12
step_z = 12

last_sc = 20

the_range = c(seq(0, 193, 3) , seq(198, 385, 6))

if ((args[2] == "gefs")) {
  last_z = 18
  step_z = 6
  
  last_sc = 30
}

if ((args[2] == "cfs")) {
  last_z = 18
  step_z = 6
  
  last_sc = 4
  
  the_range = c(0)
}

first_try <- TRUE
for (z in seq(0, last_z, step_z)) {
  for (sc in seq (1, last_sc, 1)) {
    for (ech in the_range) {
      for (location in profiles$name) {
        if (config[["General"]]["area"] == "yes") {
        filename = sprintf("%s_%02d_%03d_%03d.grb2",
                           extractdate,
                           z,
                           sc,
                           ech)
        } else {
        filename = sprintf("%s_%02d_%03d_%03d_%s.grb2",
                           extractdate,
                           z,
                           sc,
                           ech,
                           location)
        }
        
        if (args[2] == "cfs") {
          filename = sprintf(".%02d.%s%02d.daily.grb2", sc, extractdate, z)
          
          tadaa <- ReadGrib(
            sprintf("../../data/cfs/z500%s", filename),
            '500 mb',
            'HGT',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"],"w"),
              west_east(profiles[which(profiles$name == location), "lon"],"e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          )
          
          tadab <- ReadGrib(
            sprintf("../../data/cfs/t850%s", filename),
            '850 mb',
            'TMP',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"],"w"),
              west_east(profiles[which(profiles$name == location), "lon"],"e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          )
          
          tadac <- ReadGrib(
            sprintf("../../data/cfs/tmp2m%s", filename),
            '2 m above ground',
            'TMP',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"],"w"),
              west_east(profiles[which(profiles$name == location), "lon"],"e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          )
          
          tadad <- ReadGrib(
            sprintf("../../data/cfs/prate%s", filename),
            'surface',
            'PRATE',
            domain = c(
              west_east(profiles[which(profiles$name == location), "lon"],"w"),
              west_east(profiles[which(profiles$name == location), "lon"],"e"),
              north(profiles[which(profiles$name == location), "lat"]),
              south(profiles[which(profiles$name == location), "lat"])
            )
          )
          
          extract_a <-
            BuildProfile(tadaa,
                         as.numeric(profiles[which(profiles$name == location), "lon"]),
                         as.numeric(profiles[which(profiles$name == location), "lat"]),
                         spatial.average = FALSE)
          
          extract_b <-
            BuildProfile(tadab,
                         as.numeric(profiles[which(profiles$name == location), "lon"]),
                         as.numeric(profiles[which(profiles$name == location), "lat"]),
                         spatial.average = FALSE)
          
          extract_c <-
            BuildProfile(tadac,
                         as.numeric(profiles[which(profiles$name == location), "lon"]),
                         as.numeric(profiles[which(profiles$name == location), "lat"]),
                         spatial.average = FALSE)
          
          extract_d <-
            BuildProfile(tadad,
                         as.numeric(profiles[which(profiles$name == location), "lon"]),
                         as.numeric(profiles[which(profiles$name == location), "lat"]),
                         spatial.average = FALSE)
          
          run_name <-
            paste(fmode(
              c(
                tadaa$model.run.date,
                tadab$model.run.date,
                tadac$model.run.date,
                tadad$model.run.date
              )
            )
            , sprintf("sc%02d", sc))
          
          tab_a = data.frame(
            runs = rep(run_name, times = length(extract_a[[1]]$forecast.date)),
            dates = extract_a[[1]]$forecast.date,
            geop = unlist(unname(c(
              extract_a[[1]]$profile.data
            ))) / 10,
            profile = location
          )
          
          tab_b = data.frame(
            runs = rep(run_name, times = length(extract_b[[1]]$forecast.date)),
            dates = extract_b[[1]]$forecast.date,
            tempalt = unlist(unname(c(
              extract_b[[1]]$profile.data
            ))) - 273.15,
            profile = location
          )
          
          tab_c = data.frame(
            runs = rep(run_name, times = length(extract_c[[1]]$forecast.date)),
            dates = extract_c[[1]]$forecast.date,
            tempsol = unlist(unname(c(
              extract_c[[1]]$profile.data
            ))) - 273.15,
            profile = location
          )
          
          tab_d = data.frame(
            runs = rep(run_name, times = length(extract_d[[1]]$forecast.date)),
            dates = extract_d[[1]]$forecast.date,
            precs = unlist(unname(c(
              extract_d[[1]]$profile.data
            ))) * 3600 * 6,
            profile = location
          )
          
          
          rm(total)
          total <-
            merge(
              tab_a,
              tab_b,
              by = c("runs", "dates", "profile"),
              all.x = TRUE,
              all.y = TRUE
            )
          
          total <-
            merge(
              total,
              tab_c,
              by = c("runs", "dates", "profile"),
              all.x = TRUE,
              all.y = TRUE
            )
          total <-
            merge(
              total,
              tab_d,
              by = c("runs", "dates", "profile"),
              all.x = TRUE,
              all.y = TRUE
            )
          
          donneesrun <- total
          
        } else {
          tout <- tryCatch({
            return(ReadGrib(
              sprintf("../../data/%s/%s", args[2], filename),
              c('500 mb', '850 mb', '2 m above ground', 'surface'),
              c('HGT', 'APCP', 'TMP'),
              domain = c(
                west_east(profiles[which(profiles$name == location), "lon"],"w"),
                west_east(profiles[which(profiles$name == location), "lon"],"e"),
                north(profiles[which(profiles$name == location), "lat"]),
                south(profiles[which(profiles$name == location), "lat"])
              )
            ))
          }, warning = function(war) {
            return(ReadGrib(
              sprintf("../../data/%s/%s", args[2], filename),
              c('500 mb', '850 mb', '2 m above ground', 'surface'),
              c('HGT', 'APCP', 'TMP'),
              domain = c(
                west_east(profiles[which(profiles$name == location), "lon"],"w"),
                west_east(profiles[which(profiles$name == location), "lon"],"e"),
                north(profiles[which(profiles$name == location), "lat"]),
                south(profiles[which(profiles$name == location), "lat"])
              )
            ))
          },
          error = function(e) {
            return(data.frame())
          })
          rm(donneesrun)
          
          
          
          donneesrun <- data.frame(
            runs = character(),
            dates = character(),
            profile = character(),
            geop = numeric(),
            tempalt = numeric(),
            tempsol = numeric(),
            precs = numeric(),
            stringsAsFactors = FALSE
          )
          if ((!is.data.frame(tout)) &
              (!is.null(tout$model.run.date))) {
            print(filename)
            print(dim(donneesjour))
            
            profile <-
              BuildProfile(tout,
                           as.numeric(profiles[which(profiles$name == location), "lon"]),
                           as.numeric(profiles[which(profiles$name == location), "lat"]),
                           spatial.average = FALSE)
            
            #Geop
            var_hgt <-
              profile[[1]]$profile.data[, which(profile[[1]]$variables == 'HGT'), 1][which(profile[[1]]$levels == '500 mb')] /
              10
            if (length(var_hgt) == 0) {
              var_hgt = NA
            }
            #T850
            var_talt <-
              profile[[1]]$profile.data[, which(profile[[1]]$variables == 'TMP'), 1][which(profile[[1]]$levels == '850 mb')] - 273.15
            if (length(var_talt) == 0) {
              var_talt = NA
            }
            #T2M
            var_tsol <-
              profile[[1]]$profile.data[, which(profile[[1]]$variables == 'TMP'), 1][which(profile[[1]]$levels == '2 m above ground')] - 273.15
            if (length(var_tsol) == 0) {
              var_tsol = NA
            }
            #prec
            var_pp <-
              profile[[1]]$profile.data[, which(profile[[1]]$variables == 'APCP'), 1][which(profile[[1]]$levels == 'surface')]
            if (length(var_pp) == 0) {
              var_pp = NA
            }
            
            
            
            
            dates <-  profile[[1]]$forecast.date
            runs <-
              paste(tout$model.run.date[1], sprintf("sc%02d", sc))
            
            
            donneesrun[nrow(donneesrun) + 1,] <- c(runs,
                                                   dates,
                                                   location,
                                                   var_hgt,
                                                   var_talt,
                                                   var_tsol,
                                                   var_pp)
          }
          
          
        }
        
        
        
        if (first_try) {
          donneesjour <- donneesrun
          first_try <- FALSE
        } else {
          donneesjour <- rbind(donneesjour, donneesrun)
        }
        
        
        
      }
    }
  }
  
}

write.csv(
  donneesjour,
  sprintf("../../data/%s/%s-%s.csv", args[2], args[2], extractdate),
  row.names = FALSE
)
