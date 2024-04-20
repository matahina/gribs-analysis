#!/usr/bin/env Rscript

args = commandArgs(trailingOnly = TRUE)

# args[1] Day Ago
# args[2] Model

library(rNOMADS)
library(stringr)
library(assertthat)


extractdate <-
  str_replace_all(Sys.Date() - as.integer(args[1]), "-", "")

donneesrun <- data.frame(dates = character(),
                         runs = character(),
                         stringsAsFactors = FALSE)

donneesjour <- data.frame(dates = character(),
                          runs = character(),
                          stringsAsFactors = FALSE)

last_z = 12
step_z = 12

last_sc = 20

last_ech = 384
step_ech = 6

if ((args[2] == "gefs")) {
  last_z = 18
  step_z = 6
  
  last_sc = 30
}

if ((args[2] == "cfs")) {
  last_z = 18
  step_z = 6
  
  last_sc = 4
  
  last_ech = 0
  step_ech = 0
}

first_try <- TRUE
for (z in seq(0, last_z, step_z)) {
  for (sc in seq (1, last_sc, 1)) {
    for (ech in seq (0, last_ech, step_ech)) {
      filename = sprintf("%s_%02d_%03d_%03d.grb2", extractdate, z, sc, ech)
      
      if (args[2] == "cfs") {
        filename = sprintf(".%02d.%s%02d.daily.grb2", sc, extractdate, z)
        
        tadaa <- ReadGrib(
          sprintf("../../data/cfs/z500%s", filename),
          '500 mb',
          'HGT',
          domain = c(5.5, 6.5, 49.5, 48.5)
        )
        
        tadab <- ReadGrib(
          sprintf("../../data/cfs/t850%s", filename),
          '850 mb',
          'TMP',
          domain = c(5.5, 6.5, 49.5, 48.5)
        )
        
        tadac <- ReadGrib(
          sprintf("../../data/cfs/tmp2m%s", filename),
          '2 m above ground',
          'TMP',
          domain = c(6, 7, 49, 48)
        )
        
        tadad <- ReadGrib(
          sprintf("../../data/cfs/prate%s", filename),
          'surface',
          'PRATE',
          domain = c(6, 7, 49, 48)
        )
        
        
        tab_a = data.frame(
          runs = paste(tadaa$model.run.date, sprintf("sc%02d", sc)),
          dates = tadaa$forecast.date,
          geop = tadaa$value / 10
        )
        
        tab_b = data.frame(
          runs = paste(tadab$model.run.date, sprintf("sc%02d", sc)),
          dates = tadab$forecast.date,
          tempalt = tadab$value - 273.15
        )
        
        tab_c = data.frame(
          runs = paste(tadac$model.run.date, sprintf("sc%02d", sc)),
          dates = tadac$forecast.date,
          tempsol = tadac$value - 273.15
        )
        
        tab_d = data.frame(
          runs = paste(tadad$model.run.date, sprintf("sc%02d", sc)),
          dates = tadad$forecast.date,
          precs = tadad$value * 3600 * 6
        )
        
        
        rm(total)
        total <-
          merge(
            tab_a,
            tab_b,
            by = c("runs", "dates"),
            all.x = TRUE,
            all.y = TRUE
          )
        
        total <-
          merge(
            total,
            tab_c,
            by = c("runs", "dates"),
            all.x = TRUE,
            all.y = TRUE
          )
        total <-
          merge(
            total,
            tab_d,
            by = c("runs", "dates"),
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
            domain = c(5, 7, 50, 48)
          ))
        }, warning = function(war) {
          return(ReadGrib(
            sprintf("../../data/%s/%s", args[2], filename),
            c('500 mb', '850 mb', '2 m above ground', 'surface'),
            c('HGT', 'APCP', 'TMP'),
            domain = c(5, 7, 50, 48)
          ))
        },
        error = function(e) {
          return(data.frame())
        })
        rm(donneesrun)
        
        
        
        donneesrun <- data.frame(
          runs = character(),
          dates = character(),
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
            BuildProfile(tout, 6.1727, 49.1191, spatial.average = FALSE)
          
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
          
          
          donneesrun[nrow(donneesrun) + 1, ] <- c(runs,
                                                  dates,
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

write.csv(
  donneesjour,
  sprintf("../../data/%s/%s-%s.csv", args[2], args[2], extractdate),
  row.names = FALSE
)
