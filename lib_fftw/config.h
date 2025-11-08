
#include <picross/pic_config.h>

#ifdef PI_WINDOWS
#define FFTW_DLL 1
#include <config_windows_x86_64.h>
#endif

#ifdef PI_LINUX
#ifdef PI_LINUX_ARM
#include <config_linux_arm64.h>
#else
#include <config_linux_x86_64.h>
#endif
#endif

#ifdef PI_MACOSX
#ifdef PI_MACOSX_ARM
#include <config_macosx_arm64.h>
#endif 

#ifdef PI_MACOSX_8664
#include <config_macosx_x86_64.h>
#endif
#endif