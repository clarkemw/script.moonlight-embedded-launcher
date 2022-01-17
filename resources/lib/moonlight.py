#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Various functions to execute moonlight-embedded
"""
import os
import re
import sys
import time
import xbmc
import xbmcgui
from avahi import host_check
from utils import stop_old_container, subprocess_runner, wait_or_cancel


def install():
    """
    Executes the installer script to configure/download the moonlight-embedded docker container
    :return: boolean for success of installation
    """
    script = os.path.join(os.path.dirname(__file__), "bin",
                          "install_moonlight.sh")
    cmd = "bash {script}".format(script=script)                      
    proc = subprocess_runner(cmd.split(' '), 'install', wait=False)
    (status,_) = wait_or_cancel(proc, 'Installation',
                         'Running installation...this may take a few minutes')
    if status == 0:
        return True
    else:
        return False


def launch(res, fps, bitrate, quitafter, hostip, usercustom):
    """
    Launches moonlight-embedded as an external process and kills Kodi so display is available
    Kodi will be automatically relaunched after moonlight-embedded exits

    :param res: video resolution of streaming session
    :param fps: frames per second of streaming session
    :param bitrate: bitrate of streaming session
    :param quitafter: quit flag helpful for desktop sessions
    :param hostip: gamestream host ip (blank if using autodetect)
    :param usercustom: any custom flags the user wants to pass to moonlight
    """

    gameList = load_installed_games(hostip)
    if gameList == None:
        return
    dialog = xbmcgui.Dialog()
    gameIdx = dialog.select("Choose your Game:", gameList)
    if gameIdx == -1:
        sys.exit()
    # We split at the first blank to get rid of the number in the beginning
    # We also make sure to put the game name in quotation marks to ensure it to be treated as one arg
    selectedGame = gameList[gameIdx].split(" ", 1)[1].replace("\n", "")
    xbmc.log(
        "Streaming {} with moonlight-embedded, Kodi will now exit.".format(
            selectedGame),
        xbmc.LOGINFO,
    )
    # Send quit command from moonlight after existing (helpful for non-steam sessions):
    quitflag = "-q" if quitafter == "true" else ""
    # Custom host ip (moonlight will auto-detect if not specified)
    hostipflag = "-i {}".format(hostip) if hostip else "" 
    # Custom user settings:
    customflag = "-c \"{}\"".format(usercustom) if usercustom else ""
    script = os.path.join(os.path.dirname(__file__), "bin",
                          "launch_moonlight.sh")
    launchCommand = "systemd-run bash {}".format(script)
    # pass optional flag arguments first because bash getopts is picky
    args = '{} {} {} "{}" "{}" "{}" "{}"'.format(hostipflag, quitflag, customflag, res, fps, bitrate, 
                                               selectedGame).strip()
    os.system(launchCommand + " " + args)


def load_installed_games(hostip):
    """
    request available games from the Gamestream host

    :return: list of available games
    """
    proc = run_moonlight("list", hostip, wait=False)
    if proc:
        (status, result) = wait_or_cancel(proc, "List",
                                          "Getting available games...")
        if status == 0 and result:
            ## We expect the list command to follow the pattern below:
            # =========================================
            # Searching for server...
            # Connect to 192.168.178.166...
            # 1. MarioKart8
            # 2. Dolphin
            # 3. Steam
            # =========================================
            # A return code=0 signals that we were successful in obtaining the list.
            gamelist = [game for game in result.splitlines() if re.search('^\d+\.',game)]
            if gamelist:
                return gamelist
            else:
                xbmcgui.Dialog().ok("Error during fetching installed games",
                                    result)


def pair(hostip):
    """
    Generates pairing credentials with a gamestream host
    """
    opt = xbmcgui.Dialog().yesno(
        "Pairing", "Do you want to pair with a Gamestream host?")
    if opt:
        pDialog = xbmcgui.DialogProgress()
        proc = run_moonlight("pair", hostip, wait=False, blockio=False)
        stdout = ""
        codeFlag = False
        pDialog.create("Pairing", "Launching pairing...")
        while proc and proc.poll() is None and not pDialog.iscanceled():
            try:
                stdout += proc.stdout.read()
            except:
                pass
            if not codeFlag:
                code = re.search(
                    r"Please enter the following PIN on the target PC: (\d+)",
                    stdout)
                if code:
                    codeFlag = True
                    code = code.groups()[0]
                    pDialog.update(
                        50,
                        "Please enter authentication code {code} on Gamestream host"
                        .format(code=code),
                    )
        if not pDialog.iscanceled() and proc.returncode == 0:
            pDialog.update(100, "Complete!")
            time.sleep(3)
        else:
            try:
                proc.terminate()
            except:
                pass
        pDialog.close()
        if re.search(r"Failed to pair to server: Already paired", stdout):
            opt = xbmcgui.Dialog().ok(
                "Pairing",
                "Gamestream credentials already exist for this host.")


def run_moonlight(mode, hostip, wait=True, blockio=True):
    """
    execute moonlight in a local subprocess (won't work for streaming)

    :param mode: moonlight execution mode (pair/unpair/list etc)
    :param wait: wait for process to complete
    :param block: allow reading of stdout to block
    :return: subprocess object
    """
    stop_old_container("moonlight_{mode}".format(mode=mode))
    if not hostip and not host_check():
        xbmcgui.Dialog().ok(
            "Error",
            "No Gamestream host auto-detected on local network. Please connect it, enable Gamestream and retry.",
        )
        return None
    cmd = (
        "docker run --rm -t --name moonlight_{mode}"
        " -v moonlight-home:/home/moonlight-user -v /var/run/dbus:/var/run/dbus"
        " clarkemw/moonlight-embedded-raspbian {mode} {hostip}").format(mode=mode, hostip=hostip)
    return subprocess_runner(cmd.rstrip().split(" "), "moonlight " + mode, wait,
                             blockio)

def update_moonlight():
    """
    performs a docker pull to update the moonlight-embedded container
    """
    opt = xbmcgui.Dialog().yesno(
        "Update", "Do you want to update the moonlight-embedded docker container?")
    if opt:   
        cmd = "docker pull clarkemw/moonlight-embedded-raspbian"
        proc = subprocess_runner(cmd.split(" "), "docker update", wait=False)
        wait_or_cancel(proc, "Update",
                       "Running docker update...this may take a few minutes")
