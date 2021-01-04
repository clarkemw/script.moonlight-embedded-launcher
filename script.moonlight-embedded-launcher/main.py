# -*- coding: utf-8 -*-

import os
import subprocess
from subprocess import CalledProcessError
import xbmcgui


def load_installed_games():
    try:
        result = subprocess.check_output("~/.kodi/addons/script.moonlight-embedded-launcher/bin/get_games.sh", shell=True)
        gamelist = result.splitlines()
        ## We excpect the list command to following the pattern below:
        #=========================================
        # Searching for server...
        # Connect to 192.168.178.166...
        # 1. MarioKart8
        # 2. Dolphin
        # 3. Steam
        # =========================================
        # A return code=0 signals that we were sucessful in obtaining the list. We omit the first 2 lines
        # as they are just indicating to which PC we connected to.
        if len(gamelist) > 2:
            return gamelist[2:]
        else:
            xbmcgui.Dialog().ok("Error during fetching installed Games", result)
        return gamelist
    except CalledProcessError as procError:
        msg = procError.output
        xbmcgui.Dialog().ok("Error during fetching installed Games", msg)
        return None
    
def launch():
    gameList = load_installed_games()
    if gameList == None:
        return
    dialog = xbmcgui.Dialog()
    gameIdx = dialog.select("Choose your Game:", gameList)
    # We split at the first blank to get rid of the number in the beginning
    # We also make sure to put the game name in quotation marks to ensure it to be treated as one arg
    selectedGame = gameList[gameIdx].split(" ", 1)[1].replace("\n","")
    xbmcgui.Dialog().ok("Starting...", "Lauching " + selectedGame)
    
    launchCommand = 'systemd-run ' + getEnvArgsForSystemD(selectedGame) + ' bash ~/.kodi/addons/script.moonlight-embedded-launcher/bin/launch_moonlight.sh'
    os.system(launchCommand)

def getEnvArgsForSystemD(selectedGame):
    envVars = []
    for item, value in os.environ.items():
        envVars.append('-E "' + item + '=' + value + '"')
    envVars.append('-E "MOONLIGHT_GAME=' + selectedGame + '"') 
    return " ".join(envVars)

launch()