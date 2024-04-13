#! /bin/bash


######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR
DATE=`date +%Y%m%d -d "2 day ago"` # tous le lendemain ! à 6:00 UTC (8:00 UTC+2)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export DISPLAY=:0



######################################
######################################
######      ANALYSIS
######################################
######################################


######################################
## System Alerts
######################################
/usr/bin/ffplay -nodisp -autoexit -volume 50 ../../assets/sounds/dialog-warning.ogg
DISPLAY=:0 /usr/bin/notify-send -h "string:desktop-entry:org.kde.konsole"  "Grib2 NOAA R Start" "CFS "$DATE""
../libs/tray-gribs.py "Grib2 NOAA R — CFS "$DATE" Start" &

######################################
## R script and files
######################################
cd ../stats
Rscript -e "rmarkdown::render('cfs_dashboard.Rmd')" > cfs-error.log 2>&1
mv cfs_dashboard.html ../../


######################################
## System Alerts
######################################
/usr/bin/ffplay -nodisp -autoexit -volume 50 ../../assets/sounds/system-ready.ogg
DISPLAY=:0 /usr/bin/notify-send -h "string:desktop-entry:org.kde.konsole"  "Grib2 NOAA R Done" "CFS "$DATE""
killall -9 tray-gribs.py

######################################
## Clear Python cache and files
######################################
cd $DIR
rm -R __pycache__
echo `date +%Y%m%d` > lock/cfs_r.txt

######################################
## Check for error while executing
######################################
if grep -q "Exécution arrêtée" "../stats/cfs-error.log"; then
    QT_STYLE_OVERRIDE=Breeze DISPLAY=:0 kdialog --title "CFS" --textbox ../stats/cfs-error.log 800 500 &
fi
