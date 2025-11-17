# CMakeLists.txt for EigenD
# This is a wrapper that calls SCons4 in the same way as the Makefile
# The actual build system is SCons - this just provides CMake integration for IDEs

cmake_minimum_required(VERSION 3.15)
project(EigenD NONE)

# Build configuration variables (similar to Makefile)
set(JOBS 8 CACHE STRING "Number of parallel jobs")
set(SCONS_OPTS "" CACHE STRING "Additional SCons options")
set(TARGET "target-default" CACHE STRING "SCons target to build")
set(VERBOSE "" CACHE STRING "Verbose environment prefix (e.g., PI_VERBOSE=1)")
set(QUIET "" CACHE STRING "Quiet option for SCons")

# Set paths
set(TOOLS_DIR "${CMAKE_SOURCE_DIR}/tools")
set(SCONS_DIR "${TOOLS_DIR}/packages/SCons4")
set(SCONS_SCRIPT "${SCONS_DIR}/bin/scons")
set(SCONSTRUCT "${TOOLS_DIR}/SConstruct")

# Find Python3
find_package(Python3 REQUIRED COMPONENTS Interpreter)

# Override to use Python 3.14 from python.org (standard installation)
set(Python3_EXECUTABLE "/usr/local/bin/python3.14")

# Common SCons command setup
set(SCONS_ENV PYTHONPATH=${SCONS_DIR})
set(SCONS_BASE_CMD ${CMAKE_COMMAND} -E env ${SCONS_ENV} ${Python3_EXECUTABLE} ${SCONS_SCRIPT} -f ${SCONSTRUCT})

# Default target (builds with configurable jobs)
add_custom_target(eigend-all ALL
    COMMAND ${CMAKE_COMMAND} -E env ${VERBOSE} ${SCONS_ENV} ${Python3_EXECUTABLE} ${SCONS_SCRIPT} -f ${SCONSTRUCT} ${QUIET} ${SCONS_OPTS} -j${JOBS} ${TARGET}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building EigenD (${TARGET} with ${JOBS} jobs)"
    USES_TERMINAL
)


# Clean target
add_custom_target(clean-all
    COMMAND ${SCONS_BASE_CMD} -c
    COMMAND ${CMAKE_COMMAND} -E rm -rf tmp env.sh dbg.sh tags .sconsign*
    COMMAND find . -name "*.pyc" -type f -delete
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Cleaning EigenD build artifacts"
    USES_TERMINAL
)

# Tags target
add_custom_target(tags
    COMMAND ${SCONS_BASE_CMD} tags
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Generating tags"
    USES_TERMINAL
)

# Stage target
add_custom_target(stage
    COMMAND ${SCONS_BASE_CMD} target-stage
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building EigenD stage"
    USES_TERMINAL
)

# Mac package target
add_custom_target(mpkg
    COMMAND ${SCONS_BASE_CMD} target-mpkg
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building EigenD Mac package"
    USES_TERMINAL
)

# Generic package target
add_custom_target(pkg
    COMMAND ${SCONS_BASE_CMD} target-pkg
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building EigenD package"
    USES_TERMINAL
)

# Make 'eigend-all' the default target when running 'cmake --build'
set_property(DIRECTORY PROPERTY VS_STARTUP_PROJECT eigend-all)

# Print usage information
message(STATUS "EigenD CMake wrapper for SCons build system")
message(STATUS "Available targets:")
message(STATUS "  eigend-all - Build EigenD (${TARGET} with ${JOBS} jobs)")
message(STATUS "  clean-all  - Clean all build artifacts")
message(STATUS "  tags       - Generate tags")
message(STATUS "  stage      - Build EigenD stage")
message(STATUS "  mpkg       - Build Mac package")
message(STATUS "  pkg        - Build generic package")
message(STATUS "")
message(STATUS "Configuration variables (set with -DVAR=value):")
message(STATUS "  JOBS=${JOBS} - Number of parallel jobs")
message(STATUS "  TARGET=${TARGET} - SCons target to build")
message(STATUS "  SCONS_OPTS=${SCONS_OPTS} - Additional SCons options")
message(STATUS "  VERBOSE=${VERBOSE} - Verbose prefix e.g PI_VERBOSE=1")
message(STATUS "  QUIET=${QUIET} - Quiet option")
message(STATUS "")
message(STATUS "Usage:")
message(STATUS "  cmake -B build -DJOBS=4 -DTARGET=target-stage")
message(STATUS "  cmake --build build --target eigend-all")
message(STATUS "  cmake --build build --target parallel")
message(STATUS "")
message(STATUS "Note: For arbitrary SCons targets (e.g., plg_rig), use the Makefile:")
message(STATUS "  make plg_rig")
message(STATUS "  make TARGET=plg_rig JOBS=4")
