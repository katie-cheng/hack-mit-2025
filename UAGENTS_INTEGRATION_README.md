# AURA uAgents Integration

This document describes how the AURA Smart Home Management System has been integrated with the uAgents ecosystem, enabling seamless communication and deployment across different AI agent architectures.

## 🚀 Overview

The AURA system's three main agents have been wrapped with uAgents adapters, allowing them to:

- **Communicate** across the uAgents network
- **Discover** each other automatically
- **Deploy** independently on different machines
- **Scale** horizontally as needed
- **Integrate** with other uAgents ecosystem components

## 🤖 AURA uAgents

### 1. Threat Assessment Agent (The Oracle)
- **uAgent Name**: `threat_assessment_oracle`
- **Port**: 8001
- **Purpose**: Analyzes environmental threats and grid conditions
- **Input**: `ThreatAnalysisRequestModel`
- **Output**: `ThreatAnalysisResultModel`

### 2. Home State Agent (Digital Twin)
- **uAgent Name**: `home_state_digital_twin`
- **Port**: 8002
- **Purpose**: Manages home device states and executes actions
- **Input**: `HomeStateRequestModel`
- **Output**: `HomeStateResultModel`

### 3. Agent Orchestrator (Coordinator)
- **uAgent Name**: `aura_orchestrator`
- **Port**: 8000
- **Purpose**: Coordinates the complete threat-to-action pipeline
- **Input**: `ThreatToActionRequestModel`
- **Output**: `ThreatToActionResultModel`

## 📦 Installation

```bash
# Install uAgents dependencies
pip install -r services/backend/requirements-uagents.txt

# Install uAgents (if not already installed)
pip install uagents uagents-protocol
```

## 🚀 Quick Start

### Option 1: Complete System
```python
from uagents_adapters import start_aura_uagents_system

# Start all AURA agents
aura_system = await start_aura_uagents_system()

# Get agent addresses
addresses = aura_system.get_agent_addresses()
print(f"Threat Agent: {addresses['threat_assessment']}")
print(f"Home Agent: {addresses['home_state']}")
print(f"Orchestrator: {addresses['orchestrator']}")
```

### Option 2: Individual Agents
```python
from uagents_adapters import ThreatAssessmentUAgent, HomeStateUAgent

# Start individual agents
threat_agent = ThreatAssessmentUAgent(port=8001)
home_agent = HomeStateUAgent(port=8002)

await asyncio.gather(
    threat_agent.start(),
    home_agent.start()
)

# Get agent addresses
threat_address = threat_agent.get_agent_address()
home_address = home_agent.get_agent_address()
```

## 💬 Communication Examples

### Threat Analysis Request
```python
from uagents import Agent, Context
from uagents_adapters import ThreatAnalysisRequestModel, ThreatAnalysisResultModel

# Create client agent
client = Agent(name="client", seed="client_seed")

# Send threat analysis request
request = ThreatAnalysisRequestModel(
    location="Austin, TX",
    include_weather=True,
    include_grid=True,
    include_research=False
)

response = await client.send_and_wait(
    threat_agent_address,
    request,
    response_type=ThreatAnalysisResultModel,
    timeout=30.0
)

print(f"Threat Level: {response.analysis['overall_threat_level']}")
print(f"Threat Types: {response.analysis['threat_types']}")
```

### Home State Control
```python
from uagents_adapters import HomeStateRequestModel, HomeStateResultModel

# Send home state request
request = HomeStateRequestModel(
    actions=[
        {
            "device_type": "thermostat",
            "action_type": "set",
            "parameters": {"temperature": 68.0, "mode": "cool"}
        },
        {
            "device_type": "battery",
            "action_type": "set", 
            "parameters": {"soc_percent": 100.0, "backup_reserve": 30.0}
        }
    ]
)

response = await client.send_and_wait(
    home_agent_address,
    request,
    response_type=HomeStateResultModel,
    timeout=30.0
)

print(f"Actions Executed: {len(response.action_results)}")
print(f"Home State Updated: {response.success}")
```

### Complete Pipeline
```python
from uagents_adapters import ThreatToActionRequestModel, ThreatToActionResultModel

# Send complete threat-to-action request
request = ThreatToActionRequestModel(
    location="Austin, TX",
    include_research=False,
    scenario="heatwave"
)

response = await client.send_and_wait(
    orchestrator_address,
    request,
    response_type=ThreatToActionResultModel,
    timeout=60.0
)

print(f"Pipeline Success: {response.success}")
print(f"Threat Analysis: {response.threat_analysis is not None}")
print(f"Home Actions: {len(response.home_actions)}")
print(f"Home State: {response.home_state is not None}")
```

## 🧪 Testing

### Run Integration Tests
```bash
# Test complete uAgents integration
python test_uagents_integration.py

# Test usage examples
python example_uagents_usage.py
```

### Test Individual Components
```bash
# Test original pipeline (without uAgents)
python test_aura_pipeline.py

# Test dynamic actions
python test_dynamic_actions.py
```

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI API key for LLM features
export OPENAI_API_KEY="your-openai-api-key"

# Agent configuration
export THREAT_AGENT_PORT=8001
export HOME_AGENT_PORT=8002
export ORCHESTRATOR_PORT=8000
```

### Custom Agent Configuration
```python
# Custom threat assessment agent
threat_agent = ThreatAssessmentUAgent(
    agent_name="custom_threat_agent",
    seed="custom_seed_phrase",
    port=8001,
    openai_api_key="your-api-key"
)

# Custom home state agent
home_agent = HomeStateUAgent(
    agent_name="custom_home_agent", 
    seed="custom_home_seed",
    port=8002,
    openai_api_key="your-api-key"
)
```

## 🌐 Network Communication

### Agent Discovery
uAgents automatically handles agent discovery through the network. Agents can find each other using:

- **Agent Names**: `threat_assessment_oracle`, `home_state_digital_twin`, `aura_orchestrator`
- **Agent Addresses**: Unique addresses generated from seed phrases
- **Port Numbers**: 8000 (orchestrator), 8001 (threat), 8002 (home)

### Message Routing
```python
# Send message by name (if discovery is enabled)
await client.send_by_name("threat_assessment_oracle", request)

# Send message by address (direct communication)
await client.send(threat_agent_address, request)
```

## 🚀 Deployment

### Local Development
```bash
# Start all agents locally
python -m uagents_adapters

# Or start individually
python -c "
import asyncio
from uagents_adapters import start_aura_uagents_system
asyncio.run(start_aura_uagents_system())
"
```

### Production Deployment
```bash
# Deploy on different machines
# Machine 1: Threat Assessment Agent
python -c "from uagents_adapters import ThreatAssessmentUAgent; asyncio.run(ThreatAssessmentUAgent().start())"

# Machine 2: Home State Agent  
python -c "from uagents_adapters import HomeStateUAgent; asyncio.run(HomeStateUAgent().start())"

# Machine 3: Orchestrator Agent
python -c "from uagents_adapters import AgentOrchestratorUAgent; asyncio.run(AgentOrchestratorUAgent().start())"
```

## 🔍 Monitoring and Debugging

### Agent Status
```python
# Check agent status
print(f"Threat Agent Address: {threat_agent.get_agent_address()}")
print(f"Home Agent Address: {home_agent.get_agent_address()}")
print(f"Orchestrator Address: {orchestrator.get_agent_address()}")
```

### Logging
uAgents provides built-in logging for message passing and agent communication:

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Benefits of uAgents Integration

1. **Decoupled Architecture**: Agents can run independently
2. **Network Communication**: Agents can communicate across machines
3. **Automatic Discovery**: Agents find each other automatically
4. **Scalability**: Scale individual agents as needed
5. **Fault Tolerance**: Individual agent failures don't crash the system
6. **Ecosystem Integration**: Works with other uAgents ecosystem components
7. **Production Ready**: Built for real-world deployment

## 🔗 Integration with Other Frameworks

The uAgents adapters enable integration with:

- **LangChain**: For LLM-powered threat analysis
- **LangGraph**: For complex orchestration workflows
- **CrewAI**: For multi-agent collaboration
- **Custom Agents**: Any uAgents-compatible agent

## 📚 Next Steps

1. **Deploy to Production**: Use the uAgents ecosystem for production deployment
2. **Add More Agents**: Create additional specialized agents
3. **Integrate External Systems**: Connect with other uAgents ecosystem components
4. **Monitor and Scale**: Use uAgents monitoring tools for production management

The AURA system is now fully integrated with the uAgents ecosystem, ready for production deployment and scaling! 🚀
