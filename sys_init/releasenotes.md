# EigenD Community Release Notes Release : 2.2.0-community

Download: [https://github.com/TheTechnobear/EigenD/releases](https://github.com/TheTechnobear/EigenD/releases)



Important note: please read the installation notes

Included files
- releasenotes.pdf - release and installation notes (also included in all releases)
- EigenD-gpl-2.2.0-community-x86_64.pkg - macOS 64 bit. 
- EigenD-gpl-2.2.0-community-win32 - Windows 32 bit
- EigenD-gpl-2.2.0-community-arm.deb - Linux debian package for ARM 7 (e.g. PI) 
- EigenD-gpl-2.2.0-community-x86_64.deb - Linux debian package 64 bit. 
- linux_eigend.sh.txt - start script for linux, rename to linux_eigend.sh


# 1 – Introduction
This release is a community release of EigenD, originally forked from the Eigenlabs release.
It is distributed and maintained on a purely voluntary basis, with no commercial support, and as should be taken ‘as is’.
If you require a commercially supported product you are are directed to Eigenlabs for their releases (http://eigenlabs.com)

## Why use the community release?
The community release is still under active development, in particular it is being updated due to new OS releases, and I fix bugs where I encounter them,
long term I hope to get the software onto more current versions of the frameworks it uses.

major features of the community release over the eigenlabs stable release: - 
- Support for Mac OS X 10.13+, Intel 64bit and Apple Silicon (arm)
- Support for Mac OS 64 bit
- Support for Linux 64 bit
- Linux 
- New agents

Caveats:
The main caveat I have is, that whilst I compile and distribute for Windows, I do NOT actively use or test on it - so it should work (and I know musicians using t) , but no promises.

Support
I most actively monitor the google plus (G+) Eigenharp community, so please if you have questions post there:

https:/polyexpression.com

again, repeat this is volunteer basis for this build - its not the official support, which can only be found on the Eigenlabs forums (eigenlabs.com)

Enjoy
Mark (aka TheTechnobear)

# 2 – Changes for this release
- Upgraded Juce to 6.08
- Improved build
- Mac OS use system python 
- Improved release notes covering installation.

# 3 - Platform notes



## Windows
no changes

-------



## Mac OS

### Supported version
- Mac OS / Mac OSX 13+
- Intel 64 bit  (no 32 bit support)
- Apple Silicon 


### Limitations

- you can only host vsts of same binary format i.e. apple silicon, or intel 64 bit (not 32bit) 
- EigenBrowser and EigenCommander, currently not included
- convolver/cello not include (apple silcon only)
- resource package is no longer support, so no loops/samples are included (currently)



### Important note

- Runtime package is no longer needed - do NOT use
EigenD now uses python installed as part of the OS, not its own version
/System/Library/Frameworks/Python.framework/Versions/2.7/bin/python

 /usr/local/py/python and /Library/Frameworks/Python.framework were previously used, 
 and are no longer needed (but you can leave there)

- Resources package - is not longer used

-------



## Linux (64 bit)

sudo dpkg -i pi-eigend_2.1.7-community.deb use linux_eigenD.sh to run
you will need to ensure a few things:
- your user has ability to create real time threads... this is usually done by adding to the ‘audio group’ ,
- ensure your user has access to USB devices, as a hack you can do this using sudo chmod 666 /dev/bus/usb/*/* BUT the correct way is to create devices rules
$ sudo cp data/69-eigenharp.rules /etc/udev/rules.d/ $ sudo udevadm control --reload-rules
please note: Ive not double checked the rules, if you have an issue , please report on polyexpression.com 
setups are stored in `~/.Eigenlabs/2.2.0-community/Setups`

--------



## Linux (ARM)

Thanks to Kai Drange for contributing this.

### INSTALLING PI OS ONTO SDCARD USING WINDOWS
(note: this is similar for Mac OS)
Format SD card using SDFormatter (included in zip). Set FORMAT SIZE ADJUSTMENT (in options) to ON.
Install the included Win32DiskImager. Unzip the raspuntu image.
Burn the raspuntu image by running Win32DiskImager as Administrator (right click icon and select run as admin).
Copy "eigend.desktop", "linux_eigend.sh" and the eigenpi .deb file to a memory stick.

### CONFIGURING THE OS
On the Raspberry, insert the sd card, boot, and select user linaro, with linaro as password as well. You should see a graphical desktop at this point.

Note: for some reason my first sd card did not work. This OS would not start properly. The card was not faulty or anything, and some other OSes worked just fine. A recommended sd card was "Sandisk Extreme Pro 8GB", so I bought that instead and it worked as expected.

From this point on, I used xterm selected from the start menu as a terminal. So when I typed something, this is where I did so. Whenever I edited a text file I started that with admin rights from the terminal by typing "sudo leafpad".

If the desktop borders are outside your tv screen (mine were) open boot/ config.txt. Remove the "#" before the overscan_left 16, right, etc to uncomment those lines. Save and reboot by clicking bottom right, select log off, and then back at the user logon screen select Quit -> reboot.
To change keyboard layout, type "sudo dpkg-reconfigure keyboard-configuration" and go through the setup.
To autologin as linaro user, open /etc/lxdm/default.conf, uncomment the autologin line and set it to "autologin=linaro".

### INSTALLING EIGEND
Plug the memory stick into the Raspberry. You should get an error message you can ignore. To access the memory stick first create a new folder by typing "sudo mkdir /media/usb". Then mount it with "sudo mount /dev/sda1 /media/usb". This last line is worth remembering since you will need to to this again if you later want to mount your memory stick again. Your stick contents should now be available in /media/usb.

To install EigenPi, type "cd /media/usb" and then "sudo dpkg -i pi-eigend_2.2.0- community-raspberryPI2.deb". 

EigenD should now reside in /usr/pi/release-2.2.0- community

Copy the startup script linux_eigend.sh to the EigenD folder by typing 

"sudo cp / media/usb/linux_eigend.sh /usr/pi/release-2.1.7-community".

To make EigenD automatically run on startup, copy the eigend.desktop file to / etc/xdg/autostart in the same way.
Set some file access rights needed by EigenD by typing "sudo chmod 666 /dev/ bus/usb/*/*". 

I also typed 

"sudo chmod 755 /usr/pi/release-2.2.0-community/linux_eigend.sh", 

but I'm not sure if this is needed.
...and that should be it! The VST plugin scanning will hang, but still try to do it once so you won't be asked again. Cancel the big factory preset when it tries to load as it will crash. Select a small one as default instead.

User setups are stored at "/home/linaro/.Eigenlabs/2.2.0-community/Setups" 

so I just copied mine there after first saving a blank one. Not sure if the user presets folder was already there or was created first time I saved a user setup. The ".Eigenlabs" folder is hidden, but you can still see it in the file manager if you set "view hidden files" or something similar. Selected midi devices were remembered from my PC setup, btw, so my midi setup worked right out of the box.


