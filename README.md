# AURA

AI-powered smart home management system built for HackMIT Hackathon.

## Overview

AURA is a proactive smart home management system that protects homes from weather events through intelligent alerts and automated responses. The system monitors weather conditions, proactively alerts homeowners via phone calls, and automatically manages home systems to optimize comfort and energy trading.

## Features

- **Weather Intelligence**: AI analyzes weather patterns and detects potential events
- **Proactive Alerts**: Voice calls to homeowners with intelligent conversation capabilities
- **Automated Response**: Smart systems pre-cool homes, charge batteries, and optimize energy usage
- **Energy Trading**: Automatic energy sales during peak demand periods
- **EOC Dashboard**: Real-time monitoring and simulation control center

## Demo Flow

1. **QR Registration**: Judges scan QR code to register their home with name and phone number
2. **Heatwave Simulation**: Click "Simulate Heatwave" button on EOC Dashboard
3. **Call #1 - Warning**: Phone rings with AI alert about 92% probability heatwave at 4 PM
4. **Live Visualization**: Dashboard shows automated response sequence (AC pre-cooling, battery charging, energy sale)
5. **Call #2 - Resolution**: Final report call with results and profit information

## Architecture

- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Backend**: FastAPI with in-memory storage and real-time simulation
- **AI Services**: xAI Grok API for intelligent voice conversations
- **Voice**: VAPI.ai for voice call delivery and two-way communication
- **Simulation**: Real-time smart home device state management

## Setup

### Prerequisites

- Node.js 18+
- Python 3.10+
- API keys for xAI and VAPI

### Environment Variables

```bash
# xAI API
XAI_API_KEY=your_xai_api_key

# VAPI (Voice calls)
VAPI_API_KEY=your_vapi_key
VAPI_PHONE_NUMBER_ID=your_phone_id
```

### Installation

1. Clone the repository
2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend:
   ```bash
   cd services/backend
   python -m backend
   ```
5. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

## Usage

1. **Home Registration**: Visit `/register` to register a home with QR code generation
2. **EOC Dashboard**: Visit `/dashboard` to monitor smart home systems and simulate events
3. **Demo Flow**: Use the dashboard to simulate heatwave events and watch the automated response

## API Endpoints

- `POST /register` - Homeowner registration
- `GET /homeowners` - List all registered homeowners
- `GET /home-status` - Get current smart home status
- `POST /simulate-heatwave` - Initiate heatwave simulation
- `POST /simulation/reset` - Reset simulation to initial state

## Smart Home Devices

- **Battery**: Charge level monitoring and solar charging simulation
- **Thermostat**: Temperature control and AC operation
- **Market**: Energy trading status and profit tracking

## License

Built for HackMIT Hackathon 2024.