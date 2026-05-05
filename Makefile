.PHONY: all etc html clean tags save load stage pkg test dev-setup libusb-setup list-targets FORCE

FORCE:

.DEFAULT_GOAL := all

TOOLS = tools

# Platform detection
ifeq ($(OS),Windows_NT)
    # Windows/MSYS2
    PYTHON_BUILD ?= /c/Python314/python.exe
    VENV_ACTIVATE = $(VENV_DEV)/Scripts/activate
    RM_RF = rm -rf
    FIND_PYC = find . -name "*.pyc" -type f -delete
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

# libusb unpacked location (Windows only)
LIBUSB_ARCHIVE = resources/libusb-1.0.29.7z
LIBUSB_DIR     = tmp/libusb
LIBUSB_SENTINEL = $(LIBUSB_DIR)/include/libusb-1.0/libusb.h


ifeq ($(OS),Windows_NT)
SCONS ?= PYTHONPATH=$(TOOLS)/packages/SCons4 $(PYTHON_BUILD) $(TOOLS)/packages/SCons4/bin/scons
else
SCONS ?= PYTHONPATH=$(TOOLS)/packages/SCons4 python3 $(TOOLS)/packages/SCons4/bin/scons
endif
VENV_DEV = .venv_dev

# VERBOSE example
# make plg_rig VERBOSE="PI_VERBOSE=1" 

ifeq ($(OS),Windows_NT)
all: $(LIBUSB_SENTINEL)
	@$(VERBOSE) $(SCONS) -f $(TOOLS)/SConstruct $(QUIET) $(SCONS_OPTS) -j$(JOBS) $(TARGET)
else
all:
	@$(VERBOSE) $(SCONS) -f $(TOOLS)/SConstruct $(QUIET) $(SCONS_OPTS) -j$(JOBS) $(TARGET)
endif

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
	@$(VENV_DEV)/Scripts/pip install -r py_requirements.txt
else
	@$(VENV_DEV)/bin/pip install --upgrade pip > /dev/null
	@$(VENV_DEV)/bin/pip install -r py_requirements.txt
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

# Unpack the libusb Windows binaries from the vendored archive.
# Only needed on Windows; uses p7zip (pacman -S p7zip).
# Re-runs automatically if the archive is newer than the sentinel.
libusb-setup: $(LIBUSB_SENTINEL)

$(LIBUSB_SENTINEL): $(LIBUSB_ARCHIVE)
	@echo "Unpacking libusb from $(LIBUSB_ARCHIVE)..."
	@mkdir -p $(LIBUSB_DIR)/include/libusb-1.0
	@mkdir -p $(LIBUSB_DIR)/lib
	@7z e $(LIBUSB_ARCHIVE) include/libusb.h -o$(LIBUSB_DIR)/include/libusb-1.0 -y > /dev/null
	@7z e $(LIBUSB_ARCHIVE) 'VS2022/MS64/dll/libusb-1.0.lib' -o$(LIBUSB_DIR)/lib -y > /dev/null
	@7z e $(LIBUSB_ARCHIVE) 'VS2022/MS64/dll/libusb-1.0.dll' -o$(LIBUSB_DIR)/lib -y > /dev/null
	@touch $(LIBUSB_SENTINEL)
	@echo "libusb unpacked: include at $(LIBUSB_DIR)/include, lib at $(LIBUSB_DIR)/lib"

% : FORCE
	@$(VERBOSE) $(SCONS) -f $(TOOLS)/SConstruct $(QUIET) $(SCONS_OPTS) -j$(JOBS) $@
