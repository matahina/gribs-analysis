#! /bin/bash

# $1 : Set
# $2 : Day ago
# $3 : Profile


######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

DATE=`date +%Y%m%d -d $2" day ago"`

while [ $(cat lock.txt) != "FREE" ]
do
    sleep 1m
done

echo "BUSY" > lock.txt
echo "["`date +"%Y-%m-%d %T %z"`"]     ""R Analysis Start - "${1^^}" "$DATE"" >> ../../data/logs/"$DATE".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "R Analysis Start" "${1^^} $DATE"
LOC=`sed -nr "/^\["$3"\]/ { :l /^name[ ]*=/ { s/[^=]*=[ ]*//; p; q;}; n; b l;}" ./magic_config.ini`

######################################
## R Analysis
######################################
cd ../stats
R -e "rmarkdown::render('"$1"_dashboard.Rmd', output_file = '"$1"_dashboard_"$3".html')" --args "$LOC" "$3" "$2" >> ../../data/logs/"$DATE".log
rm my.inv

######################################
## Clear files
######################################
cd $DIR
python3 storage_clean.py

echo "["`date +"%Y-%m-%d %T %z"`"]     ""R Analysis Done - "${1^^}" "$DATE"" >> ../../data/logs/"$DATE".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "R Analysis Done" "${1^^} $DATE"
echo "" >> ../../data/logs/"$DATE".log
echo "" >> ../../data/logs/"$DATE".log
echo "FREE" > lock.txt

test -f ../libs/publish_dashboards.sh && ../libs/publish_dashboards.sh
