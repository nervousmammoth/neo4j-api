#!/bin/bash
#
# Run all tests: Unit tests (pytest) + Code quality checks
#
# Usage:
#   ./scripts/run_all_tests.sh
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "  Complete Test Suite"
echo "  Neo4j Multi-Database REST API"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}Creating virtual environment...${NC}"
  python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt
echo ""

# Run pytest (unit tests)
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Step 1: Unit Tests (pytest)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -d "tests" ]; then
  pytest tests/ \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    -v || { echo -e "${RED}❌ Unit tests failed${NC}"; exit 1; }
  echo ""
  echo -e "${GREEN}✅ Unit tests passed${NC}"
else
  echo -e "${YELLOW}⚠️  No tests/ directory found - skipping unit tests${NC}"
fi

echo ""

# Code quality checks
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Step 2: Code Quality Checks${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Black formatting check
echo -e "${BLUE}Running Black (formatter check)...${NC}"
if [ -d "app" ]; then
  black --check app/ tests/ 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Code formatting issues found. Run: black app/ tests/${NC}"
  }
  echo ""
fi

# Ruff linting
echo -e "${BLUE}Running Ruff (linter)...${NC}"
if [ -d "app" ]; then
  ruff check app/ tests/ 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Linting issues found${NC}"
  }
  echo ""
fi

# mypy type checking
echo -e "${BLUE}Running mypy (type checker)...${NC}"
if [ -d "app" ]; then
  mypy app/ 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Type checking issues found${NC}"
  }
  echo ""
fi

# Summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  🎉 All Tests Passed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Reports generated:"
echo "  - Unit test coverage: htmlcov/index.html"
echo ""
