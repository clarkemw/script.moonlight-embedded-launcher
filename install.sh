#!/bin/bash
# Installer script for moonlight-embedded docker image on LibreELEC systems

# Check for dependencies: docker, avahi, Dockerfile.armhf.raspbian and a valid gamestream host
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker could not be found...exiting"
    echo "Please install under Kodi/Add-ons/Install from repository/LibreELEC Add-ons/Services/Docker"
    exit 1
fi

STATUS="$(systemctl is-active avahi-daemon.service)"
if [ "${STATUS}" = "active" ]; then
    if ! avahi-browse -t _nvstream._tcp | grep -q 'nvstream'; then
        echo "WARNING: Nvidia gamestream host could not be found on local network..."
        echo "Automatic pairing is not possible. Manual pairing will be required prior to use."
        echo "Please turn on host and enable via GeForce Experience/Settings/Shield/Gamestream slider."
        autopair=false
    else
        autopair=true   
    fi
else
    echo "ERROR: Avahi is not running...exiting"
    echo "Please enable under Kodi/Add-ons/LibreELEC Configuration/Services/Enable Avahi"  
    exit 1  
fi

if [ ! -f Dockerfile.armhf.raspbian ]; then
    echo "ERROR: Dockerfile not found in current directory...exiting"
    exit 1
fi

# Generate volume and container:
if ! docker volume create --name moonlight-home; then
    echo "ERROR: unable to create docker volume for persistent moonlight data...exiting"
    exit 1
fi    

echo "Beginning docker build...this may take a few minutes..."
if ! docker build -t moonlight - < Dockerfile.armhf.raspbian; then
    echo "ERROR: unable to build docker container...exiting"
    exit 1
fi

# Automatic pairing if avahi-browse was able to find gamestream host:
if [ $autopair = true ]; then
    if ! docker run -it -v moonlight-home:/home/moonlight-user \
        -v /var/run/dbus:/var/run/dbus --device /dev/vchiq:/dev/vchiq \
        moonlight pair; then
        echo "WARNING: unable to automatically pair to gamestream host"
    fi
fi

# Create kodi add-on zip:
zip -r script.moonlight-embedded-launcher.zip script.moonlight-embedded-launcher

echo ""
echo "Installation complete!"
echo "Please install launcher add-on in Kodi via zip file using: script.moonlight-embedded-launcher.zip"
