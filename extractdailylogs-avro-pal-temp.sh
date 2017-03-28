#!/bin/bash

#
# This script extracts the hourly logs from AdGear GIVEME API and puts them in a daily log file.
# https://adgear.atlassian.net/wiki/display/adgear/Giveme+API
#

if [ $# -lt 3 ]
  then
    echo "Missing arguments. Sample usage : extractdailylogs.sh 2015-10-31 2015-11-22 delivery|attribution"
    exit
fi

FARM="production"
TYPE=$3
PATHNAME="/home/adgear/logs/$FARM/$TYPE"
CURRENT_DATE=$1

datediff() {
    d1=$(/bin/date -d "$1" +%s)
    d2=$(/bin/date -d "$2" +%s)
    echo $(( (d1 - d2) / 86400 ))
}

DAYS=$(datediff $2 $1)
let DAYS=DAYS+1

# For each day in the range...
while [  $DAYS -ne 0 ]; do

  echo
  echo "Exporting '$TYPE' logs for $CURRENT_DATE..."
  echo

  # For each hour of the day...
  for ((hour=0;hour<24;hour++))
  do
    printf -v paddedhour "%02d" $hour;
    EXPORTED_HOUR="$CURRENT_DATE-$paddedhour";
    echo "Exporting logs for hour $EXPORTED_HOUR to file $LOG_FILE";

      LOG_FILE="$PATHNAME/$EXPORTED_HOUR.avro"

#      if [ -f "$LOG_FILE" ] ; then
#        echo "File $LOG_FILE exists, removing!"
#        /bin/rm -f $LOG_FILE
#      fi

#    /usr/bin/ssh giveme@giveme.adgear.com events trader $FARM $TYPE avro $EXPORTED_HOUR >> $LOG_FILE
#    gsutil cp $LOG_FILE gs://adgear-raw/AdGear_${TYPE^}_$(basename $LOG_FILE)
    bq ls Adgear_${TYPE^}_logs | grep $(sed 's/-//g' <(echo $CURRENT_DATE)) >/dev/null
    if $(test $hour -eq 0 -a $? -eq 0); then
        echo The table already exists. This means we are in a bad state.
        echo Delete then run me again
        exit
    fi
    echo bq load --source_format=AVRO AdGear_${TYPE^}_Raw.AdGear_${TYPE^}_$(sed 's/-//g' <(echo $CURRENT_DATE)) gs://adgear-raw/AdGear_${TYPE^}_$(basename $LOG_FILE)
    bq load --source_format=AVRO AdGear_${TYPE^}_Raw.AdGear_${TYPE^}_$(sed 's/-//g' <(echo $CURRENT_DATE)) gs://adgear-raw/AdGear_${TYPE^}_$(basename $LOG_FILE)
  done

  CURRENT_DATE=`/bin/date '+%Y-%m-%d' -d "$CURRENT_DATE+1 days"`
  let DAYS=DAYS-1

done

echo
echo "Log file extract COMPLETED"
echo
