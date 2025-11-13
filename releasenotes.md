# EigenD Community Release Notes Release - BETA 1

Download: [https://github.com/TheTechnobear/EigenD/releases](https://github.com/TheTechnobear/EigenD/releases)


# 1 – Introduction
This is a beta 1 for Apple Silicon only - other platforms will be released on 

# 2.  Important notes

# 2.1 Setup Upgrades
Setup upgrades are **always** between versions - e.g. 2.2.1 to 3.0.0, 3.0.0 to 3.0.1
there is no upgrade / migration of setups between beta versions ! 
if you need setup (etc) from one beta to another, you may copy setups, though 'officially' this is not supported.


# 2.2 - File Locations

version is something like : 3.0.0-beta-1

## 2.2.1 - macOS

- **Application**: `/Applications/Eigenlabs/<VERSION>/` (apps: Workbench, Commander, Browser)
- **Binaries/Plugins**: `/Applications/Eigenlabs/<VERSION>/pi/` (bin, plugins, modules, resources)
- **Global Resources**: `/usr/local/pi/` (shared: ImpulseResponse, Loop, Soundfont, VST - preserved across versions)
- **User Data**: `~/Library/Eigenlabs/<VERSION>/` (setups, recordings, instruments, scripts - preserved on uninstall)

**Uninstall**: 
```bash
# Remove version-specific files
sudo rm -rf /Applications/Eigenlabs/<VERSION>

# Optionally remove user data for this version
rm -rf ~/Library/Eigenlabs/<VERSION>

# Global resources in /usr/local/pi/ are shared across versions - keep unless removing all EigenD versions
```

## 2.2.2 - Windows

- **Application**: `C:\Program Files\EigenLabs\release-<VERSION>\` (binaries, plugins, resources)
- **User Data**: `%USERPROFILE%\Documents\Eigenlabs\<VERSION>\` (setups, recordings, instruments, scripts - preserved on uninstall)
- **Start Menu**: `%ProgramData%\Microsoft\Windows\Start Menu\Programs\EigenLabs\<VERSION>\` (shortcuts)

**Uninstall** : use installer, user data manually.

## 2.2.3 - Linux

- **Application**: `/usr/local/pi/release-<VERSION>/` (binaries, plugins, resources)
- **User Data**: `~/.belcanto/<VERSION>/` (setups, recordings, instruments, scripts - preserved on uninstall)

**Uninstall** : using package manager ```sudo apt remove pi-eigend``` , user data manually.

# 4. Support

## Important Note: 
I'm an open source developer doing this in my spare time, because Im enthusiasic these wonderful instruments.
please keep this in mind with your expectations.

I can be found on the community forum, come find me there.
if you have issues that shoud be your first point of contact to me, and the community.
Do NOT log users issues/support questions on Bugs / Issue tracker, I will likely just close.


- Forum for Eigenharp community : https://polyexpression.com

- Bugs / Issues :  https://github.com/TheTechnobear/EigenD/issues 

- My YouTube Channel : https://youtube.com/@thetechnobear 


# Supporting this project
You can support this project in multiple way

a) Help others in the community
We can help each other to have a better experience, find new ways to enjoy the Eigenharps and EigenD.
join the community forum

b) Help with testing / feedback
Co-ordinated via polyexpression.com, 

c) Help with development 

d) Buy me a coffee at  ko-fi (https://ko-fi.com/thetechnobear)
I do this for the love of it, not money.
however, I do incur various expenses, things hardware, software,subscriptions / services (e.g. github pro).
It's not much, and its 'cross project', I have many open source projects, so a little can help.


