2025-11-17: Fixed convolver test to access private attributes via name mangling (_ImpulseBrowser__files) - test now correctly detects 3 impulse files in /usr/local/pi/impulseresponse
2025-11-17: Added --show-output/-s option to run_tests.sh to display test print statements in console
2025-11-17: Fixed convolver impulse directory from 'impulseresponse' to 'ImpulseResponse' to match /usr/local/pi/ImpulseResponse
2025-11-17: Discovered convolver test finds 0 impulse files available - impulse browser exists but no .wav files in resource directories
2025-11-17: Added guidance to test.prompt.md on how to see test output using -s flag with pytest
2025-11-17: Added reminder to test.prompt.md about not running Python directly due to import path issues
2025-11-17: Extended convolver test to check for available impulse files - test confirms impulse browser exists and impulse files are available
2025-11-17: Added test for convolver plugin instantiation in application context to test_03_plugins.py
2025-11-17: Created integration test for Fingerer plugin and fixed relative import issue in finger_plg.py
2025-11-17: updated test suite to allow for testing in application context
2025-11-17: updated test.prompt.md to clarify plugin test level placement - plugins requiring PIW session context belong in integration layer
2025-11-17: reorganized test layers - plugin instantiation now belongs in plugins layer (test_03_plugins.py) with piw_session fixture, moved Fingerer test accordingly
2025-11-17: moved clip manager widget functionality test from integration to plugins layer as it's testing plugin functionality
2025-11-17: moved clip manager agent instantiation test from integration to plugins layer as it's testing plugin functionality
2025-11-17: moved tmp/plugins path setup to conftest.py framework so it's automatically available for all plugin tests