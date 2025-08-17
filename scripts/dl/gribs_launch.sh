#! /bin/bash

## IF LAUNCH FOR DL type
# $1 : Model (cfs / gefs / gem / fnmoc / ecmwf)
# $2 : Run (00 / 06 / 12 / 18) depending on Model
# $3 : Day ago (integer)
# $4 : Type (dl)
# $5 : Source (noaa / ecmwf)

## IF LAUNCH FOR STATS type
# $1 : Set (ens / cfs)
# $2 : Profile (as set in magic_config.ini)
# $3 : Day ago (integer)
# $4 : Type (stats)
# $5 : Source (noaa)

######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

DATE=`date +%Y%m%d -d $3" day ago"`

str="$(ls ongoing)"
if [[ -z "${str}" ]]
then
    str2="10"
else
    str2="`echo "$str" | tail -n1`"
    let str2++
fi
echo "$DIR/$5_$4.sh $1 $2 $DATE" > "ongoing/$str2"
chmod +x "ongoing/$str2"

if [[ $(cat lock.txt) == "FREE" ]]
then
echo "BUSY" > lock.txt

str="$(ls ongoing)"
while [ ! -z "${str}" ]
do
    str2="`echo "$str" | head -n1`"
    ./ongoing/$str2
    rm ongoing/$str2
    str="$(ls ongoing)"
done

echo "FREE" > lock.txt
fi
