# EigenD Community Release Notes Release - BETA 1

Download: [https://github.com/TheTechnobear/EigenD/releases](https://github.com/TheTechnobear/EigenD/releases)


# 1 – Introduction
This is a beta 1 for Apple Silicon only - other platforms will be released in future phases (soon)

# 2 - Changes 

Native Apple Silicon support
Improved installer
Lot of bug fixes


Major changes to underlying technology:
- Python 3.14
- Juce 8
- C++17
- SCons4 
- Improved build tools
- Dev docs
- New issue tracking at github.com

Breaking changes: 
- VST3 support only, due to licensing.

Lot's of other stuff I can't remember - lol

# 3.  Important notes


# 3.1 - File Locations

Directories used by EigenD, version is something like : 3.0.0-beta-1

## 3.1.1 - macOS

- **Application**: `/Applications/Eigenlabs/<VERSION>/` (apps: Workbench, Commander, Browser)
- **Binaries/Plugins**: `/Applications/Eigenlabs/<VERSION>/pi/` (bin, plugins, modules, resources)
- **Global Resources**: `/usr/local/pi/` (shared: ImpulseResponse, Loop, Soundfont, VST - preserved across versions)
- **User Data**: `~/Library/Eigenlabs/<VERSION>/` (setups, recordings, instruments, scripts - preserved on uninstall)

**Uninstall**:  `remove /Applications/Eigenlabs/<VERSION>`, remove global resources and user data manually

## 3.1.2 - Windows

- **Application**: `C:\Program Files\EigenLabs\release-<VERSION>\` (binaries, plugins, resources)
- **User Data**: `%USERPROFILE%\Documents\Eigenlabs\<VERSION>\` (setups, recordings, instruments, scripts - preserved on uninstall)
- **Start Menu**: `%ProgramData%\Microsoft\Windows\Start Menu\Programs\EigenLabs\<VERSION>\` (shortcuts)

**Uninstall** : use installer, user data manually.

## 3.1.3 - Linux

- **Application**: `/usr/local/pi/release-<VERSION>/` (binaries, plugins, resources)
- **User Data**: `~/.belcanto/<VERSION>/` (setups, recordings, instruments, scripts - preserved on uninstall)

**Uninstall** : using package manager ```sudo apt remove pi-eigend``` , user data manually.

# 3.2 Setup Upgrades
Setup upgrades are **always** between versions - e.g. 2.2.1 to 3.0.0, 3.0.0 to 3.0.1
there is no upgrade / migration of setups between beta versions ! 
if you need setup (etc) from one beta to another, you may copy setups, though 'officially' this is not supported.

# 3.4 Apple file location changes
I've moved binaries from /usr/local/pi/<release> to /Applications/Eigenlabs/<release>/pi.
This means you can uninstall a version , by simply deleting folder in Applications.

However, for now, to be backwards compatible, Ive left factory 'global resources' (see above) in /usr/local/pi
This is subject to change, as I dont like its 'hidden' nature.

# 3.5 Python changes
These are massive ! 
Its fixed to Python 3.14 which must be a default install from python.org, except Linux, use your package manager.
Installer will now check this and advise if necessary.


# 4. Support

## Important Note: 
I'm an open source developer doing this in my spare time, because Im enthusiasic these wonderful instruments.
please keep this in mind with your expectations.

I can be found on the community forum, come find me there.
if you have issues that shoud be your first point of contact to me, and the community.
Do NOT log users issues/support questions on Bugs / Issue tracker, I will likely just close.


- Eigenharp community forum : https://polyexpression.com

- Bugs / Issues :  https://github.com/TheTechnobear/EigenD/issues 

- My YouTube Channel : https://youtube.com/@thetechnobear 


# 5. Supporting this project
You can support this project in multiple way

a) Help others in the community
We can help each other to have a better experience, find new ways to enjoy the Eigenharps and EigenD.
join the community forum

b) Help with testing / feedback
Co-ordinated via polyexpression.com, 

c) Help with development 

d) Buy me a coffee at  ko-fi (https://ko-fi.com/thetechnobear)
I do this for the love of it, not monetary gain.
however, I do incur various expenses, things like hardware, software, subscriptions / services (e.g. github pro).
It's not much, and it's 'cross project' ( as I have many open source projects ) but a little can help.


