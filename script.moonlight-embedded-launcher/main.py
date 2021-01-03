# -*- coding: utf-8 -*-

import os
import subprocess
import xbmcgui, xbmc


def load_installed_games():
    try:
        result = subprocess.check_output("systemd-run ~/.kodi/addons/script.moonlight-embedded-launcher/bin/get_games.sh", shell=True)
        gamelist = result.splitlines()
        return gamelist[2,]
    except CalledProcessError as procError:
        msg = procError.output
        xbmcgui.Dialog().ok("Error during fetching installed Games", message)
        return None
    
gameList = load_installed_games()
if gameList == None:
    return
gameIdx = xbmcgui.Dialog.select("Choose your Game:",gamelist)
launchCommand = "systemd-run ~/.kodi/addons/script.moonlight-embedded-launcher/bin/launch_moonlight.sh " + gameList[gameIdx].split(" ", 1)
os.system(launchCommand)
