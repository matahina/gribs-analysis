#! /bin/bash


######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR
DATE=`date +%Y%m%d -d "1 day ago"` # tous le lendemain ! à 6:00 UTC (8:00 UTC+2)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export DISPLAY=:0


while [ $(cat lock/gem_00.txt) != `date +%Y%m%d` ]
do
    sleep 5m
done

######################################
## System Alerts
######################################
/usr/bin/ffplay -nodisp -autoexit -volume 50 ../../assets/sounds/dialog-question.ogg
DISPLAY=:0 /usr/bin/notify-send -h "string:desktop-entry:org.kde.konsole"  "Grib2 NOAA DL Start" "CFS 00z06z "$DATE""
../libs/tray-gribs.py "Grib2 NOAA DL — CFS 00z06z "$DATE" Start" &


######################################
## GRIB2 Downloads
######################################
cd "../../data/cfs/"


rm dl.txt

for value in 00 06
do
    for param in "z500" "t850" "prate" "tmp2m"
    do
        for sc in $(seq -f %02g 1 1 4)
        do
        echo "https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod/cfs."$DATE"/"$value"/time_grib_"$sc"/"$param"."$sc"."$DATE""$value".daily.grb2" >> dl.txt
        done

    done
done


# cat dl.txt | xargs -n 1 -P 5 wget --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 0
# cat dl.txt | xargs -n 1 -P 5 torsocks curl --connect-timeout 5 --max-time 180 --retry 20 --retry-all-errors -C - -O
cat dl.txt | xargs -n 1 -P 2 torsocks wget

######################################
## GRIB2 Extract Data
######################################
cd $DIR
python3 cfs_rename.py

######################################
## System Alerts
######################################
/usr/bin/ffplay -nodisp -autoexit -volume 50 ../../assets/sounds/system-ready.ogg
DISPLAY=:0 /usr/bin/notify-send -h "string:desktop-entry:org.kde.konsole"  "Grib2 NOAA DL Done" "CFS 00z06z "$DATE""
killall -9 tray-gribs.py

######################################
## Clear Python cache and files
######################################
rm -R __pycache__
rm my.inv
echo `date +%Y%m%d` > lock/cfs_am.txt
