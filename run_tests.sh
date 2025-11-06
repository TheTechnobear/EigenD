#!/bin/bash

# Professional EigenD Test Runner
# Usage: ./run_tests.sh [--level LEVEL] [--test TEST_PATTERN] [--timeout SECONDS] [--verbose] [--html]

set -e

# Default values
LEVEL=""
TEST_PATTERN=""
TIMEOUT=10
VERBOSE=""
HTML=""
PYTHON_EXE=""
PYTEST_EXTRA_ARGS=""
DURATIONS=10  # Show 10 slowest tests by default

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
        --test|-k)
            TEST_PATTERN="$2"
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
        --durations)
            DURATIONS="$2"
            shift 2
            ;;
        --no-durations)
            DURATIONS="0"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--level LEVEL] [--test TEST_PATTERN] [--timeout SECONDS] [--verbose] [--html] [--durations N] [--pytest-args ARGS]"
            echo ""
            echo "Options:"
            echo "  --level LEVEL         Run specific test level (foundation|core|data|plugins|applications|integration|all)"
            echo "  --test TEST_PATTERN   Run specific test(s) matching pattern (pytest -k syntax)"
            echo "  --timeout SECONDS     Test timeout in seconds (default: 10)"
            echo "  --verbose, -v         Verbose output"
            echo "  --html                Generate HTML report"
            echo "  --durations N         Show N slowest tests (default: 10, use 0 to disable)"
            echo "  --no-durations        Disable duration reporting"
            echo "  --pytest-args ARGS   Additional pytest arguments (e.g., --pytest-args='-s --tb=short')"
            echo "  --help, -h            Show this help"
            echo ""
            echo "Test Levels:"
            echo "  foundation    - Basic Python 3.14 environment and imports"
            echo "  core          - PIW engine and core functionality" 
            echo "  data          - Data serialization and persistence"
            echo "  plugins       - Plugin system functionality"
            echo "  applications  - Application layer testing"
            echo "  integration   - End-to-end integration tests"
            echo "  all           - Run all tests"
            echo ""
            echo "Test Pattern Examples:"
            echo "  --test 'mutex'                    - Run tests with 'mutex' in name"
            echo "  --test 'mutex_function'           - Run specific test method"
            echo "  --test 'mutex or session'         - Run tests matching either pattern"
            echo "  --test 'not mutex'                - Run tests NOT matching pattern"
            echo ""
            echo "Performance Notes:"
            echo "  PIW session tests reflect real EigenD behavior (~7s session cleanup)"
            echo "  This is expected overhead for proper network component teardown"
            echo "  Tests run in realistic conditions to avoid false positives"
            echo ""
            echo "Pytest Arguments Examples:"
            echo "  --pytest-args='-s'               - Show print statements during tests"
            echo "  --pytest-args='-s --tb=short'    - Show prints and short tracebacks"
            echo "  --pytest-args='--pdb'            - Drop into debugger on failures"
            echo "  --pytest-args='-x'               - Stop on first failure"
            exit 0
            ;;
        --pytest-args)
            PYTEST_EXTRA_ARGS="$2"
            shift 2
            ;;
        --pytest-args=*)
            PYTEST_EXTRA_ARGS="${1#*=}"
            shift
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

# Add duration reporting if enabled
if [[ $DURATIONS -gt 0 ]]; then
    PYTEST_ARGS="$PYTEST_ARGS --durations=$DURATIONS"
fi

if [[ -n "$HTML" ]]; then
    PYTEST_ARGS="$PYTEST_ARGS $HTML"
fi

# Add extra pytest arguments if specified
if [[ -n "$PYTEST_EXTRA_ARGS" ]]; then
    PYTEST_ARGS="$PYTEST_ARGS $PYTEST_EXTRA_ARGS"
fi

# Add test pattern if specified
if [[ -n "$TEST_PATTERN" ]]; then
    PYTEST_ARGS="$PYTEST_ARGS -k \"$TEST_PATTERN\""
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

# Record start time
START_TIME=$(date +%s)
START_TIME_READABLE=$(date '+%Y-%m-%d %H:%M:%S')
print_status "Test run started at: $START_TIME_READABLE"
echo ""

# Use eval to properly handle complex command arguments
FULL_COMMAND="$PYTEST_CMD $PYTEST_ARGS $TEST_PATH"
if eval "$FULL_COMMAND"; then
    # Calculate elapsed time
    END_TIME=$(date +%s)
    END_TIME_READABLE=$(date '+%Y-%m-%d %H:%M:%S')
    ELAPSED_TIME=$((END_TIME - START_TIME))
    ELAPSED_MINUTES=$((ELAPSED_TIME / 60))
    ELAPSED_SECONDS=$((ELAPSED_TIME % 60))
    
    echo ""
    print_success "All tests completed successfully!"
    print_status "Test run finished at: $END_TIME_READABLE"
    
    if [[ $ELAPSED_TIME -lt 60 ]]; then
        print_status "Total execution time: ${ELAPSED_TIME} seconds"
    else
        print_status "Total execution time: ${ELAPSED_MINUTES}m ${ELAPSED_SECONDS}s (${ELAPSED_TIME} seconds total)"
    fi
    
    # Warn if tests took longer than expected (accounting for PIW session overhead)
    if [[ $ELAPSED_TIME -gt 300 ]]; then
        print_warning "Test execution took longer than 5 minutes - potential performance issues detected"
    elif [[ $ELAPSED_TIME -gt 120 ]]; then
        print_warning "Test execution took longer than 2 minutes - may need investigation"
        print_status "Note: PIW session tests include realistic ~7s cleanup per session"
    fi
    
    if [[ -n "$HTML" ]]; then
        print_status "HTML report generated: reports/test_report.html"
    fi
else
    # Calculate elapsed time even for failures
    END_TIME=$(date +%s)
    END_TIME_READABLE=$(date '+%Y-%m-%d %H:%M:%S')
    ELAPSED_TIME=$((END_TIME - START_TIME))
    ELAPSED_MINUTES=$((ELAPSED_TIME / 60))
    ELAPSED_SECONDS=$((ELAPSED_TIME % 60))
    
    echo ""
    print_error "Some tests failed or encountered errors"
    print_status "Test run finished at: $END_TIME_READABLE"
    
    if [[ $ELAPSED_TIME -lt 60 ]]; then
        print_status "Total execution time: ${ELAPSED_TIME} seconds"
    else
        print_status "Total execution time: ${ELAPSED_MINUTES}m ${ELAPSED_SECONDS}s (${ELAPSED_TIME} seconds total)"
    fi
    
    exit 1
fi