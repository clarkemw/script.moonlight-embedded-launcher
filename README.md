# moonlight-embedded-launcher
Docker container/Kodi launcher for running moonlight-embedded on LibreELEC/Raspberry Pi systems.

## Background:
This Docker container/Kodi addon-on was developed to enable moonlight game streaming on LibreELEC systems.  Since LibreELEC is a "just enough" distribution dependencies for moonlight-embedded are missing, requiring the use of a Docker container to run.  A simple add-on lets you launch moonlight from within Kodi and stream games from your PC to your LibreELEC devicee.
More info on moonlight-embedded can be found here:
https://github.com/irtimmer/moonlight-embedded

## Prerequisites:
- Raspberry Pi device with LibreELEC installed, connected to local network via ethernet (preferred) or wifi
- Gaming PC with Steam and Nvidia GeForce Experience installed, connected to local network via ethernet (preferred) or wifi
- Basic familiarity with ssh and terminal for installation

## Instructions:
These instructions assume that your gaming PC  is connected to the same local network as the LibreELEC device.
1. Enable Nvidia Gamestream on your gaming PC
```
GeForce Experience/Settings/Shield/Gamestream (move slider to right)
```
2. Enable Avahi in LibreELEC
```
Kodi/Add-ons/LibreELEC Configuration/Services/Enable Avahi
```
3. Enable Docker in LibreELEC
```
Kodi/Add-ons/Install from repository/LibreELEC Add-ons/Services/Docker
```
4. SSH into your LibreELEC device, download/extract the latest release of this repository to your LibreELEC device and run install.sh
```sh
wget /link/to/thisrepo
unzip repo.zip
cd moonlight-embedded-launcher
bash ./install.sh
```
5. The installer script will guide you through the process. The only user interaction required is during the pairing process. The LibreELEC terminal will give you a 4 digit code, and you will see a pop-up on your gaming PC to enter the code.
![LibreELEC terminal code](libreelec_code.png)
![Gamestream host pop-up](gamestream_prompt.png)
6. Install the launcher add-on from the script.moonlight.launcher.zip file
```
Kodi/Add-ons/Install from zip file/Select script.moonlight.launcher.zip
```
