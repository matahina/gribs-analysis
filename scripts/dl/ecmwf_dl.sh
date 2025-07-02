#! /bin/bash

# $1 : Run
# $2 : Day ago


######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

DATE=`date +%Y%m%d -d $2" day ago"`

echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 ECMWF DL Start - "$1"z "$DATE"" >> ../../data/logs/"$DATE".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "ECMWF DL Start" "$1z $DATE"

######################################
## GRIB2 Downloads
######################################
source ../../ecmwf_env/bin/activate
python3 get_ecmwf.py $DATE $1
deactivate

######################################
## GRIB2 Extract Data
######################################
EXTR="No"

if [ $1 == "12" ]
then
        EXTR="Yes"
fi

if [ $EXTR == "Yes" ]
then
    echo $EXTR
    Rscript data_extract_ecmwf.R $2
    rm my.inv
fi

######################################
## Clear files
######################################

echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 ECMWF DL Done - "$1"z "$DATE"" >> ../../data/logs/"$DATE".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "ECMWF DL Done" "$1z $DATE"
echo "" >> ../../data/logs/"$DATE".log
echo "" >> ../../data/logs/"$DATE".log

