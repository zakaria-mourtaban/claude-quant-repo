#!/bin/bash
# Verification Script for Crypto Trading Bot Installation
# This script checks that all components are properly installed and configured

set -e

echo "========================================="
echo "Crypto Trading Bot - Installation Verification"
echo "========================================="
echo ""

ERRORS=0
WARNINGS=0

# Function to check success
check_ok() {
    echo "✅ $1"
}

# Function to report error
check_error() {
    echo "❌ $1"
    ERRORS=$((ERRORS + 1))
}

# Function to report warning
check_warning() {
    echo "⚠️  $1"
    WARNINGS=$((WARNINGS + 1))
}

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        check_ok "Python $PYTHON_VERSION found"
    else
        check_error "Python 3.11+ required, found $PYTHON_VERSION"
    fi
else
    check_error "Python 3 not found"
fi

# Check virtual environment
echo ""
echo "Checking virtual environment..."
if [ -d "venv" ]; then
    check_ok "Virtual environment exists"

    # Activate and check packages
    source venv/bin/activate

    # Check freqtrade
    if python -c "import freqtrade" 2>/dev/null; then
        check_ok "Freqtrade installed"
    else
        check_error "Freqtrade not installed (run: pip install freqtrade)"
    fi

    # Check ccxt
    if python -c "import ccxt" 2>/dev/null; then
        check_ok "CCXT installed"
    else
        check_error "CCXT not installed (run: pip install ccxt)"
    fi

    # Check pandas
    if python -c "import pandas" 2>/dev/null; then
        check_ok "Pandas installed"
    else
        check_error "Pandas not installed"
    fi

    # Check TA-Lib
    if python -c "import talib" 2>/dev/null; then
        check_ok "TA-Lib installed"
    else
        check_warning "TA-Lib not installed (optional but recommended)"
    fi

    deactivate
else
    check_error "Virtual environment not found (run: python3 -m venv venv)"
fi

# Check directory structure
echo ""
echo "Checking directory structure..."

REQUIRED_DIRS=(
    "config"
    "user_data"
    "user_data/strategies"
    "scripts"
    "monitoring"
    "risk_management"
    "tests"
    "docs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_ok "Directory exists: $dir"
    else
        check_error "Directory missing: $dir"
    fi
done

# Check configuration files
echo ""
echo "Checking configuration files..."

if [ -f "config/config.json" ]; then
    check_ok "config.json exists"

    # Validate JSON
    if python3 -m json.tool config/config.json > /dev/null 2>&1; then
        check_ok "config.json is valid JSON"
    else
        check_error "config.json has syntax errors"
    fi
else
    check_error "config.json missing"
fi

if [ -f "config/config_bybit_testnet.json" ]; then
    check_ok "config_bybit_testnet.json exists"

    # Validate JSON
    if python3 -m json.tool config/config_bybit_testnet.json > /dev/null 2>&1; then
        check_ok "config_bybit_testnet.json is valid JSON"
    else
        check_error "config_bybit_testnet.json has syntax errors"
    fi
else
    check_error "config_bybit_testnet.json missing"
fi

# Check strategy file
echo ""
echo "Checking strategy files..."

if [ -f "user_data/strategies/MomentumMeanReversion.py" ]; then
    check_ok "MomentumMeanReversion strategy exists"

    # Check Python syntax
    if python3 -m py_compile user_data/strategies/MomentumMeanReversion.py 2>/dev/null; then
        check_ok "Strategy has valid Python syntax"
    else
        check_error "Strategy has syntax errors"
    fi
else
    check_error "MomentumMeanReversion strategy missing"
fi

# Check scripts
echo ""
echo "Checking helper scripts..."

SCRIPTS=(
    "scripts/download_data.sh"
    "scripts/run_backtest.sh"
    "scripts/run_hyperopt.sh"
    "scripts/start_dryrun.sh"
    "scripts/start_testnet.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            check_ok "Script exists and is executable: $script"
        else
            check_warning "Script exists but not executable: $script (run: chmod +x $script)"
        fi
    else
        check_error "Script missing: $script"
    fi
done

# Check risk management modules
echo ""
echo "Checking risk management modules..."

if [ -f "risk_management/position_sizing.py" ]; then
    check_ok "Position sizing module exists"

    if python3 -m py_compile risk_management/position_sizing.py 2>/dev/null; then
        check_ok "Position sizing has valid syntax"
    else
        check_error "Position sizing has syntax errors"
    fi
else
    check_error "Position sizing module missing"
fi

if [ -f "risk_management/drawdown_protection.py" ]; then
    check_ok "Drawdown protection module exists"

    if python3 -m py_compile risk_management/drawdown_protection.py 2>/dev/null; then
        check_ok "Drawdown protection has valid syntax"
    else
        check_error "Drawdown protection has syntax errors"
    fi
else
    check_error "Drawdown protection module missing"
fi

# Check monitoring modules
echo ""
echo "Checking monitoring modules..."

if [ -f "monitoring/metrics.py" ]; then
    check_ok "Metrics module exists"
else
    check_error "Metrics module missing"
fi

if [ -f "monitoring/dashboard.py" ]; then
    check_ok "Dashboard module exists"
else
    check_error "Dashboard module missing"
fi

# Check test files
echo ""
echo "Checking test files..."

if [ -f "tests/test_strategy.py" ]; then
    check_ok "Strategy tests exist"
else
    check_warning "Strategy tests missing"
fi

if [ -f "tests/test_risk_management.py" ]; then
    check_ok "Risk management tests exist"
else
    check_warning "Risk management tests missing"
fi

# Check documentation
echo ""
echo "Checking documentation..."

DOCS=(
    "README.md"
    "QUICKSTART.md"
    "PROJECT_SUMMARY.md"
    "docs/RESEARCH_PHASE1.md"
    "docs/PHASE2_STRATEGY_SELECTION.md"
    "docs/FREQTRADE_SETUP.md"
    "docs/BYBIT_TESTNET_SETUP.md"
    "docs/DEPLOYMENT_GUIDE.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        check_ok "Documentation exists: $doc"
    else
        check_error "Documentation missing: $doc"
    fi
done

# Check .env configuration
echo ""
echo "Checking environment configuration..."

if [ -f ".env.example" ]; then
    check_ok ".env.example exists"
else
    check_warning ".env.example missing"
fi

if [ -f ".env" ]; then
    check_ok ".env file exists (API keys configured)"

    # Check for required variables
    source .env

    if [ -n "$BYBIT_TESTNET_API_KEY" ]; then
        check_ok "BYBIT_TESTNET_API_KEY is set"
    else
        check_warning "BYBIT_TESTNET_API_KEY not set"
    fi

    if [ -n "$BYBIT_TESTNET_API_SECRET" ]; then
        check_ok "BYBIT_TESTNET_API_SECRET is set"
    else
        check_warning "BYBIT_TESTNET_API_SECRET not set"
    fi
else
    check_warning ".env file not found (API keys not configured)"
fi

# Check .gitignore
echo ""
echo "Checking security..."

if [ -f ".gitignore" ]; then
    check_ok ".gitignore exists"

    # Check that .env is in .gitignore
    if grep -q "^\.env$" .gitignore; then
        check_ok ".env is in .gitignore (secrets protected)"
    else
        check_error ".env NOT in .gitignore (SECURITY RISK!)"
    fi
else
    check_error ".gitignore missing (SECURITY RISK!)"
fi

# Run tests if pytest is available
echo ""
echo "Running unit tests..."

if [ -d "venv" ]; then
    source venv/bin/activate

    if command -v pytest &> /dev/null; then
        check_ok "pytest installed"

        echo ""
        echo "Running tests..."
        if pytest tests/ -v --tb=short 2>&1 | tee /tmp/pytest_output.txt; then
            check_ok "All tests passed!"
        else
            FAILED_TESTS=$(grep "FAILED" /tmp/pytest_output.txt | wc -l)
            if [ $FAILED_TESTS -gt 0 ]; then
                check_error "$FAILED_TESTS test(s) failed"
            else
                check_warning "Some tests had issues (check output above)"
            fi
        fi
    else
        check_warning "pytest not installed (run: pip install pytest)"
    fi

    deactivate
fi

# Final summary
echo ""
echo "========================================="
echo "Verification Summary"
echo "========================================="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo "✅ All checks passed! Installation is complete."
        echo ""
        echo "Next steps:"
        echo "1. Configure API keys in .env file (if not done)"
        echo "2. Download historical data: ./scripts/download_data.sh"
        echo "3. Run backtest: ./scripts/run_backtest.sh"
        echo "4. See QUICKSTART.md for detailed instructions"
    else
        echo "⚠️  Installation complete with $WARNINGS warning(s)."
        echo "Review warnings above. Most are optional components."
    fi
else
    echo "❌ Installation has $ERRORS error(s)."
    echo "Please fix errors above before proceeding."
    exit 1
fi

echo "========================================="
