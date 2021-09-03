#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Avahi functions to check for gamstream hosts etc
"""
from utils import subprocess_runner


def host_check():
    """
    Check if gamestream host is available on local network

    :return: boolean for host availability
    """
    check = subprocess_runner("avahi-browse -t _nvstream._tcp".split(" "), "host check")
    if check and "nvstream" in check:
        return True
    else:
        return False
