#! /bin/bash

# $1 : Set
# $2 : Profile
# $3 : Date YYYYMMDD

export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib

######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

echo "["`date +"%Y-%m-%d %T %z"`"]     ""R Analysis Start - "${1^^}" "$3"" >> ../../data/logs/"$3".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "R Analysis Start" "${1^^} $3"
LOC=`sed -nr "/^\["$2"\]/ { :l /^name[ ]*=/ { s/[^=]*=[ ]*//; p; q;}; n; b l;}" ../../magic_config.ini`
TZ=`sed -nr "/^\["$2"\]/ { :l /^tz[ ]*=/ { s/[^=]*=[ ]*//; p; q;}; n; b l;}" ../../magic_config.ini`


######################################
## R Analysis
######################################
cd ../stats
R -e "rmarkdown::render('"$1"_dashboard.Rmd', output_file = '"$1"_dashboard_"$2".html')" --args "$LOC" "$2" "$3" "'$TZ'"  >> ../../data/logs/"$3".log
rm my.inv
mv ens_dashboard*.html ../../
mv cfs_dashboard*.html ../../

######################################
## Clear files
######################################
cd $DIR
python3 storage_clean.py

echo "["`date +"%Y-%m-%d %T %z"`"]     ""R Analysis Done - "${1^^}" "$3"" >> ../../data/logs/"$3".log
test -f ../libs/notify_ssh.sh && ./../libs/notify_ssh.sh "R Analysis Done" "${1^^} $3"
echo "" >> ../../data/logs/"$3".log
echo "" >> ../../data/logs/"$3".log

test -f ../libs/publish_dashboards.sh && ../libs/publish_dashboards.sh
