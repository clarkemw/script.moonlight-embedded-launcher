#!/bin/bash
. /etc/profile

# Get optional arguments/flags (should be specified before standard arguments)
optstring=':qi:'
while getopts ${optstring} arg; do
  case ${arg} in
  i)
     hostip=${OPTARG};;
  q)
     quitflag='-quitappafter';;
  esac
done
shift $((OPTIND-1))

# Get standard stream parameters
if [ -z "$1" ]; then
    echo "Error, please specify resolution (720,1080 or 4k)...exiting"
    exit 1
else
    res="$1"
fi
if [ -z "$2" ]; then
    echo "Error, please specify frame rate (30,60)...exiting"
    exit 1
else
    fps="$2"
fi
if [ -z "$3" ]; then
    echo "Error, please specify bitrate...exiting"
    exit 1
else
    bitrate="$3"
fi
if [ -z "$4" ]; then
    echo "Error, please specify game...exiting"
    exit 1
else
    game="$4"
fi

systemctl stop kodi # Must close kodi for proper video display

# Launch docker, adjusted to just used input variables 
docker run --rm --name moonlight -t -v moonlight-home:/home/moonlight-user \
-v /var/run/dbus:/var/run/dbus --device /dev/vchiq --device /dev/input \
clarkemw/moonlight-embedded-raspbian stream -"$res" -fps "$fps" -bitrate "$bitrate" $quitflag -app "$game" $hostip

docker wait moonlight

systemctl start kodi # Reopen kodi


