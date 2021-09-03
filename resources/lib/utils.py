#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility functions for subprocesses and docker containers
"""
import fcntl
import os
import subprocess
import time
import xbmcgui


def subprocess_runner(cmd, desc, wait=True, blockio=True):
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
            xbmcgui.Dialog().ok("Error during {desc}".format(desc=desc), msg)
            return None
    else:
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        if not blockio:
            fd = proc.stdout.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    return proc


def stop_old_container(container):
    """
    Check if docker container is running and stop if necessary

    :param container: name of docker container to check
    """
    check = subprocess_runner("docker ps".split(" "), "container check")
    if check and container in check:
        stop = "docker container stop {container}".format(container=container)
        subprocess_runner(stop.split(" "), "stop container")


def wait_or_cancel(proc, title, message):
    """
    Display status dialog while process is running and allow user to cancel

    :param proc: subprocess object
    :param title: title for status dialog
    :param message: message for status dialog
    :return: (process exit code, stdout output or None)
    """
    pDialog = xbmcgui.DialogProgress()
    pDialog.create(title, "")
    while proc and proc.poll() is None and not pDialog.iscanceled():
        pDialog.update(50, message)
    try:
        if not pDialog.iscanceled():
            msg = proc.communicate()[0]
            exitcode = proc.returncode
            if exitcode == 0:
                stdout = msg
                pDialog.update(100, "Complete!")
                time.sleep(3)
            else:
                xbmcgui.Dialog().ok(
                    "Error during {desc}".format(desc=title.lower()), msg)
                stdout = msg
        else:
            proc.terminate()
            stdout = None
            exitcode = 1
    except:
        pass
    pDialog.close()
    return (exitcode, stdout)
