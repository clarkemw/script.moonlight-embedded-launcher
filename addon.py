# -*- coding: utf-8 -*-

import os
import sys
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon(id="script.moonlight-embedded-launcher")
sys.path.append(os.path.join(addon.getAddonInfo("path"), "resources", "lib"))
import moonlight

while True:
    if addon.getSetting("firstrun") == "true":
        opt = xbmcgui.Dialog().yesno("Installation", 
        "First launch detected. Do you want to run the required script to configure moonlight?")
        if opt:
            status = moonlight.install()
            if status:
                addon.setSetting(id="firstrun", value="false")
                moonlight.pair()
            else:
                continue    
        else:
            xbmcgui.Dialog().ok("Installation",
                                "Skipping installation...press OK to exit")
            sys.exit()

    opt = xbmcgui.Dialog().contextmenu(["Play Game", "Configure"])
    hostip = addon.getSetting("hostip") if addon.getSetting("autodetect") == "false" else ""
    if opt == 0:
        res = addon.getSetting("resolution")
        fps = addon.getSetting("fps") # Removed auto fps, appears to be broken
        bitrate = (addon.getSetting("bitrate")
                   if addon.getSetting("bitrate") != "auto" else "-1")
        quitafter = addon.getSetting("quitafter")
        usercustom = addon.getSetting("usercustom")
        moonlight.launch(res, fps, bitrate, quitafter, hostip, usercustom)
        sys.exit()
    elif opt == 1:
        opt2 = xbmcgui.Dialog().contextmenu(
            ["Settings", "Pair", "Docker Update"])
        if opt2 == 0:
            addon.openSettings()
        elif opt2 == 1:
            moonlight.pair(hostip)
        elif opt2 == 2:
            moonlight.update_moonlight()
    else:
        sys.exit()
