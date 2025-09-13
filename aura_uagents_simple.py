#!/usr/bin/env python3
"""
AURA uAgents Integration using the LangchainRegisterTool approach.
This is a simplified version that focuses on registering our LangChain-based agents
as uAgents using the pattern from your example.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

# Add backend directory to path
backend_dir = Path(__file__).parent / "services" / "backend" / "src"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "backend"))

from uagents import Agent, Bureau, Context, Model
from uagents.setup import fund_agent_if_low

# Import AURA components
from threat_assessment_agent import ThreatAssessmentAgent
from home_state_agent import HomeStateAgent
from agent_orchestrator import AgentOrchestrator


# ============================================================================
# MESSAGE MODELS
# ============================================================================

class ThreatAnalysisRequest(Model):
    """Request for threat analysis"""
    location: str
    include_weather: bool = True
    include_grid: bool = True
    include_research: bool = False


class ThreatAnalysisResponse(Model):
    """Response from threat analysis"""
    success: bool
    threat_level: str
    threat_types: list
    message: str


class HomeStateRequest(Model):
    """Request for home state changes"""
    actions: list
    request_id: Optional[str] = None


class HomeStateResponse(Model):
    """Response from home state changes"""
    success: bool
    actions_executed: int
    message: str


class OrchestrationRequest(Model):
    """Request for complete threat-to-action pipeline"""
    location: str
    scenario: Optional[str] = None


class OrchestrationResponse(Model):
    """Response from orchestration"""
    success: bool
    threat_analysis: bool
    home_actions: int
    message: str


# ============================================================================
# AURA uAGENTS USING BUREAU PATTERN
# ============================================================================

class AURAUAgentsSystem:
    """AURA system using uAgents Bureau pattern"""
    
    def __init__(self, openai_api_key: Optional[str] = None, agentverse_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.agentverse_api_key = agentverse_api_key or os.getenv("AGENTVERSE_API_KEY")
        
        # Initialize AURA components
        self.threat_agent = ThreatAssessmentAgent(openai_api_key=self.openai_api_key)
        self.home_agent = HomeStateAgent(openai_api_key=self.openai_api_key)
        self.orchestrator = AgentOrchestrator(openai_api_key=self.openai_api_key)
        
        # Create uAgents
        self.create_uagents()
        
        # Create Bureau
        self.bureau = Bureau()
        self.bureau.add(self.threat_uagent)
        self.bureau.add(self.home_uagent)
        self.bureau.add(self.orchestrator_uagent)
    
    def create_uagents(self):
        """Create the uAgents"""
        
        # Threat Assessment uAgent
        self.threat_uagent = Agent(
            name="threat_assessment_oracle",
            seed="threat_oracle_seed_aura_2025",
            port=8001,
            endpoint="http://localhost:8001/submit"
        )
        
        # Home State uAgent
        self.home_uagent = Agent(
            name="home_state_digital_twin",
            seed="home_state_seed_aura_2025",
            port=8002,
            endpoint="http://localhost:8002/submit"
        )
        
        # Orchestrator uAgent
        self.orchestrator_uagent = Agent(
            name="aura_orchestrator",
            seed="orchestrator_seed_aura_2025",
            port=8000,
            endpoint="http://localhost:8000/submit"
        )
        
        # Fund agents
        fund_agent_if_low(self.threat_uagent.wallet.address())
        fund_agent_if_low(self.home_uagent.wallet.address())
        fund_agent_if_low(self.orchestrator_uagent.wallet.address())
        
        # Register message handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register message handlers for all agents"""
        
        # Threat Assessment Agent handlers
        @self.threat_uagent.on_message(model=ThreatAnalysisRequest, replies=ThreatAnalysisResponse)
        async def handle_threat_analysis(ctx: Context, sender: str, msg: ThreatAnalysisRequest):
            """Handle threat analysis requests"""
            try:
                ctx.logger.info(f"🔍 Analyzing threats for {msg.location}")
                
                # Convert to internal format
                from threat_models import ThreatAnalysisRequest as InternalRequest
                internal_request = InternalRequest(
                    location=msg.location,
                    include_weather=msg.include_weather,
                    include_grid=msg.include_grid,
                    include_research=msg.include_research
                )
                
                # Process the request
                result = await self.threat_agent.analyze_threats(internal_request)
                
                # Convert response
                response = ThreatAnalysisResponse(
                    success=result.success,
                    threat_level=result.analysis.overall_threat_level.value if result.analysis else "UNKNOWN",
                    threat_types=[t.value for t in result.analysis.threat_types] if result.analysis else [],
                    message=result.message
                )
                
                await ctx.send(sender, response)
                ctx.logger.info(f"✅ Threat analysis complete: {result.success}")
                
            except Exception as e:
                ctx.logger.error(f"❌ Threat analysis failed: {e}")
                error_response = ThreatAnalysisResponse(
                    success=False,
                    threat_level="ERROR",
                    threat_types=[],
                    message=f"Error: {str(e)}"
                )
                await ctx.send(sender, error_response)
        
        # Home State Agent handlers
        @self.home_uagent.on_message(model=HomeStateRequest, replies=HomeStateResponse)
        async def handle_home_state(ctx: Context, sender: str, msg: HomeStateRequest):
            """Handle home state requests"""
            try:
                ctx.logger.info(f"🏠 Processing {len(msg.actions)} home actions")
                
                # Convert to internal format
                from home_state_models import Action, DeviceType, ActionType, HomeStateRequest as InternalRequest
                
                actions = []
                for action_data in msg.actions:
                    action = Action(
                        device_type=DeviceType(action_data["device_type"]),
                        action_type=ActionType(action_data["action_type"]),
                        parameters=action_data.get("parameters", {}),
                        target_value=action_data.get("target_value")
                    )
                    actions.append(action)
                
                internal_request = InternalRequest(
                    actions=actions,
                    request_id=msg.request_id or "uagent_request"
                )
                
                # Process the request
                result = await self.home_agent.process_request(internal_request)
                
                # Convert response
                response = HomeStateResponse(
                    success=result.success,
                    actions_executed=len(result.action_results) if result.action_results else 0,
                    message=result.message
                )
                
                await ctx.send(sender, response)
                ctx.logger.info(f"✅ Home state update complete: {result.success}")
                
            except Exception as e:
                ctx.logger.error(f"❌ Home state update failed: {e}")
                error_response = HomeStateResponse(
                    success=False,
                    actions_executed=0,
                    message=f"Error: {str(e)}"
                )
                await ctx.send(sender, error_response)
        
        # Orchestrator Agent handlers
        @self.orchestrator_uagent.on_message(model=OrchestrationRequest, replies=OrchestrationResponse)
        async def handle_orchestration(ctx: Context, sender: str, msg: OrchestrationRequest):
            """Handle orchestration requests"""
            try:
                ctx.logger.info(f"🎯 Orchestrating threat-to-action for {msg.location}")
                
                # Process the complete pipeline
                result = await self.orchestrator.process_threat_to_action(
                    location=msg.location,
                    include_research=False
                )
                
                # Convert response
                response = OrchestrationResponse(
                    success=result["success"],
                    threat_analysis=result.get("threat_analysis") is not None,
                    home_actions=len(result.get("home_actions", [])),
                    message=result["message"]
                )
                
                await ctx.send(sender, response)
                ctx.logger.info(f"✅ Orchestration complete: {result['success']}")
                
            except Exception as e:
                ctx.logger.error(f"❌ Orchestration failed: {e}")
                error_response = OrchestrationResponse(
                    success=False,
                    threat_analysis=False,
                    home_actions=0,
                    message=f"Error: {str(e)}"
                )
                await ctx.send(sender, error_response)
    
    def get_agent_addresses(self):
        """Get all agent addresses"""
        return {
            "threat_assessment": self.threat_uagent.address,
            "home_state": self.home_uagent.address,
            "orchestrator": self.orchestrator_uagent.address
        }
    
    def print_agent_info(self):
        """Print agent information"""
        print("🤖 AURA uAgents Information:")
        print("=" * 50)
        print(f"🔍 Threat Assessment Agent:")
        print(f"   Address: {self.threat_uagent.address}")
        print(f"   Port: 8001")
        print(f"🏠 Home State Agent:")
        print(f"   Address: {self.home_uagent.address}")
        print(f"   Port: 8002")
        print(f"🎯 Orchestrator Agent:")
        print(f"   Address: {self.orchestrator_uagent.address}")
        print(f"   Port: 8000")
    
    async def run(self):
        """Run the AURA uAgents system"""
        self.print_agent_info()
        print(f"\n🚀 Starting AURA uAgents System...")
        await self.bureau.run()


# ============================================================================
# TEST CLIENT
# ============================================================================

async def create_test_client(aura_system: AURAUAgentsSystem):
    """Create a test client to interact with AURA agents"""
    
    # Create test client agent
    test_client = Agent(
        name="aura_test_client",
        seed="test_client_seed_aura_2025",
        port=8003
    )
    
    fund_agent_if_low(test_client.wallet.address())
    
    # Get agent addresses
    addresses = aura_system.get_agent_addresses()
    
    @test_client.on_interval(5.0)
    async def test_agents(ctx: Context):
        """Periodically test the agents"""
        
        # Test 1: Threat Analysis
        ctx.logger.info("🧪 Testing Threat Assessment Agent...")
        threat_request = ThreatAnalysisRequest(
            location="Austin, TX",
            include_weather=True,
            include_grid=True
        )
        
        threat_response = await ctx.send_and_wait(
            addresses["threat_assessment"],
            threat_request,
            response_type=ThreatAnalysisResponse,
            timeout=30.0
        )
        
        ctx.logger.info(f"Threat Analysis Result: {threat_response.success} - {threat_response.threat_level}")
        
        # Test 2: Home State Control
        ctx.logger.info("🧪 Testing Home State Agent...")
        home_request = HomeStateRequest(
            actions=[
                {
                    "device_type": "thermostat",
                    "action_type": "set",
                    "parameters": {"temperature": 68.0, "mode": "cool"}
                }
            ]
        )
        
        home_response = await ctx.send_and_wait(
            addresses["home_state"],
            home_request,
            response_type=HomeStateResponse,
            timeout=30.0
        )
        
        ctx.logger.info(f"Home State Result: {home_response.success} - {home_response.actions_executed} actions")
        
        # Test 3: Orchestration
        ctx.logger.info("🧪 Testing Orchestrator Agent...")
        orchestration_request = OrchestrationRequest(
            location="Austin, TX",
            scenario="heatwave"
        )
        
        orchestration_response = await ctx.send_and_wait(
            addresses["orchestrator"],
            orchestration_request,
            response_type=OrchestrationResponse,
            timeout=60.0
        )
        
        ctx.logger.info(f"Orchestration Result: {orchestration_response.success} - {orchestration_response.home_actions} actions")
    
    return test_client


# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def main():
    """Main function"""
    print("🚀 AURA uAgents Simple Integration")
    print("=" * 60)
    
    # Set API key
    agentverse_api_key = "sk_0325c4f7581c495196236a19cc2394da451bcb69caf74c35ab9c3d03540a7231"
    os.environ["AGENTVERSE_API_KEY"] = agentverse_api_key
    
    try:
        # Create AURA system
        aura_system = AURAUAgentsSystem(agentverse_api_key=agentverse_api_key)
        
        # Create test client
        test_client = await create_test_client(aura_system)
        
        # Add test client to bureau
        aura_system.bureau.add(test_client)
        
        # Run the system
        await aura_system.run()
        
    except Exception as e:
        print(f"❌ System failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
