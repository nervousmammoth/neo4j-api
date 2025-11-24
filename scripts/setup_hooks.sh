#!/usr/bin/env bash
#
# Setup script for Git hooks
# Installs pre-commit framework hooks and custom pre-push hook
#
# Usage: ./scripts/setup_hooks.sh

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🎣 Git Hooks Setup for neo4j-api${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    echo -e "${RED}   Please run this script from the project root${NC}"
    exit 1
fi

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Virtual environment not activated${NC}"
    echo -e "${YELLOW}   It's recommended to activate your virtual environment first:${NC}"
    echo -e "${YELLOW}   source venv/bin/activate${NC}\n"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Setup cancelled${NC}"
        exit 0
    fi
fi

# 1. Install pre-commit if not already installed
echo -e "${BLUE}📦 Step 1/4: Installing pre-commit framework...${NC}"
if command -v pre-commit &> /dev/null; then
    echo -e "${GREEN}✓ pre-commit is already installed: $(pre-commit --version)${NC}"
else
    echo -e "${YELLOW}Installing pre-commit...${NC}"
    pip install pre-commit>=3.5.0
    echo -e "${GREEN}✓ pre-commit installed${NC}"
fi

# 2. Install pre-commit hooks
echo -e "\n${BLUE}🔧 Step 2/4: Installing pre-commit hooks...${NC}"
if pre-commit install --install-hooks; then
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    echo -e "${RED}❌ Failed to install pre-commit hooks${NC}"
    exit 1
fi

# 3. Install commit-msg hook for conventional commits
echo -e "\n${BLUE}💬 Step 3/4: Installing commit-msg hook...${NC}"
if pre-commit install --hook-type commit-msg; then
    echo -e "${GREEN}✓ Commit-msg hook installed (conventional commits validation)${NC}"
else
    echo -e "${RED}❌ Failed to install commit-msg hook${NC}"
    exit 1
fi

# 4. Install custom pre-push hook
echo -e "\n${BLUE}🚀 Step 4/4: Installing custom pre-push hook...${NC}"

# Check if pre-push template exists
if [ ! -f "scripts/pre-push.template" ]; then
    echo -e "${RED}❌ Error: scripts/pre-push.template not found${NC}"
    exit 1
fi

# Copy template to .git/hooks/pre-push
cp scripts/pre-push.template .git/hooks/pre-push

# Make it executable
chmod +x .git/hooks/pre-push

echo -e "${GREEN}✓ Custom pre-push hook installed${NC}"

# 5. Summary
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Git hooks setup complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${GREEN}Installed hooks:${NC}"
echo -e "  ${GREEN}✓${NC} pre-commit  - Code quality checks (Black, Ruff, mypy)"
echo -e "  ${GREEN}✓${NC} commit-msg  - Conventional commits validation"
echo -e "  ${GREEN}✓${NC} pre-push    - Unit tests with 100% coverage\n"

echo -e "${BLUE}What happens now:${NC}"
echo -e "  • On ${YELLOW}git commit${NC}: Fast quality checks (~5-10 seconds)"
echo -e "    - Black (code formatting)"
echo -e "    - Ruff (linting)"
echo -e "    - mypy (type checking)"
echo -e "    - Commit message format (feat:, fix:, test:, etc.)"
echo -e "\n  • On ${YELLOW}git push${NC}: Unit testing (~30-60 seconds)"
echo -e "    - Unit tests with 100% coverage requirement\n"

echo -e "${BLUE}Useful commands:${NC}"
echo -e "  ${YELLOW}pre-commit run --all-files${NC}  - Run hooks on all files"
echo -e "  ${YELLOW}pre-commit autoupdate${NC}       - Update hook versions"
echo -e "  ${YELLOW}git commit --no-verify${NC}      - Skip pre-commit hooks (not recommended)"
echo -e "  ${YELLOW}git push --no-verify${NC}        - Skip pre-push hook (not recommended)\n"

echo -e "${GREEN}✨ You're all set! Happy coding!${NC}\n"

exit 0
