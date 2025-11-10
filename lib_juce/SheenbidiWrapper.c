/*
 * Wrapper file to compile SheenBidi with unity build enabled.
 * This matches the approach used by JUCE's CMake build system.
 */

#define SB_CONFIG_UNITY 1

#include "juce/modules/juce_graphics/unicode/sheenbidi/Source/SheenBidi.c"
