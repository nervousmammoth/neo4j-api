#!/bin/bash
#
# Run BDD tests with behave
#
# Usage:
#   ./scripts/run_bdd_tests.sh              # Run all tests
#   ./scripts/run_bdd_tests.sh --smoke      # Run only smoke tests
#   ./scripts/run_bdd_tests.sh --tag=auth   # Run tests with specific tag
#   ./scripts/run_bdd_tests.sh --help       # Show help
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default configuration
TAGS=""
FORMAT="pretty"
OUTPUT_DIR="reports/behave"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --smoke)
      TAGS="--tags=@smoke"
      echo -e "${YELLOW}Running smoke tests only...${NC}"
      shift
      ;;
    --tag=*)
      TAG="${1#*=}"
      TAGS="--tags=@$TAG"
      echo -e "${YELLOW}Running tests with tag: @$TAG${NC}"
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --smoke          Run only smoke tests (@smoke tag)"
      echo "  --tag=<name>     Run tests with specific tag"
      echo "  --help           Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0                    # Run all BDD tests"
      echo "  $0 --smoke            # Run smoke tests only"
      echo "  $0 --tag=auth         # Run authentication tests"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Run with --help for usage information"
      exit 1
      ;;
  esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Print header
echo ""
echo "=========================================="
echo "  BDD Tests - Neo4j Multi-Database API"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
  echo -e "${YELLOW}Warning: No virtual environment detected${NC}"
  echo "Consider activating venv: source venv/bin/activate"
  echo ""
fi

# Run behave tests
echo -e "${GREEN}Running behave tests...${NC}"
echo ""

behave features/ \
  $TAGS \
  --format=$FORMAT \
  --format=html --outfile="$OUTPUT_DIR/index.html" \
  --format=json --outfile="$OUTPUT_DIR/results.json" \
  --no-capture \
  --no-capture-stderr

# Check exit code
if [ $? -eq 0 ]; then
  echo ""
  echo -e "${GREEN}✅ All tests passed!${NC}"
  echo ""
  echo "HTML Report: $OUTPUT_DIR/index.html"
  echo "JSON Results: $OUTPUT_DIR/results.json"
  echo ""
else
  echo ""
  echo -e "${RED}❌ Some tests failed${NC}"
  echo ""
  echo "Check the reports at: $OUTPUT_DIR/"
  exit 1
fi
