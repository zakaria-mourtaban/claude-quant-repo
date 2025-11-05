#!/bin/bash
# Freqtrade Installation Script for Crypto Trading Bot
# This script automates the installation of Freqtrade and its dependencies

set -e  # Exit on error

echo "========================================="
echo "Crypto Trading Bot - Freqtrade Installer"
echo "========================================="
echo ""

# Check if running in project directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python 3.11+ required. Found: $PYTHON_VERSION"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install TA-Lib (if not installed)
echo ""
echo "Checking TA-Lib installation..."
if ! python -c "import talib" 2>/dev/null; then
    echo "⚠️  TA-Lib not found. Installing system dependencies..."

    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Detected Linux. Installing TA-Lib..."

        # Check if sudo is available
        if command -v sudo &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y build-essential wget libssl-dev libffi-dev python3-dev

            # Download and install TA-Lib
            cd /tmp
            wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
            tar -xzf ta-lib-0.4.0-src.tar.gz
            cd ta-lib/
            ./configure --prefix=/usr
            make
            sudo make install
            cd -
        else
            echo "⚠️  sudo not available. Please install TA-Lib manually:"
            echo "   See: docs/FREQTRADE_SETUP.md"
        fi

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS. Installing TA-Lib..."

        if command -v brew &> /dev/null; then
            brew install ta-lib
        else
            echo "⚠️  Homebrew not found. Please install TA-Lib manually:"
            echo "   brew install ta-lib"
        fi
    else
        echo "⚠️  Unsupported OS. Please install TA-Lib manually."
        echo "   See: docs/FREQTRADE_SETUP.md"
    fi

    # Install Python TA-Lib wrapper
    pip install TA-Lib
    echo "✅ TA-Lib installed"
else
    echo "✅ TA-Lib already installed"
fi

# Install Freqtrade
echo ""
echo "Installing Freqtrade..."
pip install freqtrade

# Install project dependencies
echo ""
echo "Installing project dependencies..."
pip install -r requirements.txt

# Verify installation
echo ""
echo "Verifying installation..."
freqtrade --version

# Create user data directory (if not exists)
if [ ! -d "user_data/strategies" ]; then
    echo ""
    echo "Creating user data directory..."
    freqtrade create-userdir --userdir user_data
fi

echo ""
echo "========================================="
echo "✅ Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Set up Bybit Testnet: See docs/BYBIT_TESTNET_SETUP.md"
echo "3. Download data: ./scripts/download_data.sh"
echo "4. Run backtest: ./scripts/run_backtest.sh"
echo ""
echo "For more information, see: docs/FREQTRADE_SETUP.md"
