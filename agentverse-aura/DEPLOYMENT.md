# AURA AgentVerse Deployment Guide

## 🚀 Quick Deployment to FetchAI AgentVerse

### Prerequisites
1. **FetchAI AgentVerse Account**: Sign up at [AgentVerse](https://agentverse.ai)
2. **API Keys**: Gather your VAPI, Twilio, and xAI API keys
3. **Python Environment**: Python 3.8+ with pip

### Step 1: Prepare Your Agent

1. **Clone/Download** the `agentverse-aura` folder
2. **Install Dependencies**:
```bash
cd agentverse-aura
pip install -r requirements.txt
```

3. **Configure Environment**:
```bash
cp env.example .env
# Edit .env with your API keys
```

### Step 2: Test Locally

```bash
# Test the agent works
python -c "
import asyncio
from src.aura_agent import AURAAgent

async def test():
    agent = AURAAgent()
    result = await agent.register_homeowner('Test User', '+1234567890')
    print(f'✅ {result.message}')

asyncio.run(test())
"
```

### Step 3: Deploy to AgentVerse

#### Option A: Direct Upload
1. **Zip the agent**:
```bash
zip -r aura-agent.zip . -x "*.pyc" "__pycache__/*" ".git/*"
```

2. **Upload to AgentVerse**:
   - Go to your AgentVerse dashboard
   - Click "Create New Agent"
   - Upload `aura-agent.zip`
   - Configure agent settings

#### Option B: Git Repository
1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "AURA Smart Home Agent"
git remote add origin https://github.com/yourusername/aura-agentverse.git
git push -u origin main
```

2. **Connect to AgentVerse**:
   - In AgentVerse dashboard, select "Import from Git"
   - Enter your repository URL
   - Configure deployment settings

### Step 4: Configure Agent Settings

In your AgentVerse dashboard:

1. **Agent Configuration**:
   - Name: `AURA`
   - Description: `Smart Home Management Agent`
   - Type: `Smart Home Manager`

2. **Environment Variables**:
   ```
   VAPI_API_KEY=your_vapi_key
   VAPI_PHONE_NUMBER_ID=your_phone_id
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_number
   XAI_API_KEY=your_xai_key
   ```

3. **Capabilities**:
   - ✅ Voice Calls
   - ✅ Smart Home Control
   - ✅ Weather Monitoring
   - ✅ Energy Management
   - ✅ Homeowner Registration

### Step 5: Test Deployment

1. **Health Check**:
```bash
curl https://your-agent-url.agentverse.ai/health
```

2. **Register Homeowner**:
```bash
curl -X POST "https://your-agent-url.agentverse.ai/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "phone_number": "+1234567890"}'
```

3. **Simulate Heatwave**:
```bash
curl -X POST "https://your-agent-url.agentverse.ai/simulate-heatwave"
```

### Step 6: AgentVerse Integration

Your agent is now available in the AgentVerse ecosystem:

1. **Message Handling**: Other agents can send messages to your AURA agent
2. **Collaborative Features**: Your agent can work with other agents
3. **Real-time Updates**: Status updates are shared across the network
4. **Voice Integration**: Voice calls work through VAPI integration

### Example AgentVerse Messages

```json
{
  "content": "register homeowner John +1234567890",
  "source": "agentverse",
  "target": "AURA"
}
```

```json
{
  "content": "simulate heatwave",
  "source": "weather-agent",
  "target": "AURA"
}
```

## 🎯 Demo Script for Judges

### 1. Show Agent Registration
```bash
# Register a homeowner
curl -X POST "https://your-agent-url.agentverse.ai/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Judge", "phone_number": "+1234567890"}'
```

### 2. Show Home Status
```bash
# Get current home status
curl "https://your-agent-url.agentverse.ai/home-status"
```

### 3. Trigger Heatwave Simulation
```bash
# Start the full demo
curl -X POST "https://your-agent-url.agentverse.ai/simulate-heatwave"
```

### 4. Show AgentVerse Integration
```bash
# Send message through AgentVerse
curl -X POST "https://your-agent-url.agentverse.ai/agentverse/message" \
  -H "Content-Type: application/json" \
  -d '{"content": "get home status", "source": "agentverse", "target": "AURA"}'
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **API Key Issues**: Verify all environment variables are set
3. **Voice Call Failures**: Check VAPI and Twilio configuration
4. **AgentVerse Connection**: Ensure agent is properly deployed

### Debug Mode

```bash
# Run with debug logging
python main.py --debug
```

### Health Check

```bash
# Check agent health
curl https://your-agent-url.agentverse.ai/health
```

## 📊 Monitoring

### Agent Metrics
- Homeowner registrations
- Voice calls made
- Simulations completed
- Energy savings generated

### Performance
- Response times
- Success rates
- Error rates
- Resource usage

## 🎉 Success!

Your AURA agent is now live on FetchAI AgentVerse and ready to:
- ✅ Manage smart homes intelligently
- ✅ Make voice calls to homeowners
- ✅ Collaborate with other agents
- ✅ Win the FetchAI track prize! 🏆

---

**Built with ❤️ for FetchAI AgentVerse**
