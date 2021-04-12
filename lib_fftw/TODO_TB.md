THIS IS NOT COMPILING AT THE MOMENT - SEE BELOW



What Ive Done

Ive updated src with fftw 3.3.9 - from http://fftw.org/download.html
this has ARM support.

I then ran ./configure on macos m1 to get a valid 3.3.9 config file - which is now in config_mac.h

note: this would potentiallly not be compatible with intel mac!

options can be found in src/config.h.in 


note: have neon is surprisingly off...



next steps... 
intially is just to build and compile, 
do this this I need to update the source files required.

it looks like the best way to do this, would be to look at CMakeFile.txt

this has a section like:
````
file(GLOB           fftw_dft_simd_avx_SOURCE        dft/simd/avx/*.c    dft/simd/avx/*.h)
file(GLOB           fftw_dft_simd_avx2_SOURCE       dft/simd/avx2/*.c   dft/simd/avx2/*.h dft/simd/avx2-128/*.c   dft/simd/avx2-128/*.h)
file(GLOB           fftw_kernel_SOURCE              kernel/*.c          kernel/*.h)
````

so this is telling me, which files I need depending on if we are compiling general and for various fpu.
(again oddly neon is missing - but its pretty obvious what to add)

I think I can therefore basically do something similar in my SConscript for different fpu types

(seems pretty simple now, the fpu are in different sub dirs)



I can also cross reference this file list, with what I can see is new/missing in git (sublime shows this well)



this should allow me to compile and test


I will need to test this with the 'clarinet'
bare in mind, on linux when using the installed fftw3, it didnt not sound right... 
so this newer version MAY be problematic!  
so we need to hear the clarinet working properly before committing this back to main! 





-------- 

ONCE its working on Mac apple silcon... (with neon/arm support?!)

then I can look to see at the differences in config_mac, to orginal in git...
the idea being to work out what I need to change for config_linux.h, and config_win.h

also to check to see if there are some options that perhaps have been enabled explicity via ./configure.
(i.e. by default are not enabled, but eigenlabs enabled)


I think that should get me working on all platforms.
we might also want a config_mac_arm.h vs config_mac_intel_.h , and something similar for linux


ALSO currently on linux, sconcript it set to not use this local version, but rather to use installed one - so this needs to be changed.
