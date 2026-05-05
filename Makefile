.PHONY: all etc html clean tags save load stage pkg test dev-setup list-targets FORCE

FORCE:

.DEFAULT_GOAL := all

TOOLS = tools

# Platform detection
ifeq ($(OS),Windows_NT)
    # Windows: MinGW-w64 via MSYS2 (default) or MSVC (BUILD_TOOLCHAIN=msvc).
    # Run from MSYS2 MinGW64 or UCRT64 shell (no vcvars needed for MinGW).
    # Python.org Python is used for both SCons and Python extension headers/libs.
    PYTHON_BUILD ?= /c/Python314/python.exe
    VENV_ACTIVATE = $(VENV_DEV)/Scripts/activate
    RM_RF = rm -rf
    FIND_PYC = find . -name "*.pyc" -type f -delete
    # Override SCONS invocation to use Windows Python explicitly
    SCONS = PYTHONPATH=$(TOOLS)/packages/SCons4 $(PYTHON_BUILD) $(TOOLS)/packages/SCons4/bin/scons
else
    # macOS/Linux
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        # macOS
        PYTHON_BUILD ?= /usr/local/bin/python3.14
    else
        # Linux
        PYTHON_BUILD ?= /usr/local/bin/python3.14
    endif
    VENV_ACTIVATE = $(VENV_DEV)/bin/activate
    RM_RF = rm -rf
    FIND_PYC = find . -name "*.pyc" -type f -delete
endif

# Build configuration
JOBS ?= 8
SCONS_OPTS ?=
TARGET ?= target-default
VERBOSE ?=
QUIET ?=


SCONS ?= PYTHONPATH=$(TOOLS)/packages/SCons4 python3 $(TOOLS)/packages/SCons4/bin/scons
VENV_DEV = .venv_dev

# VERBOSE example
# make plg_rig VERBOSE="PI_VERBOSE=1" 

all:
	@$(VERBOSE) $(SCONS) -f $(TOOLS)/SConstruct $(QUIET) $(SCONS_OPTS) -j$(JOBS) $(TARGET)

clean:
	@$(SCONS) -f $(TOOLS)/SConstruct -c
	@$(RM_RF) tmp env.sh dbg.sh tags .sconsign*
	@$(FIND_PYC)

tags:
	@$(SCONS) -f $(TOOLS)/SConstruct tags

stage:
	@$(SCONS) -f $(TOOLS)/SConstruct target-stage

mpkg:
	@$(SCONS) -f $(TOOLS)/SConstruct target-mpkg

pkg:
	@$(SCONS) -f $(TOOLS)/SConstruct target-pkg

list-targets:
	@$(SCONS) -f $(TOOLS)/SConstruct --list-targets

dev-setup:
	@echo "========================================"
	@echo "Setting up EigenD development environment"
	@echo "========================================"
	@if [ ! -x "$(PYTHON_BUILD)" ]; then \
		echo "ERROR: Python not found at $(PYTHON_BUILD)"; \
		echo "Please install Python 3.14 from python.org"; \
		exit 1; \
	fi
	@echo "Using Python: $(PYTHON_BUILD)"
	@$(PYTHON_BUILD) --version
	@echo ""
	@if [ -d "$(VENV_DEV)" ]; then \
		echo "Removing existing $(VENV_DEV)..."; \
		$(RM_RF) $(VENV_DEV); \
	fi
	@echo "Creating virtual environment..."
	@$(PYTHON_BUILD) -m venv $(VENV_DEV)
	@echo "Installing development dependencies..."
ifeq ($(OS),Windows_NT)
	@$(VENV_DEV)/Scripts/python.exe -m pip install --upgrade pip > /dev/null
	@$(VENV_DEV)/Scripts/python.exe -m pip install -r py_requirements.txt
else
	@$(VENV_DEV)/bin/python -m pip install --upgrade pip > /dev/null
	@$(VENV_DEV)/bin/python -m pip install -r py_requirements.txt
endif
	@echo ""
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "To run tests:"
	@echo "  ./run_tests.sh --quick --level foundation"
	@echo ""
	@echo "Note: run_tests.sh will auto-activate the venv"
	@echo "======================================="

FORCE:

% : FORCE
	@$(VERBOSE) $(SCONS) -f $(TOOLS)/SConstruct $(QUIET) $(SCONS_OPTS) -j$(JOBS) $@
