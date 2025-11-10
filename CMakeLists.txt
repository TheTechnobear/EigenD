# CMakeLists.txt for EigenD
# This is a wrapper that calls SCons4 in the same way as the Makefile
# The actual build system is SCons - this just provides CMake integration for IDEs

cmake_minimum_required(VERSION 3.15)
project(EigenD NONE)

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

# Default target (builds with -j1)
add_custom_target(eigend-all
    COMMAND ${SCONS_BASE_CMD} -j8 target-default
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building EigenD (parallel)"
    USES_TERMINAL
)

# Parallel build target (builds with -j8)
add_custom_target(parallel
    COMMAND ${SCONS_BASE_CMD} -j8 target-default
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building EigenD (parallel)"
    USES_TERMINAL
)

# Single-threaded build target (same as 'all')
add_custom_target(single
    COMMAND ${SCONS_BASE_CMD} -j1 target-default
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building EigenD (single-threaded)"
    USES_TERMINAL
)

# Verbose build target
add_custom_target(verbose
    COMMAND ${CMAKE_COMMAND} -E env PI_VERBOSE=1 ${SCONS_ENV} ${Python3_EXECUTABLE} ${SCONS_SCRIPT} -f ${SCONSTRUCT} -j1 target-default
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building EigenD (verbose)"
    USES_TERMINAL
)

# Quiet build target
add_custom_target(quiet
    COMMAND ${SCONS_BASE_CMD} -j1 -s target-default
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building EigenD (quiet)"
    USES_TERMINAL
)

# Clean target
add_custom_target(clean-all
    COMMAND ${SCONS_BASE_CMD} -c
    COMMAND ${CMAKE_COMMAND} -E rm -rf tmp env.sh dbg.sh tags
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
message(STATUS "  eigend-all - Build EigenD (8 parallel default)")
message(STATUS "  parallel   - Build EigenD (8 parallel jobs)")
message(STATUS "  single     - Build EigenD (single-threaded)")
message(STATUS "  verbose    - Build EigenD with verbose output")
message(STATUS "  quiet      - Build EigenD with minimal output")
message(STATUS "  clean-all  - Clean all build artifacts")
message(STATUS "  tags       - Generate tags")
message(STATUS "  stage      - Build EigenD stage")
message(STATUS "  mpkg       - Build Mac package")
message(STATUS "  pkg        - Build generic package")
message(STATUS "")
message(STATUS "Usage:")
message(STATUS "  cmake -B build")
message(STATUS "  cmake --build build --target eigend-all")
message(STATUS "  cmake --build build --target parallel")
message(STATUS "")
message(STATUS "Note: The actual build system is SCons. This CMakeLists.txt")
message(STATUS "      is a wrapper to provide CMake/IDE integration.")
