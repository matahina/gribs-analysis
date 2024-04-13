#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)

library(rNOMADS)
library(stringr)
library(assertthat)


extractdate <- str_replace_all(Sys.Date() - as.integer(args[1]), "-", "")

donneescfs <- data.frame(dates=character(),
                         runs=character(),
                         stringsAsFactors=FALSE) 

donneesjour <- data.frame(dates=character(),
                          runs=character(),
                          stringsAsFactors=FALSE)

first_try <- TRUE
for (z in seq(0,12,12)) {
  
  for (sc in seq (1,20,1)) {
    
    for (ech in seq (0,384,6)) {
    
    filename = sprintf("%s_%02d_%02d_%03d.grb2",extractdate,z,sc,ech)
    
    geop <- c()
    dates <- c()
    runs <- c()
    
   
    # tout <- ReadGrib(
    #   sprintf("../../data/gefs/%s", filename),
    #   c('500 mb','850 mb','2 m above ground','surface'),
    #   c('HGT','APCP','TMP'),
    #   domain = c(5,7,50,48)
    # )
    
    
    tout <- tryCatch({
      return(
        ReadGrib(
          sprintf("../../data/gem/%s", filename),
          c('500 mb','850 mb','2 m above ground','surface'),
          c('HGT','APCP','TMP'),
          domain = c(5,7,50,48)
        )
      )
    }, warning = function(war) {
      return(
        ReadGrib(
          sprintf("../../data/gem/%s", filename),
          c('500 mb','850 mb','2 m above ground','surface'),
          c('HGT','APCP','TMP'),
          domain = c(5,7,50,48)
        )
      )
    },
    error = function(e) {
      return(data.frame())
    })

    if ((!is.data.frame(tout)) & (!is.null(tout$model.run.date) )) {
      
      print(filename)
      print(dim(donneesjour))
      
      profile <- BuildProfile(tout, 6.1727, 49.1191,spatial.average = FALSE)
      
      #Geop
      var_hgt <- profile[[1]]$profile.data[,which(profile[[1]]$variables == 'HGT'),1][which(profile[[1]]$levels == '500 mb')]
      
      #T850
      var_talt <- profile[[1]]$profile.data[,which(profile[[1]]$variables == 'TMP'),1][which(profile[[1]]$levels == '850 mb')]
      
      #T2M
      var_tsol <- profile[[1]]$profile.data[,which(profile[[1]]$variables == 'TMP'),1][which(profile[[1]]$levels == '2 m above ground')]
      
      #prec
      var_pp <- profile[[1]]$profile.data[,which(profile[[1]]$variables == 'APCP'),1][which(profile[[1]]$levels == 'surface')]
      
      
      
      
      geop <- c(geop, var_hgt /10)
      dates <- c(dates, profile[[1]]$forecast.date)
      runs <- c(runs,paste(tout$model.run.date[1], sprintf("sc%02d",sc)))
      
      rm(donneescfs)
      donneescfs <- data.frame(runs=runs,
                               dates=dates,
                               geop=geop) 
      
      
      tempalt <- c()
      
      
      
      tempalt <- c(tempalt, var_talt - 273.15)
      
      donneescfs$tempalt <- tempalt
      
      
      tempsol <- c()
      
      
      
      tempsol <- c(tempsol, var_tsol - 273.15)
      
      if(length(tempsol) != 0){
        donneescfs$tempsol <- tempsol
      } else {
        donneescfs$tempsol <- c(NA)
      }
      
      
      precs <- c()
      
      
      
      # precs <- c(precs, var_pp *3600*6)
      precs <- c(precs, var_pp)
      if(length(precs) != 0){
      donneescfs$precs <- precs
      } else {
        donneescfs$precs <- c(NA)
      }
      
      if (first_try) {
        donneesjour <- donneescfs
        first_try <- FALSE
      } else {
        donneesjour <- rbind(donneesjour, donneescfs)
      }
      
    }
    
    

    
    }
  }
  
}

write.csv(donneesjour,sprintf("../../data/gem/gem-%s.csv", extractdate), row.names = FALSE)












