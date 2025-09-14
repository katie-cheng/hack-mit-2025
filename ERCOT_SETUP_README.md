# ERCOT API Setup Guide

This guide explains how to set up ERCOT API authentication for the live weather and grid monitoring system.

## 🔐 ERCOT Authentication Requirements

ERCOT uses OAuth2 authentication with the following credentials:
- **Username**: Your ERCOT API account username
- **Password**: Your ERCOT API account password  
- **Subscription Key**: Your ERCOT API subscription key

## 📋 Setup Steps

### 1. Get ERCOT API Credentials

1. Go to [ERCOT Public API](https://www.ercot.com/mp/data-products/data-product-details?id=NP4-785-ER)
2. Sign up for an account
3. Request API access
4. Get your credentials:
   - Username
   - Password
   - Subscription Key

### 2. Set Environment Variables

```bash
# Set your ERCOT credentials
export ERCOT_USERNAME="your_username_here"
export ERCOT_PASSWORD="your_password_here"
export ERCOT_SUBSCRIPTION_KEY="your_subscription_key_here"

# Verify they're set
echo $ERCOT_USERNAME
echo $ERCOT_PASSWORD
echo $ERCOT_SUBSCRIPTION_KEY
```

### 3. Test Authentication

```bash
# Test ERCOT authentication
python test_ercot_auth.py

# Test token fetcher
python ercot_token_fetcher.py
```

### 4. Run Live Monitor

```bash
# Run the live monitoring system
python live_weather_grid_monitor.py
```

## 🔧 How It Works

### OAuth2 Authentication Flow

1. **Token Request**: The system sends credentials to ERCOT's OAuth2 endpoint
2. **Access Token**: ERCOT returns an access token and expiration time
3. **API Calls**: All subsequent API calls use the Bearer token
4. **Token Refresh**: Tokens are automatically refreshed when they expire

### API Endpoints Used

- **Authentication**: `https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token`
- **System Demand**: `https://api.ercot.com/api/v1/system/demand`
- **System Load**: `https://api.ercot.com/api/v1/system/load`
- **Price Data**: `https://api.ercot.com/api/v1/prices/hb_houston`
- **System Status**: `https://api.ercot.com/api/v1/system/status`

### Headers Used

```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Ocp-Apim-Subscription-Key": subscription_key,
    "Content-Type": "application/json"
}
```

## 🚨 Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check your username/password
2. **403 Forbidden**: Check your subscription key
3. **404 Not Found**: API endpoint may have changed
4. **429 Too Many Requests**: Rate limiting - wait and retry

### Debug Steps

1. **Test Token Fetcher**:
   ```bash
   python ercot_token_fetcher.py
   ```

2. **Check Environment Variables**:
   ```bash
   env | grep ERCOT
   ```

3. **Test Individual Components**:
   ```bash
   python test_ercot_auth.py
   ```

4. **Check Logs**: Look for authentication success/failure messages

## 📊 Expected Output

When working correctly, you should see:

```
🔐 Testing ERCOT OAuth2 Authentication
==================================================
✅ ERCOT client initialized successfully
🔄 Testing grid data fetch...
✅ ERCOT authentication successful
✅ Grid data fetch successful!
🏭 Authority: ERCOT
⚡ Demand: 75,000 MW
💰 Price: $50.00/MWh
🔧 Status: Normal
```

## 🔄 Token Management

The system automatically handles token management:

- **Token Fetching**: Tokens are fetched on first API call
- **Token Caching**: Tokens are cached in memory
- **Token Refresh**: Tokens are refreshed when they expire
- **Error Handling**: Falls back to default data if authentication fails

## 📝 Security Notes

- **Never commit credentials** to version control
- **Use environment variables** for credential storage
- **Rotate credentials** regularly
- **Monitor API usage** to avoid rate limits

## 🆘 Support

If you encounter issues:

1. Check the [ERCOT API Documentation](https://www.ercot.com/mp/data-products/data-product-details?id=NP4-785-ER)
2. Verify your credentials are correct
3. Check if your API access is still active
4. Review the error logs for specific error messages

## 🎯 Next Steps

Once ERCOT authentication is working:

1. Run the full live monitoring system
2. Test the threat analysis with real grid data
3. Set up monitoring and alerting
4. Integrate with your smart home system
