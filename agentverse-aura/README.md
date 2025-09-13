# AURA Smart Home Management Agent for FetchAI AgentVerse

🤖 **AURA** is an intelligent smart home management agent designed for the FetchAI AgentVerse platform. It provides proactive weather-based home preparation, voice call notifications, and automated smart home device control.

## 🌟 Features

### Core Capabilities
- **🌡️ Weather Monitoring**: Detects heatwaves and other weather events
- **📞 Voice Calls**: Makes automated voice calls via VAPI integration
- **🏠 Smart Home Control**: Manages thermostat, battery, solar panels, and AC
- **⚡ Energy Management**: Optimizes energy consumption and market sales
- **👥 Homeowner Registration**: Manages registered homeowners and their preferences

### AgentVerse Integration
- **🔗 Native AgentVerse Support**: Built specifically for FetchAI AgentVerse platform
- **🤝 Collaborative Agents**: Can work with other agents in the AgentVerse ecosystem
- **📡 Real-time Communication**: Handles messages and commands from AgentVerse
- **🔄 Autonomous Operation**: Runs independently with proactive monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FetchAI AgentVerse account
- VAPI account (for voice calls)
- Twilio account (for phone numbers)
- xAI API key (for AI responses)

### Installation

1. **Clone and setup**:
```bash
cd agentverse-aura
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp env.example .env
# Edit .env with your API keys
```

3. **Run the agent**:
```bash
python main.py
```

The agent will start on `http://localhost:8000` and be ready for AgentVerse integration.

## 🔧 Configuration

### Environment Variables
```bash
# FetchAI AgentVerse
AGENTVERSE_API_KEY=your_agentverse_api_key
AGENTVERSE_AGENT_ID=your_agent_id

# VAPI (Voice Calls)
VAPI_API_KEY=your_vapi_api_key
VAPI_PHONE_NUMBER_ID=your_phone_number_id

# Twilio (Phone Numbers)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number

# xAI (AI Responses)
XAI_API_KEY=your_xai_api_key
```

### Agent Configuration
Edit `config/agent_config.yaml` to customize:
- Agent behavior and capabilities
- Smart home device settings
- Weather monitoring thresholds
- Voice call preferences

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Agent status and information
- `GET /health` - Health check
- `POST /register` - Register homeowner
- `GET /homeowners` - List registered homeowners
- `GET /home-status` - Get current home status
- `POST /simulate-heatwave` - Trigger heatwave simulation
- `POST /simulation/reset` - Reset simulation state

### AgentVerse Integration
- `POST /agentverse/message` - Handle AgentVerse messages
- `GET /agentverse/capabilities` - Get agent capabilities

### Voice Calls
- `POST /voice-call` - Make voice call

## 🎯 Usage Examples

### Register a Homeowner
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "phone_number": "+1234567890"}'
```

### Simulate Heatwave Response
```bash
curl -X POST "http://localhost:8000/simulate-heatwave"
```

### Get Home Status
```bash
curl "http://localhost:8000/home-status"
```

### AgentVerse Message
```bash
curl -X POST "http://localhost:8000/agentverse/message" \
  -H "Content-Type: application/json" \
  -d '{"content": "register homeowner Jane +1987654321", "source": "agentverse"}'
```

## 🏗️ Architecture

### Agent Components
- **AURAAgent**: Main agent class extending AgentVerse Agent
- **AURAVoiceService**: Handles VAPI voice call integration
- **SmartHomeSimulator**: Simulates smart home device responses
- **Models**: Pydantic models for data validation

### Integration Flow
1. **Weather Event Detection** → Agent monitors for weather events
2. **Homeowner Notification** → Voice calls sent to registered homeowners
3. **Smart Home Response** → Devices automatically adjust (AC, battery, etc.)
4. **Energy Optimization** → Battery charges, energy sold to market
5. **Resolution Call** → Final status update to homeowners

## 🔄 AgentVerse Integration

### Message Handling
The agent responds to natural language commands:
- `"register homeowner John +1234567890"`
- `"simulate heatwave"`
- `"get home status"`
- `"list homeowners"`
- `"reset simulation"`

### Collaborative Features
- Can receive messages from other agents
- Can send responses back to AgentVerse
- Maintains state across interactions
- Supports real-time updates

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/
```

### Manual Testing
```bash
# Test registration
python -c "
import asyncio
from src.aura_agent import AURAAgent
async def test():
    agent = AURAAgent()
    result = await agent.register_homeowner('Test User', '+1234567890')
    print(result)
asyncio.run(test())
"
```

## 🚀 Deployment

### AgentVerse Deployment
1. **Build the agent**:
```bash
python -m build
```

2. **Deploy to AgentVerse**:
   - Upload to AgentVerse platform
   - Configure agent settings
   - Set environment variables
   - Activate the agent

### Local Development
```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Monitoring

### Health Checks
- `GET /health` - Agent health status
- Service status monitoring
- Performance metrics
- Error logging

### Logs
- Structured JSON logging
- Request/response tracking
- Error monitoring
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FetchAI** for the AgentVerse platform
- **VAPI** for voice call integration
- **Twilio** for phone number services
- **xAI** for AI capabilities

---

**Built with ❤️ for the FetchAI AgentVerse ecosystem**
