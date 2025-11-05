# Bybit Testnet Setup Guide

This guide walks you through creating a Bybit Testnet account for demo trading with virtual funds.

## Why Bybit Testnet?

- **$50,000 Virtual Balance** (highest among major exchanges)
- **355 Trading Assets** (spot + derivatives)
- **No Real Money Risk** (perfect for testing strategies)
- **Real Market Conditions** (uses live market data)
- **API Access** (test full bot integration)

---

## Step 1: Create Bybit Testnet Account

### 1.1 Visit Bybit Testnet Website

Go to: **https://testnet.bybit.com**

**Important**: This is different from the main Bybit website (bybit.com). The testnet is a separate environment for demo trading.

### 1.2 Sign Up

1. Click **Sign Up** in the top-right corner
2. Choose sign-up method:
   - **Email** (recommended)
   - Phone number
   - Google account

3. For email registration:
   - Enter your email address
   - Create a strong password
   - Verify your email (check inbox for verification code)

4. Complete registration

**Note**: You can use the same email for both regular Bybit and Testnet (they're separate systems).

---

## Step 2: Access Demo Trading

### 2.1 Log In to Testnet

1. Go to **https://testnet.bybit.com**
2. Log in with your testnet credentials
3. You should see a banner indicating "Testnet" environment

### 2.2 Verify Virtual Balance

1. Click on **Assets** in the top menu
2. Navigate to **Spot Wallet** or **Derivatives Wallet**
3. You should see virtual funds:
   - **USDT**: ~10,000 (for spot trading)
   - **USDC**: ~10,000 (for derivatives)
   - Other assets available on request

**Note**: If you don't see funds, click **"Request Test Funds"** or contact support.

---

## Step 3: Create API Keys

API keys allow your bot to place trades programmatically.

### 3.1 Navigate to API Management

1. Click on **Profile Icon** (top-right)
2. Select **API Management**
3. Click **Create New Key**

### 3.2 Configure API Key

**API Key Settings**:
1. **API Key Name**: `Freqtrade-Demo-Bot` (or any descriptive name)
2. **Permissions**: Enable:
   - ✅ **Read** (view account info, positions, orders)
   - ✅ **Trade** (place and cancel orders)
   - ❌ **Withdraw** (keep disabled for security)
3. **IP Restriction** (optional but recommended):
   - If you have a static IP, enter it here
   - For testing, you can leave it unrestricted
4. **Confirm** with 2FA (if enabled)

### 3.3 Save API Credentials

After creation, you'll see:
- **API Key**: `xxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **API Secret**: `yyyyyyyyyyyyyyyyyyyyyyyyyyyy`

**CRITICAL**:
- Copy both immediately (secret is shown only once)
- Store securely (use password manager or `.env` file)
- Never commit to Git or share publicly

---

## Step 4: Configure Freqtrade for Bybit Testnet

### 4.1 Create Environment File

Create `.env` file in project root:

```bash
cd ~/claude-quant-repo
nano .env  # or use your preferred text editor
```

Add:
```bash
# Bybit Testnet API Credentials
BYBIT_TESTNET_API_KEY=your_api_key_here
BYBIT_TESTNET_API_SECRET=your_api_secret_here

# Telegram Bot (optional, set up later)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Dashboard Password
DASHBOARD_PASSWORD=your_secure_password_here
```

**Save and close** (Ctrl+O, Enter, Ctrl+X in nano)

### 4.2 Secure .env File

```bash
# Add to .gitignore (prevent accidental commits)
echo ".env" >> .gitignore

# Restrict permissions (Linux/macOS)
chmod 600 .env
```

### 4.3 Update Freqtrade Config

Edit `config/config_bybit_testnet.json`:

```json
{
  "exchange": {
    "name": "bybit",
    "key": "${BYBIT_TESTNET_API_KEY}",
    "secret": "${BYBIT_TESTNET_API_SECRET}",
    "ccxt_config": {
      "enableRateLimit": true,
      "urls": {
        "api": {
          "public": "https://api-testnet.bybit.com",
          "private": "https://api-testnet.bybit.com"
        }
      }
    }
  }
}
```

**Note**: The `${VARIABLE}` syntax allows Freqtrade to read from environment variables.

---

## Step 5: Test API Connection

### 5.1 Test with Python Script

Create `scripts/test_bybit_connection.py`:

```python
import ccxt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Bybit Testnet
bybit = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
    'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
    'enableRateLimit': True,
    'urls': {
        'api': {
            'public': 'https://api-testnet.bybit.com',
            'private': 'https://api-testnet.bybit.com',
        }
    }
})

try:
    # Test: Fetch account balance
    balance = bybit.fetch_balance()
    print("✅ Connection successful!")
    print("\nAccount Balance:")
    for currency, amount in balance['total'].items():
        if amount > 0:
            print(f"  {currency}: {amount}")

    # Test: Fetch market data
    ticker = bybit.fetch_ticker('BTC/USDT')
    print(f"\n✅ Market data access successful!")
    print(f"BTC/USDT Price: ${ticker['last']:,.2f}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run:
```bash
python scripts/test_bybit_connection.py
```

**Expected Output**:
```
✅ Connection successful!

Account Balance:
  USDT: 10000.0
  BTC: 0.5

✅ Market data access successful!
BTC/USDT Price: $43,250.50
```

### 5.2 Test with Freqtrade

```bash
freqtrade test-pairlist --config config/config_bybit_testnet.json
```

**Expected Output**:
```
Pairs: BTC/USDT, ETH/USDT, SOL/USDT, ...
```

---

## Step 6: Place Test Trade (Manual)

Before running the bot, verify you can place trades manually:

### 6.1 Via Bybit Testnet Web Interface

1. Go to **https://testnet.bybit.com**
2. Navigate to **Spot Trading**
3. Select **BTC/USDT** pair
4. Place a small **Limit Buy** order:
   - Price: Slightly below current market
   - Quantity: 0.001 BTC (minimal amount)
5. Verify order appears in **Open Orders**
6. Cancel the order

### 6.2 Via Python Script

Create `scripts/test_place_order.py`:

```python
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

bybit = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
    'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
    'enableRateLimit': True,
    'urls': {
        'api': {
            'public': 'https://api-testnet.bybit.com',
            'private': 'https://api-testnet.bybit.com',
        }
    }
})

try:
    # Fetch current price
    ticker = bybit.fetch_ticker('BTC/USDT')
    current_price = ticker['last']

    # Place limit buy order 5% below current price
    order_price = current_price * 0.95
    order_quantity = 0.001  # Minimal BTC amount

    print(f"Current BTC Price: ${current_price:,.2f}")
    print(f"Placing limit buy at: ${order_price:,.2f}")
    print(f"Quantity: {order_quantity} BTC")

    order = bybit.create_limit_buy_order('BTC/USDT', order_quantity, order_price)
    print(f"\n✅ Order placed successfully!")
    print(f"Order ID: {order['id']}")

    # Cancel the order immediately
    bybit.cancel_order(order['id'], 'BTC/USDT')
    print(f"✅ Order canceled successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
```

Run:
```bash
python scripts/test_place_order.py
```

**Expected Output**:
```
Current BTC Price: $43,250.50
Placing limit buy at: $41,087.98
Quantity: 0.001 BTC

✅ Order placed successfully!
Order ID: 1234567890abcdef
✅ Order canceled successfully!
```

---

## Step 7: Monitor & Manage Testnet Account

### 7.1 Web Interface

- **Trading**: https://testnet.bybit.com/trade/spot/BTC/USDT
- **Assets**: https://testnet.bybit.com/user/assets
- **Order History**: https://testnet.bybit.com/user/orders
- **API Management**: https://testnet.bybit.com/user/api-management

### 7.2 Request Additional Test Funds

If you run out of virtual funds:
1. Go to **Assets** → **Request Test Funds**
2. Or contact Bybit support via testnet chat

### 7.3 Reset API Keys (If Compromised)

1. Go to **API Management**
2. Delete old API key
3. Create new API key
4. Update `.env` file with new credentials

---

## Step 8: Best Practices

### Security
- ✅ **Keep API secret secure** (never commit to Git)
- ✅ **Disable withdrawal permissions** on API keys
- ✅ **Use IP restrictions** if possible
- ✅ **Enable 2FA** on your account
- ✅ **Regularly rotate API keys** (every 90 days)

### Testing
- ✅ **Start with minimal position sizes** (0.001 BTC, 1 USDT)
- ✅ **Test order placement manually** before running bot
- ✅ **Monitor first 24 hours closely** after bot deployment
- ✅ **Use dry-run mode first** (Freqtrade simulated execution)

### Rate Limits
- Bybit Testnet has rate limits (similar to production)
- Freqtrade handles this with `enableRateLimit: true`
- Avoid spamming orders (can lead to temporary bans)

---

## Troubleshooting

### Issue: "Invalid API key"

**Solution**:
- Verify API key copied correctly (no extra spaces)
- Check `.env` file is in project root
- Restart terminal (reload environment variables)
- Ensure testnet URL is used (not production)

### Issue: "Insufficient balance"

**Solution**:
- Request additional test funds via web interface
- Verify you're in the correct wallet (spot vs. derivatives)

### Issue: "Trading not allowed"

**Solution**:
- Check API key has **Trade** permission enabled
- Verify trading pair is available on testnet
- Some pairs may be restricted

### Issue: "Rate limit exceeded"

**Solution**:
- Wait 60 seconds
- Ensure `enableRateLimit: true` in config
- Reduce order frequency in strategy

---

## What's Next?

✅ Bybit Testnet account created
✅ API keys configured securely
✅ Freqtrade connected to Bybit
✅ Test trades executed successfully

**Next Steps**:
1. [ ] Implement first strategy (Momentum + Mean Reversion)
2. [ ] Run backtests on historical data
3. [ ] Optimize parameters with Hyperopt
4. [ ] Deploy to Bybit Testnet for demo trading
5. [ ] Monitor performance for 8-12 weeks

---

## Resources

- [Bybit Testnet Website](https://testnet.bybit.com)
- [Bybit API Documentation](https://bybit-exchange.github.io/docs/v5/intro)
- [CCXT Bybit Documentation](https://docs.ccxt.com/en/latest/exchange-markets.html#bybit)
- [Freqtrade Bybit Exchange Guide](https://www.freqtrade.io/en/stable/exchanges/)

---

**Status**: Bybit Testnet setup complete. You're ready to start demo trading!
