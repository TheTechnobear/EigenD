#!/bin/bash

#
# EigenD Professional Test Runner
# ==============================
# 
# Professional pytest-based test runner for EigenD Python 3.14 migration.
# Ensures consistent environment and provides comprehensive test execution options.
#
# Usage:
#   ./run_tests.sh                           # Run all tests
#   ./run_tests.sh --level foundation        # Run specific level
#   ./run_tests.sh --markers core,data       # Run specific markers
#   ./run_tests.sh --html-report             # Generate HTML report
#   ./run_tests.sh --coverage                # Run with coverage
#   ./run_tests.sh --list-tests              # List available tests
#   ./run_tests.sh --parallel                # Run tests in parallel
#

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "EigenD Professional Test Environment"
echo "===================================="
echo "Project Root: $PROJECT_ROOT"
echo "Test Directory: $SCRIPT_DIR"

# Verify we're in the right place
if [ ! -f "$PROJECT_ROOT/Makefile" ] || [ ! -d "$PROJECT_ROOT/pi" ]; then
    echo "ERROR: Not in EigenD project root directory"
    echo "Expected to find Makefile and pi/ directory"
    exit 1
fi

# Set up Python environment
PYTHON_VENV="$PROJECT_ROOT/.venv/bin/python"
PIP_VENV="$PROJECT_ROOT/.venv/bin/pip"

if [ ! -f "$PYTHON_VENV" ]; then
    echo "ERROR: Python virtual environment not found at $PYTHON_VENV"
    echo "Please run: python3.14 -m venv .venv"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$("$PYTHON_VENV" --version 2>&1)
echo "Python Version: $PYTHON_VERSION"

# Install pytest if not available
if ! "$PYTHON_VENV" -c "import pytest" 2>/dev/null; then
    echo "Installing pytest and plugins..."
    "$PIP_VENV" install pytest pytest-xdist pytest-html pytest-cov pytest-json-report pytest-timeout
fi

# Check if pytest-timeout is installed, install if needed
if ! "$PYTHON_VENV" -c "import pytest_timeout" 2>/dev/null; then
    echo "Installing pytest-timeout..."
    "$PIP_VENV" install pytest-timeout
fi

# Set up environment variables
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/tmp/modules"
export EIGEND_ROOT="$PROJECT_ROOT"

echo "PYTHONPATH: $PYTHONPATH"
echo ""

# Parse command line arguments
PYTEST_ARGS=()
HTML_REPORT=false
COVERAGE=false
PARALLEL=false
LIST_TESTS=false
LEVEL=""
MARKERS=""
TIMEOUT=10  # Default timeout in seconds

while [[ $# -gt 0 ]]; do
    case $1 in
        --level)
            LEVEL="$2"
            shift 2
            ;;
        --markers)
            MARKERS="$2"
            shift 2
            ;;
        --html-report)
            HTML_REPORT=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --list-tests)
            LIST_TESTS=true
            shift
            ;;
        --help)
            echo "EigenD Test Runner Options:"
            echo "  --level LEVEL        Run specific test level (foundation, core, data, plugins, applications, integration)"
            echo "  --markers MARKERS    Run tests with specific markers (comma-separated)"
            echo "  --html-report        Generate HTML test report"
            echo "  --coverage           Run with code coverage analysis"
            echo "  --parallel           Run tests in parallel"
            echo "  --list-tests         List available tests without running"
            echo "  --timeout SECONDS    Set test timeout in seconds (default: 10)"
            echo "  --help               Show this help message"
            echo ""
            echo "Available test levels:"
            echo "  foundation - Core dependency and import tests"
            echo "  core       - Core library functionality (pi, piw, pisession)"
            echo "  data       - Data layer and serialization tests"
            echo "  plugins    - Plugin system tests"
            echo "  applications - Application layer tests"
            echo "  integration - Cross-component integration tests"
            echo ""
            echo "Available markers:"
            echo "  foundation, core, data, plugins, applications, integration"
            echo "  slow, cpp, migration"
            exit 0
            ;;
        *)
            PYTEST_ARGS+=("$1")
            shift
            ;;
    esac
done

# Change to test directory
cd "$SCRIPT_DIR"

# Build pytest command
PYTEST_CMD=("$PYTHON_VENV" -m pytest)

# Add level-specific arguments
if [ -n "$LEVEL" ]; then
    case $LEVEL in
        foundation)
            PYTEST_CMD+=("-m" "foundation")
            ;;
        core)
            PYTEST_CMD+=("-m" "core")
            ;;
        data)
            PYTEST_CMD+=("-m" "data")
            ;;
        plugins)
            PYTEST_CMD+=("-m" "plugins")
            ;;
        applications)
            PYTEST_CMD+=("-m" "applications")
            ;;
        integration)
            PYTEST_CMD+=("-m" "integration")
            ;;
        *)
            echo "ERROR: Unknown level '$LEVEL'"
            echo "Available levels: foundation, core, data, plugins, applications, integration"
            exit 1
            ;;
    esac
fi

# Add marker-specific arguments
if [ -n "$MARKERS" ]; then
    PYTEST_CMD+=("-m" "$MARKERS")
fi

# Add coverage if requested
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD+=("--cov=$PROJECT_ROOT" "--cov-report=html" "--cov-report=term")
fi

# Add HTML report if requested
if [ "$HTML_REPORT" = true ]; then
    PYTEST_CMD+=("--html=reports/test_report.html" "--self-contained-html")
    mkdir -p reports
fi

# Add parallel execution if requested
if [ "$PARALLEL" = true ]; then
    PYTEST_CMD+=("-n" "auto")
fi

# Add list tests if requested
if [ "$LIST_TESTS" = true ]; then
    PYTEST_CMD+=("--collect-only" "-q")
fi

# Add timeout (using pytest-timeout plugin)
PYTEST_CMD+=("--timeout=$TIMEOUT")
PYTEST_CMD+=("--timeout-method=thread")  # Use thread-based timeout for better handling
PYTEST_CMD+=("${PYTEST_ARGS[@]}")

echo "Running Tests"
echo "============="
echo "Command: ${PYTEST_CMD[*]}"
echo ""

# Execute the tests
exec "${PYTEST_CMD[@]}"