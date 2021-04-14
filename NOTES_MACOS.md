## STATUS

experimental pre-release 2.2.0



## requirements 

MIN macos 10.13 (High Sierra)

system python at /System/Library/Frameworks/Python.framework/Versions/2.7/bin/python



## Known issues 
(will fix)
- convolver is disabled on apple silicon (only)


## Limitations (will not change)
- Carbon is not supported on arm
- can only load plugins of same architecture , i.e. intel 64 bit only , or arm only, no bridging
- no universal binary


## currently not support
- EigenCommander & EigenBrowser



## BUILDING on macos

arm  build
export BUILD_TARGET=arm
make
make mpkg

64 bit intel  build
export BUILD_TARGET=x86_64
make
make mpkg




------


## Code issues/notes

//ARMHACK

pic_resources.cpp : 561 ///HACKED - no close function... move to fopen/fclose?
libfftw:  disabled  SConfig, no ARM
plg_convolver disabled SConfig no libfftw




not used anymore since default has changed, but useful to know
export PI_PYTHON=/System/Library/Frameworks/Python.framework/Versions/2.7/bin/python


