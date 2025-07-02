#! /bin/bash

# $1 : Model
# $2 : Run
# $3 : Day ago
# $4 : Type (dl / stats)
# $5 : Source (noaa / ecmwf)


######################################
## Get Dir from where script is executed and Date to set correct pathways
######################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR


str="$(ls ongoing)"
if [[ -z "${str}" ]]
then
    str2="10"
else
    str2="`echo "$str" | tail -n1`"
    let str2++
fi
echo "$DIR/$5_$4.sh $1 $2 $3" > "ongoing/$str2"
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
