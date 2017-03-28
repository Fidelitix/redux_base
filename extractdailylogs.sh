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
PATH="/home/adgear/logs/$FARM/$TYPE"
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

  LOG_FILE="$PATH/$CURRENT_DATE.jsonlog"

  if [ -f "$LOG_FILE" ] ; then
    echo "File $LOG_FILE exists, removing!"
    /bin/rm -f $LOG_FILE
  fi

  # For each hour of the day...
  for ((hour=0;hour<24;hour++))
  do
    printf -v paddedhour "%02d" $hour;
    EXPORTED_HOUR="$CURRENT_DATE-$paddedhour";
    echo "Exporting logs for hour $EXPORTED_HOUR to file $LOG_FILE";
#    /usr/bin/ssh giveme@giveme.adgear.com events trader $FARM $TYPE json $EXPORTED_HOUR >> $LOG_FILE
    /usr/bin/ssh giveme@giveme.adgear.com events trader $FARM $TYPE json_legacy $EXPORTED_HOUR >> $LOG_FILE
  done

  CURRENT_DATE=`/bin/date '+%Y-%m-%d' -d "$CURRENT_DATE+1 days"`
  let DAYS=DAYS-1

done

echo
echo "Log file extract COMPLETED"
echo
