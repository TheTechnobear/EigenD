.PHONY: all etc html clean tags save load stage pkg test parallel dev-setup

TOOLS ?= tools

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

SCONS ?= PYTHONPATH=$(TOOLS)/packages/SCons4 python3 $(TOOLS)/packages/SCons4/bin/scons
VENV_DEV = .venv_dev

all:
	@$(SCONS) -f $(TOOLS)/SConstruct -j8 target-default

parallel:
	@$(SCONS) -f $(TOOLS)/SConstruct -j8 target-default

single:
	@$(SCONS) -f $(TOOLS)/SConstruct -j1 target-default

verbose:
	@PI_VERBOSE=1 $(SCONS) -f $(TOOLS)/SConstruct -j1 target-default

quiet:
	@$(SCONS) -f $(TOOLS)/SConstruct -j1 -s target-default

clean:
	@$(SCONS) -f $(TOOLS)/SConstruct -c
	@$(RM_RF) tmp env.sh dbg.sh tags
	@$(FIND_PYC)

tags:
	@$(SCONS) -f $(TOOLS)/SConstruct tags

stage:
	@$(SCONS) -f $(TOOLS)/SConstruct target-stage

mpkg:
	@$(SCONS) -f $(TOOLS)/SConstruct target-mpkg

pkg:
	@$(SCONS) -f $(TOOLS)/SConstruct target-pkg

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
	@$(VENV_DEV)/Scripts/pip install --upgrade pip > /dev/null
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
