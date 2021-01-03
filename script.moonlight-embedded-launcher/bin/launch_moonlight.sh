#!/bin/bash
. /etc/profile

systemctl stop kodi # Must close kodi for proper video display

docker run -t -v moonlight-home:/home/moonlight-user \
-v /var/run/dbus:/var/run/dbus --device /dev/vchiq --device /dev/input \
moonlight stream -1080 -fps 60

docker wait moonlight

systemctl start kodi # Reopen kodi


