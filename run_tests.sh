#!/bin/bash

# Professional EigenD Test Runner
# Usage: ./run_tests.sh [--level LEVEL] [--timeout SECONDS] [--verbose] [--html]

set -e

# Default values
LEVEL=""
TIMEOUT=10
VERBOSE=""
HTML=""
PYTHON_EXE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --level)
            LEVEL="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --html)
            HTML="--html=reports/test_report.html --self-contained-html"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--level LEVEL] [--timeout SECONDS] [--verbose] [--html]"
            echo ""
            echo "Options:"
            echo "  --level LEVEL      Run specific test level (foundation|core|data|plugins|applications|integration|all)"
            echo "  --timeout SECONDS  Test timeout in seconds (default: 10)"
            echo "  --verbose, -v      Verbose output"
            echo "  --html             Generate HTML report"
            echo "  --help, -h         Show this help"
            echo ""
            echo "Test Levels:"
            echo "  foundation    - Basic Python 3.14 environment and imports"
            echo "  core          - PIW engine and core functionality" 
            echo "  data          - Data serialization and persistence"
            echo "  plugins       - Plugin system functionality"
            echo "  applications  - Application layer testing"
            echo "  integration   - End-to-end integration tests"
            echo "  all           - Run all tests"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Find Python executable
if [[ -f ".venv/bin/python" ]]; then
    PYTHON_EXE=".venv/bin/python"
elif command -v python3.14 &> /dev/null; then
    PYTHON_EXE="python3.14"
elif command -v python3 &> /dev/null; then
    PYTHON_EXE="python3"
else
    print_error "No suitable Python interpreter found"
    exit 1
fi

print_status "Using Python interpreter: $PYTHON_EXE"

# Ensure we're in the right directory
if [[ ! -d "tests" ]]; then
    print_error "Tests directory not found. Run from EigenD root directory."
    exit 1
fi

# Create reports directory if HTML output requested
if [[ -n "$HTML" ]]; then
    mkdir -p reports
fi

# Build pytest command
PYTEST_CMD="$PYTHON_EXE -m pytest"
PYTEST_ARGS="--timeout=$TIMEOUT $VERBOSE"

if [[ -n "$HTML" ]]; then
    PYTEST_ARGS="$PYTEST_ARGS $HTML"
fi

# Determine which tests to run
if [[ -z "$LEVEL" || "$LEVEL" == "all" ]]; then
    TEST_PATH="tests/unit/"
    print_status "Running all test levels"
else
    case $LEVEL in
        foundation)
            TEST_PATH="tests/unit/test_00_foundation.py"
            ;;
        core)
            TEST_PATH="tests/unit/test_01_core_piw.py"
            ;;
        data)
            TEST_PATH="tests/unit/test_02_data_layer.py"
            ;;
        plugins)
            TEST_PATH="tests/unit/test_03_plugins.py"
            ;;
        applications)
            TEST_PATH="tests/unit/test_04_applications.py"
            ;;
        integration)
            TEST_PATH="tests/unit/test_05_integration.py"
            ;;
        *)
            print_error "Invalid test level: $LEVEL"
            print_error "Valid levels: foundation, core, data, plugins, applications, integration, all"
            exit 1
            ;;
    esac
    print_status "Running test level: $LEVEL"
fi

# Set up environment
export PYTHONPATH="$PWD:$PYTHONPATH"

# Run the tests
print_status "Executing: $PYTEST_CMD $PYTEST_ARGS $TEST_PATH"
echo ""

if $PYTEST_CMD $PYTEST_ARGS $TEST_PATH; then
    print_success "All tests completed successfully!"
    if [[ -n "$HTML" ]]; then
        print_status "HTML report generated: reports/test_report.html"
    fi
else
    print_error "Some tests failed or encountered errors"
    exit 1
fi