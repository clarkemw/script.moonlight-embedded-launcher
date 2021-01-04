#!/bin/bash
docker run --rm -t --name fetch_moonlight_games -v moonlight-home:/home/moonlight-user \
-v /var/run/dbus:/var/run/dbus moonlight list