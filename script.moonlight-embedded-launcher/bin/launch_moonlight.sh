#!/bin/bash
. /etc/profile

systemctl stop kodi # Must close kodi for proper video display

### The Env Variable MOONLIGHT_GAME ist set from the launcher add-on.
### TODO: Add also ENV_VARS to pass resolution and fps from the Add-On Config
docker run --rm --name moonlight -t -v moonlight-home:/home/moonlight-user \
-v /var/run/dbus:/var/run/dbus --device /dev/vchiq --device /dev/input \
moonlight stream -1080 -fps 60 -app $MOONLIGHT_GAME

docker wait moonlight

systemctl start kodi # Reopen kodi


