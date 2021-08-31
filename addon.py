# -*- coding: utf-8 -*-

import fcntl
import os
import re
import sys
import subprocess
import time
import xbmcaddon
import xbmcgui


def subprocess_runner(cmd,desc,wait=True,blockio=True):
    """
    execute command in a local subprocess

    :param cmd: command to execute in list format
    :param desc: description of command being run (for error messages)
    :param wait: wait for process to complete
    :param block: allow reading of stdout to block
    :return: subprocess object or None
    """ 
    if wait:
        try: 
            proc = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as procError:
            msg = procError.output
            xbmcgui.Dialog().ok('Error during {desc}'.format(desc=desc),msg)
            return None
    else:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT)
        if not blockio:
            fd = proc.stdout.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)                        
    return proc


def wait_or_cancel(proc,title,message):
        """
        Display status dialog while process is running and allow user to cancel

        :param proc: subprocess object
        :param title: title for status dialog
        :param message: message for status dialog
        :return: stdout output or None
        """
        pDialog = xbmcgui.DialogProgress()
        pDialog.create(title,'')
        while proc and proc.poll() is None and not pDialog.iscanceled():
            pDialog.update(50,message)   
        try:
            if not pDialog.iscanceled():
                msg = proc.communicate()[0]
                if proc.returncode == 0:
                    stdout = msg
                    pDialog.update(100,'Complete!')
                    time.sleep(3)
                else:
                    xbmcgui.Dialog().ok('Error during {desc}'.format(desc=title.lower()),msg)
                    return None
            else:    
                proc.terminate()
                stdout = None
        except: 
            pass
        pDialog.close() 
        return stdout


def enable_avahi():
    """
    Enables avahi daemon if it is not running:
    """
    pass

def host_check():
    """
    Check if gamestream host is available on local network

    :return: boolean for host availability 
    """
    check = subprocess_runner('avahi-browse -t _nvstream._tcp'.split(' '), 'host check')
    if check and 'nvstream' in check:
        return True
    else:
        return False   


def stop_old_container(container):
    """
    Check if docker container is running and stop if necessary

    :param container: name of docker container to check
    """
    check = subprocess_runner('docker ps'.split(' '),'container check')
    if check and container in check:
        stop = 'docker container stop {container}'.format(container=container)
        subprocess_runner(stop.split(' '),'stop container')
        

def run_moonlight(mode,wait=True,blockio=True):
    """
    execute moonlight in a local subprocess (won't work for streaming)

    :param mode: moonlight execution mode (pair/unpair/list etc)
    :param wait: wait for process to complete
    :param block: allow reading of stdout to block
    :return: subprocess object
    """ 
    stop_old_container('moonlight_{mode}'.format(mode=mode))
    if not host_check():
        xbmcgui.Dialog().ok('Error', 'No Gamestream host detected on local network. Please connect it, enable Gamestream and retry.')           
        return None
    cmd = ('docker run --rm -t --name moonlight_{mode}'
           ' -v moonlight-home:/home/moonlight-user -v /var/run/dbus:/var/run/dbus'
           ' clarkemw/moonlight-embedded-raspbian {mode}').format(mode=mode)
    return subprocess_runner(cmd.split(' '), 'moonlight ' + mode, wait, blockio)
    

def load_installed_games():
    """
    request available games from the Gamestream host

    :return: list of available games
    """     
    proc = run_moonlight('list',wait=False)
    if proc:
        result = wait_or_cancel(proc,'List','Getting available games...')
        if result:
            gamelist = result.splitlines()
            ## We expect the list command to follow the pattern below:
            #=========================================
            # Searching for server...
            # Connect to 192.168.178.166...
            # 1. MarioKart8
            # 2. Dolphin
            # 3. Steam
            # =========================================
            # A return code=0 signals that we were successful in obtaining the list. 
            # We omit the first 2 lines as they are just indicating to which PC we 
            # connected to.
            if len(gamelist) > 2:
                return gamelist[2:]
            else:
                xbmcgui.Dialog().ok("Error during fetching installed games", result)       


def launch(res,fps,bitrate,quitafter):
    """
    Launches moonlight-embedded as an external process and kills Kodi so display is available
    Kodi will be automatically relaunched after moonlight-embedded exits

    :param res: video resolution of streaming session
    :param fps: frames per second of streaming session
    :param bitrate: bitrate of streaming session
    :param quitafter: quit flag helpful for desktop sessions
    """
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
    print(selectedGame)
    # Send quit command from moonlight after existing (helpful for non-steam sessions):
    quitflag = '-quitappafter' if quitafter == 'true' else ''

    launchCommand = 'systemd-run  \
    bash ~/.kodi/addons/script.moonlight-embedded-launcher/bin/launch_moonlight.sh'
    args = ' "{}" "{}" "{}" "{}"'.format(res,fps,bitrate,selectedGame,quitflag)
    os.system(launchCommand + args)


def pair():
    """
    Generates pairing credentials with a gamestream host
    """
    opt = xbmcgui.Dialog().yesno('Pairing',
                                 'Do you want to pair with a Gamestream host?')
    if opt:
        pDialog = xbmcgui.DialogProgress()
        proc = run_moonlight('pair',wait=False,blockio=False)
        stdout = ''
        codeFlag = False
        pDialog.create('Pairing','Launching pairing...')
        while proc and proc.poll() is None and not pDialog.iscanceled():
            try:
                stdout += proc.stdout.read()
            except:
                pass
            if not codeFlag:
                code = re.search(r'Please enter the following PIN on the target PC: (\d+)', stdout)
                if code:
                    codeFlag = True
                    code = code.groups()[0]
                    pDialog.update(50,'Please enter authentication code {code} on Gamestream host'.format(code=code))
        if not pDialog.iscanceled() and proc.returncode == 0:
            pDialog.update(100,'Complete!')
            time.sleep(3)
        else:
            try:
                proc.terminate()
            except: 
                pass
        pDialog.close()   
        if re.search(r'Failed to pair to server: Already paired',stdout):
            opt = xbmcgui.Dialog().ok('Pairing','Gamestream credentials already exist for this host.')
            

def update_container():
    """
    Performs a docker pull to update moonlight container to the latest source
    """
    opt = xbmcgui.Dialog().yesno('Update','Do you want update the moonlight-embedded Docker container?')
    if opt:
        proc = subprocess_runner('docker pull clarkemw/moonlight-embedded-raspbian'.split(' '),'docker update',wait=False)
        wait_or_cancel(proc,'Update','Updating Docker image...this may take a few minutes...')


addon = xbmcaddon.Addon(id='script.moonlight-embedded-launcher')  
while True:
    opt = xbmcgui.Dialog().contextmenu(['Play Game','Configure'])
    if opt == 0:
        res = addon.getSetting('resolution')
        fps = addon.getSetting('fps') if addon.getSetting('fps') != 'auto' else '-1'
        bitrate = addon.getSetting('bitrate') if addon.getSetting('bitrate') != 'auto' else '-1'
        quitafter = addon.getSetting('quitafter')
        launch(res,fps,bitrate,quitafter)
        sys.exit()  
    elif opt == 1: 
        opt2 = xbmcgui.Dialog().contextmenu(['Settings','Pair','Docker Update'])
        if opt2 == 0:
            addon.openSettings()
        elif opt2 == 1:
            pair()    
        elif opt2 == 2:
            update_container()   
    else:
        sys.exit()    