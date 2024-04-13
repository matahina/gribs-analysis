#! /bin/bash


######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR
DATE=`date +%Y%m%d -d "1 day ago"` # tous le lendemain ! à 6:00 UTC (8:00 UTC+2)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export DISPLAY=:0


while [ $(cat lock/gem_12.txt) != `date +%Y%m%d` ]
do
    sleep 1m
done

######################################
## System Alerts
######################################
/usr/bin/ffplay -nodisp -autoexit -volume 50 ../../assets/sounds/dialog-question.ogg
DISPLAY=:0 /usr/bin/notify-send -h "string:desktop-entry:org.kde.konsole"  "Grib2 NOAA DL Start" "FNMOC 12z "$DATE""
../libs/tray-gribs.py "Grib2 NOAA DL — FNMOC 12z "$DATE" Start" &


######################################
## GRIB2 Downloads
######################################
cd "../../data/fnmoc/"

# rm dl.txt
# rm name.txt
# for value in 00 06 12 18
# do
#     for ech in $(seq -f %03g 0 3 384)
#     do
# 
#         echo "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p50.pl?file=gfs.t"$value"z.pgrb2full.0p50.f"$ech"&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_PRATE=on&var_HGT=on&var_TMP=on&leftlon=0&rightlon=10&toplat=50&bottomlat=40&dir=%2Fgfs."$DATE"%2F"$value"%2Fatmos" >> dl.txt
#         echo $DATE"_"$value"_"$ech.grb2 >> name.txt
#     done
# done
# 
# wget -i dl.txt


rm dl.txt
rm name.txt
for value in 12
do
    for pert in $(seq -f %03g 1 1 20)
    do
        for ech in $(seq -f %03g 0 6 384)
        do
        echo "https://nomads.ncep.noaa.gov/cgi-bin/filter_fens.pl?dir=%2Ffens."$DATE"%2F"$value"%2Fpgrb2ap5&file=ENSEMBLE.halfDegree.MET.fcst_et"$pert"."$ech"."$DATE""$value"&lev_2_m_above_ground=on&lev_500_mb=on&lev_850_mb=on&lev_surface=on&var_APCP=on&var_HGT=on&var_TMP=on&subregion=&leftlon=5&rightlon=7&toplat=50&bottomlat=48" >> dl.txt
#         echo "https://nomads.ncep.noaa.gov/pub/data/nccf/com/naefs/prod/fens."$DATE"/"$value"/pgrb2a/ENSEMBLE.MET.fcst_et"$pert"."$ech"."$DATE$value >> dl.txt
        echo $DATE"_"$value"_"$pert"_"$ech.grb2 >> name.txt
        done

    done
done


cat dl.txt | xargs -n 1 -P 3 torsocks curl --connect-timeout 5 --max-time 10 --retry 10 --retry-delay 0 --retry-max-time 40 --retry-all-errors -O -J -L





######################################
## GRIB2 Extract Data
######################################
cd $DIR
python3 fnmoc_rename.py $DATE "12"
Rscript fnmoc_extract.R


######################################
## System Alerts
######################################
/usr/bin/ffplay -nodisp -autoexit -volume 50 ../../assets/sounds/system-ready.ogg
DISPLAY=:0 /usr/bin/notify-send -h "string:desktop-entry:org.kde.konsole"  "Grib2 NOAA DL Done" "FNMOC 12z "$DATE""
killall -9 tray-gribs.py

######################################
## Clear Python cache and files
######################################
rm -R __pycache__
rm my.inv
echo `date +%Y%m%d` > lock/fnmoc_12.txt
