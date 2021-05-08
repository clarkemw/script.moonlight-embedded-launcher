# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from subprocess import CalledProcessError
import xbmcaddon
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
    
def launch(res,fps,bitrate,quitafter):
    gameList = load_installed_games()
    if gameList == None:
        return
    dialog = xbmcgui.Dialog()
    gameIdx = dialog.select("Choose your Game:", gameList)
    if gameIdx == -1:
        sys.exit()
    # We split at the first blank to get rid of the number in the beginning
    # We also make sure to put the game name in quotation marks to ensure it to be treated as one arg
    selectedGame = gameList[gameIdx].split(" ", 1)[1].replace("\n","")

    # Send quit command from moonlight after existing (helpful for non-steam sessions):
    quitflag = '-quitappafter' if quitafter == 'true' else ''

    launchCommand = 'systemd-run  bash ~/.kodi/addons/script.moonlight-embedded-launcher/bin/launch_moonlight.sh'
    args = ' "{}" "{}" "{}" "{}"'.format(res,fps,bitrate,selectedGame,quitflag)
    os.system(launchCommand + args)


addon = xbmcaddon.Addon(id='script.moonlight-embedded-launcher')  
while True:
    opt = xbmcgui.Dialog().contextmenu(['Play Game','Settings'])
    if opt == 0:
        res = addon.getSetting('resolution')
        fps = addon.getSetting('fps') if addon.getSetting('fps') != 'auto' else '-1'
        bitrate = addon.getSetting('bitrate') if addon.getSetting('bitrate') != 'auto' else '-1'
        quitafter = addon.getSetting('quitafter')
        launch(res,fps,bitrate,quitafter)
        sys.exit()
    elif opt == 1:
        addon.openSettings()
    else:
        sys.exit()    