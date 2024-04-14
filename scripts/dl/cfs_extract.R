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


for (z in seq(0,18,6)) {

  for (sc in seq (1,4,1)) {
    
    basefname = sprintf(".%02d.%s%02d.daily.grb2",sc,extractdate,z)
    
    geop <- c()
    dates <- c()
    runs <- c()
    
    tadaa <- ReadGrib(
      sprintf("../../data/cfs/z500%s", basefname),
      '500 mb',
      'HGT',
      domain = c(5.5,6.5,49.5,48.5)
    )
    
    geop <- c(geop, tadaa$value /10)
    dates <- c(dates, tadaa$forecast.date)
    runs <- c(runs,paste(tadaa$model.run.date, sprintf("sc%02d",sc)))
    
    rm(donneescfs)
    donneescfs <- data.frame(runs=runs,
                             dates=dates,
                             geop=geop) 
    
    
    tempalt <- c()
    
    tadab <- ReadGrib(
      sprintf("../../data/cfs/t850%s", basefname),
      '850 mb',
      'TMP',
      domain = c(5.5,6.5,49.5,48.5)
    )
    
    tempalt <- c(tempalt, tadab$value - 273.15)
  
    donneescfs$tempalt <- tempalt
    
    
    tempsol <- c()
    
    tadac <- ReadGrib(
      sprintf("../../data/cfs/tmp2m%s", basefname),
      '2 m above ground',
      'TMP',
      domain = c(6,7,49,48)
    )
    
    tempsol <- c(tempsol, tadac$value - 273.15)
    
    tempsol <- c(tempsol,rep(NA,nrow(donneescfs)-length(tempsol)))
    donneescfs$tempsol <- tempsol
    
    
    precs <- c()
    
    tadad <- ReadGrib(
      sprintf("../../data/cfs/prate%s", basefname),
      'surface',
      'PRATE',
      domain = c(6,7,49,48)
    )
    
    precs <- c(precs, tadad$value *3600*6)
    
    precs <- c(precs,rep(NA,nrow(donneescfs)-length(precs)))
    donneescfs$precs <- precs
    
    
    if (sc==1 & z==0) {
      donneesjour <- donneescfs
    } else {
      donneesjour <- rbind(donneesjour, donneescfs)
    }
      
   }
  
}

write.csv(donneesjour,sprintf("../../data/cfs/cfs-%s.csv", extractdate), row.names = FALSE)
