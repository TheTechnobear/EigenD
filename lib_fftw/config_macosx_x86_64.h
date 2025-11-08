/* config.h for FFTW 3.3.10 - macOS x86_64 */

/* Define to compile in long-double precision. */
/* #undef BENCHFFT_LDOUBLE */

/* Define to compile in quad precision. */
/* #undef BENCHFFT_QUAD */

/* Define to compile in single precision. */
/* #undef BENCHFFT_SINGLE */

/* Define to 1 if using `alloca.c'. */
/* #undef C_ALLOCA */

/* Define to disable Fortran wrappers. */
#define DISABLE_FORTRAN 1

/* Define to dummy `main' function (if any) required to link to the Fortran
   libraries. */
/* #undef F77_DUMMY_MAIN */

/* Define to a macro mangling the given C identifier (in lower and upper
   case), which must not contain underscores, for linking with Fortran. */
/* #undef F77_FUNC */

/* As F77_FUNC, but for C identifiers containing underscores. */
/* #undef F77_FUNC_ */

/* Define if F77_FUNC and F77_FUNC_ are equivalent. */
/* #undef F77_FUNC_EQUIV */

/* Define if F77 and FC dummy `main' functions are identical. */
/* #undef FC_DUMMY_MAIN_EQ_F77 */

/* C compiler name and flags */
#define FFTW_CC "clang"

/* Define to enable extra FFTW debugging code. */
/* #undef FFTW_DEBUG */

/* Define to enable the use of alloca(). */
#define FFTW_ENABLE_ALLOCA 1

/* Define to compile in long-double precision. */
/* #undef FFTW_LDOUBLE */

/* Define to compile in quad precision. */
/* #undef FFTW_QUAD */

/* Define to enable pseudorandom estimate planning for debugging. */
/* #undef FFTW_RANDOM_ESTIMATOR */

/* Define to compile in single precision. */
#define FFTW_SINGLE 1

/* Define to 1 if you have the `abort' function. */
#define HAVE_ABORT 1

/* Define to 1 if you have `alloca', as a function or macro. */
#define HAVE_ALLOCA 1

/* Define to 1 if you have <alloca.h> and it should be used (not on Ultrix).
   */
#define HAVE_ALLOCA_H 1

/* Define to enable Altivec optimizations. */
/* #undef HAVE_ALTIVEC */

/* Define to 1 if you have the <altivec.h> header file. */
/* #undef HAVE_ALTIVEC_H */

/* Define to enable AVX optimizations. */
/* #undef HAVE_AVX */

/* Define to enable AVX2 optimizations. */
/* #undef HAVE_AVX2 */

/* Define to enable AVX512 optimizations. */
/* #undef HAVE_AVX512 */

/* Define to 1 if you have the `clock_gettime' function. */
/* #undef HAVE_CLOCK_GETTIME */

/* Define to 1 if you have the `cosl' function. */
#define HAVE_COSL 1

/* Define to 1 if you have the declaration of `cosl', and to 0 if you don't.
   */
#define HAVE_DECL_COSL 1

/* Define to 1 if you have the declaration of `drand48', and to 0 if you
   don't. */
#define HAVE_DECL_DRAND48 1

/* Define to 1 if you have the declaration of `memalign', and to 0 if you
   don't. */
#define HAVE_DECL_MEMALIGN 0

/* Define to 1 if you have the declaration of `posix_memalign', and to 0 if
   you don't. */
#define HAVE_DECL_POSIX_MEMALIGN 1

/* Define to 1 if you have the declaration of `sinl', and to 0 if you don't.
   */
#define HAVE_DECL_SINL 1

/* Define to 1 if you have the <dlfcn.h> header file. */
#define HAVE_DLFCN_H 1

/* Define to 1 if you don't have `vprintf' but do have `_doprnt.' */
/* #undef HAVE_DOPRNT */

/* Define to 1 if you have the `drand48' function. */
#define HAVE_DRAND48 1

/* Define to 1 if you have the <fenv.h> header file. */
#define HAVE_FENV_H 1

/* Define to 1 if you have the `gethrtime' function. */
/* #undef HAVE_GETHRTIME */

/* Define to 1 if you have the `getpagesize' function. */
#define HAVE_GETPAGESIZE 1

/* Define to 1 if you have the `gettimeofday' function. */
#define HAVE_GETTIMEOFDAY 1

/* Define to 1 if hrtime_t is defined in <sys/time.h> */
/* #undef HAVE_HRTIME_T */

/* Define to 1 if you have the <inttypes.h> header file. */
#define HAVE_INTTYPES_H 1

/* Define if the isnan() function/macro is available. */
#define HAVE_ISNAN 1

/* Define to 1 if you have the `m' library (-lm). */
#define HAVE_LIBM 1

/* Define to 1 if you have the <limits.h> header file. */
#define HAVE_LIMITS_H 1

/* Define to 1 if the compiler supports `long double' */
#define HAVE_LONG_DOUBLE 1

/* Define to 1 if you have the `mach_absolute_time' function. */
#define HAVE_MACH_ABSOLUTE_TIME 1

/* Define to 1 if you have the <malloc.h> header file. */
/* #undef HAVE_MALLOC_H */

/* Define to 1 if you have the `memalign' function. */
/* #undef HAVE_MEMALIGN */

/* Define to 1 if you have the `memmove' function. */
#define HAVE_MEMMOVE 1

/* Define to 1 if you have the <memory.h> header file. */
#define HAVE_MEMORY_H 1

/* Define to 1 if you have the `memset' function. */
#define HAVE_MEMSET 1

/* Define to enable ARM NEON optimizations. */
/* #undef HAVE_NEON */

/* Define if OpenMP is enabled */
/* #undef HAVE_OPENMP */

/* Define to 1 if you have the `posix_memalign' function. */
#define HAVE_POSIX_MEMALIGN 1

/* Define if you have POSIX threads libraries and header files. */
/* #undef HAVE_PTHREAD */

/* Define to 1 if the system has the type `ptrdiff_t'. */
#define HAVE_PTRDIFF_T 1

/* Define to 1 if you have the `sinl' function. */
#define HAVE_SINL 1

/* Define to 1 if you have the `snprintf' function. */
#define HAVE_SNPRINTF 1

/* Define to 1 if you have the `sqrt' function. */
#define HAVE_SQRT 1

/* Define to enable SSE/SSE2 optimizations. */
#define HAVE_SSE2 1

/* Define to 1 if you have the <stddef.h> header file. */
#define HAVE_STDDEF_H 1

/* Define to 1 if you have the <stdint.h> header file. */
#define HAVE_STDINT_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#define HAVE_STDLIB_H 1

/* Define to 1 if you have the `strchr' function. */
#define HAVE_STRCHR 1

/* Define to 1 if you have the <strings.h> header file. */
#define HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#define HAVE_STRING_H 1

/* Define to 1 if you have the `sysctl' function. */
#define HAVE_SYSCTL 1

/* Define to 1 if you have the <sys/stat.h> header file. */
#define HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/time.h> header file. */
#define HAVE_SYS_TIME_H 1

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the `tanl' function. */
#define HAVE_TANL 1

/* Define if we have a threads library. */
/* #undef HAVE_THREADS */

/* Define to 1 if the system has the type `uintptr_t'. */
#define HAVE_UINTPTR_T 1

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* Define to 1 if you have the `vprintf' function. */
#define HAVE_VPRINTF 1

/* Define to enable IBM VSX optimizations. */
/* #undef HAVE_VSX */

/* Define to 1 if you have the `_mm_free' function. */
/* #undef HAVE__MM_FREE */

/* Define to 1 if you have the `_mm_malloc' function. */
/* #undef HAVE__MM_MALLOC */

/* Name of package */
#define PACKAGE "fftw"

/* Define to the address where bug reports for this package should be sent. */
#define PACKAGE_BUGREPORT "fftw@fftw.org"

/* Define to the full name of this package. */
#define PACKAGE_NAME "fftw"

/* Define to the full name and version of this package. */
#define PACKAGE_STRING "fftw 3.3.10"

/* Define to the one symbol short name of this package. */
#define PACKAGE_TARNAME "fftw"

/* Define to the home page for this package. */
#define PACKAGE_URL ""

/* Define to the version of this package. */
#define PACKAGE_VERSION "3.3.10"

/* The size of `double', as computed by sizeof. */
#define SIZEOF_DOUBLE 8

/* The size of `float', as computed by sizeof. */
#define SIZEOF_FLOAT 4

/* The size of `int', as computed by sizeof. */
#define SIZEOF_INT 4

/* The size of `long', as computed by sizeof. */
#define SIZEOF_LONG 8

/* The size of `long long', as computed by sizeof. */
#define SIZEOF_LONG_LONG 8

/* The size of `ptrdiff_t', as computed by sizeof. */
#define SIZEOF_PTRDIFF_T 8

/* The size of `size_t', as computed by sizeof. */
#define SIZEOF_SIZE_T 8

/* The size of `unsigned int', as computed by sizeof. */
#define SIZEOF_UNSIGNED_INT 4

/* The size of `unsigned long', as computed by sizeof. */
#define SIZEOF_UNSIGNED_LONG 8

/* The size of `unsigned long long', as computed by sizeof. */
#define SIZEOF_UNSIGNED_LONG_LONG 8

/* The size of `void *', as computed by sizeof. */
#define SIZEOF_VOID_P 8

/* Define to 1 if you have the ANSI C header files. */
#define STDC_HEADERS 1

/* Define to 1 if you can safely include both <sys/time.h> and <time.h>. */
#define TIME_WITH_SYS_TIME 1

/* Define if we have and are using POSIX threads. */
/* #undef USING_POSIX_THREADS */

/* Version number of package */
#define VERSION "3.3.10"

/* Use common Windows Fortran mangling styles for the Fortran interfaces. */
/* #undef WINDOWS_F77_MANGLING */

/* Include g77-compatible wrappers in addition to any other Fortran wrappers.
   */
/* #undef WITH_G77_WRAPPERS */

/* Use our own aligned malloc routine; mainly helpful for Windows systems
   lacking aligned allocation system-library routines. */
/* #undef WITH_OUR_MALLOC */

/* Use low-precision timers, making planner very slow */
/* #undef WITH_SLOW_TIMER */
