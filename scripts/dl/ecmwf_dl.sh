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

echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 ECMWF DL Start - "$2"z "$3"" >> ../../data/logs/"$3".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "ECMWF DL Start" "$2z $3"

######################################
## GRIB2 Downloads
######################################
source ../../ecmwf_env/bin/activate
python3 get_ecmwf.py $3 $2
deactivate
python3 split_ecmwf.py $3 $2


######################################
## GRIB2 Extract Data
######################################
EXTR="No"

if [ $2 == "12" ]
then
        EXTR="Yes"
fi

if [ $EXTR == "Yes" ]
then
    echo $EXTR
    Rscript data_extract_ecmwf.R $3
    rm my.inv
fi

######################################
## Clear files
######################################

echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 ECMWF DL Done - "$2"z "$3"" >> ../../data/logs/"$3".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "ECMWF DL Done" "$2z $3"
echo "" >> ../../data/logs/"$3".log
echo "" >> ../../data/logs/"$3".log

