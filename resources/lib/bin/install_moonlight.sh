#!/bin/bash
# Installer script for moonlight-embedded docker image on LibreELEC systems

# Check for dependencies: docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker could not be found...exiting"
    echo "Please install under Kodi/Add-ons/Install from repository/LibreELEC Add-ons/Services/Docker"
    exit 1
fi

# Check for dependencies: avahi
STATUS="$(systemctl is-active avahi-daemon.service)"
if [ ! "${STATUS}" = "active" ]; then
    if [ -f /storage/.cache/services/avahi.conf.disabled ]; then
        # Enable steps from: https://forum.libreelec.tv/thread/24375-enable-avahi-zeroconf-programmatically/
        rm -f /storage/.cache/services/avahi.conf.disabled
        touch /storage/.cache/services/avahi.conf
        systemctl restart avahi-daemon.service
    else
        echo "ERROR: Could not enable avahi daemon...exiting"
    fi    
fi

# Generate volume and download container:
if ! docker volume create --name moonlight-home; then
    echo "ERROR: unable to create docker volume for persistent moonlight data...exiting"
    exit 1
fi    

echo "Downloading...this may take a few minutes..."
if ! docker pull clarkemw/moonlight-embedded-raspbian; then
    echo "ERROR: unable to pull docker container...exiting"
    exit 1
fi

echo ""
echo "SUCCESS: Installation complete!"
exit 0