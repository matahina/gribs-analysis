#! /bin/bash

# $1 : Profile

export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib

######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

DATE=`date +%Y%m%d`

while [ $(cat lock.txt) != "FREE" ]
do
    sleep 1m
done

echo "BUSY" > lock.txt
echo "["`date +"%Y-%m-%d %T %z"`"]     ""NCEP Norms - "${1}"" >> ../../data/logs/"$DATE".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "NCEP Norms" "${1}"

mkdir -p ../../assets/norms_"$1"

cd ../libs

######################################
## NCEP Downloads
######################################
python3 get_norms.py $1

######################################
## R Analysis
######################################

Rscript extract_norms.R $1
rm my.inv

######################################
## Clear files
######################################
cd $DIR

echo "["`date +"%Y-%m-%d %T %z"`"]     ""NCEP Norms Done - "${1^^}" "$DATE"" >> ../../data/logs/"$DATE".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "NCEP Norms Done" "${1^^} $DATE"
echo "" >> ../../data/logs/"$DATE".log
echo "" >> ../../data/logs/"$DATE".log
echo "FREE" > lock.txt
