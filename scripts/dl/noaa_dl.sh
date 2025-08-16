#! /bin/bash

# $1 : Model
# $2 : Run
# $3 : Date YYYYMMDD

export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib

######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 NOAA DL Start - "${1^^}" "$2"z "$3"" >> ../../data/logs/"$3".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "NOAA DL Start" "${1^^} $2z $3"

######################################
## GRIB2 Downloads
######################################
python3 get.py $3 $2 $1

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
    Rscript data_extract.R $3 $1
    rm my.inv
fi

######################################
## Clear files
######################################

echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 NOAA DL Done - "${1^^}" "$2"z "$3"" >> ../../data/logs/"$3".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "NOAA DL Done" "${1^^} $2z $3"
echo "" >> ../../data/logs/"$3".log
echo "" >> ../../data/logs/"$3".log

