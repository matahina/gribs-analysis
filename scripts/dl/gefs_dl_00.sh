#! /bin/bash


######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR
DATE=`date +%Y%m%d` # tous le lendemain ! à 6:00 UTC (8:00 UTC+2)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export DISPLAY=:0


while [ $(cat lock/fnmoc_00.txt) != `date +%Y%m%d` ]
do
    sleep 5m
done

######################################
## System Alerts
######################################
/usr/bin/ffplay -nodisp -autoexit -volume 50 ../../assets/sounds/dialog-question.ogg
DISPLAY=:0 /usr/bin/notify-send -h "string:desktop-entry:org.kde.konsole"  "Grib2 NOAA DL Start" "GEFS 00z "$DATE""
../libs/tray-gribs.py "Grib2 NOAA DL — GEFS 00z "$DATE" Start" &


######################################
## GRIB2 Downloads
######################################
cd "../../data/gefs/"


rm dl.txt
rm name.txt
for value in 00
do
    for pert in $(seq -f %02g 1 1 30)
    do
        for ech in $(seq -f %03g 0 6 384)
        do
#         wget -O $DATE"_"$value"_"$ech.grb2 "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p50.pl?file=gfs.t"$value"z.pgrb2full.0p50.f"$ech"&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_PRATE=on&var_HGT=on&var_TMP=on&leftlon=0&rightlon=10&toplat=50&bottomlat=40&dir=%2Fgfs."$DATE"%2F"$value"%2Fatmos"
        echo "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs."$DATE"%2F"$value"%2Fatmos%2Fpgrb2ap5&file=gep"$pert".t"$value"z.pgrb2a.0p50.f"$ech"&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&toplat=50&leftlon=5&rightlon=7&bottomlat=48" >> dl.txt
        echo $DATE"_"$value"_"$pert"_"$ech.grb2 >> name.txt
        done

    done
done

cat dl.txt | xargs -n 1 -P 10 torsocks curl --connect-timeout 5 --max-time 10 --retry 10 --retry-delay 0 --retry-max-time 40 --retry-all-errors -O -J -L




######################################
## GRIB2 Extract Data
######################################
cd $DIR
python3 gefs_rename.py $DATE "00"


######################################
## System Alerts
######################################
/usr/bin/ffplay -nodisp -autoexit -volume 50 ../../assets/sounds/system-ready.ogg
DISPLAY=:0 /usr/bin/notify-send -h "string:desktop-entry:org.kde.konsole"  "Grib2 NOAA DL Done" "GEFS 00z "$DATE""
killall -9 tray-gribs.py

######################################
## Clear Python cache and files
######################################
rm -R __pycache__
rm my.inv
echo `date +%Y%m%d` > lock/gefs_00.txt
