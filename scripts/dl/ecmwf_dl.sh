#! /bin/bash

# $1 : Model
# $2 : Run
# $3 : Date YYYYMMDD

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.local/lib/:/lib:/usr/lib:/usr/local/lib
export PATH=$PATH:~/.local/bin/

######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 ECMWF DL Start - "${1^^}" "$2"z "$3"" >> ../../data/logs/"$3".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "ECMWF DL Start" "${1^^} $2z $3"

######################################
## GRIB2 Download and extract
######################################

test -f "../../py_env/bin/activate" && . ../../py_env/bin/activate
python3 get_extract_$1.py $3 $2
test deactivate && deactivate

######################################
## Clear files
######################################

echo "["`date +"%Y-%m-%d %T %z"`"]     ""Grib2 ECMWF DL Done - "${1^^}" "$2"z "$3"" >> ../../data/logs/"$3".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "ECMWF DL Done" "${1^^} $2z $3"
echo "" >> ../../data/logs/"$3".log
echo "" >> ../../data/logs/"$3".log

