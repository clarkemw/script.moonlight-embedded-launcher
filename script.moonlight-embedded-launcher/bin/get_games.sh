#!/bin/bash
docker run --rm -t -v moonlight-home:/home/moonlight-user \
-v /var/run/dbus:/var/run/dbus moonlight list