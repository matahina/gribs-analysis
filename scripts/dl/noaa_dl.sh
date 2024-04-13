#! /bin/bash

# $1 : Model
# $2 : Run
# $3 : Day ago


######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

DATE=`date +%Y%m%d -d $3" day ago"`

while [ $(cat lock.txt) != "FREE" ]
do
    sleep 1m
done

echo "BUSY" > lock.txt
echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 NOAA DL Start - "${1^^}" "$2"z "$DATE"" >> ../../data/logs/"$DATE".log

######################################
## GRIB2 Downloads
######################################
python3 $1_get.py $DATE $2

######################################
## GRIB2 Extract Data
######################################
EXTR="No"

if [ $2 == "18" ]
then
    if [ "$1" == "cfs" ] || [ "$1" == "gefs" ]
    then
        EXTR="Yes"
    fi
fi

if [ $2 == "12" ]
then
    if [ "$1" == "fnmoc" ] || [ "$1" == "gem" ]
    then
        EXTR="Yes"
    fi
fi

if [ $EXTR == "Yes" ]
then
    echo $EXTR
    Rscript $1_extract.R $3
    rm my.inv
fi

######################################
## Clear files
######################################
echo "FREE" > lock.txt

echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 NOAA DL Done - "${1^^}" "$2"z "$DATE"" >> ../../data/logs/"$DATE".log
echo "" >> ../../data/logs/"$DATE".log
echo "" >> ../../data/logs/"$DATE".log

