#!/usr/bin/env python3
"""
AURA uAgents Integration using Bureau for running multiple agents.
This creates a working system where agents can communicate and handle messages.
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

# Set your API key
AGENTVERSE_API_KEY = "sk_0325c4f7581c495196236a19cc2394da451bcb69caf74c35ab9c3d03540a7231"
os.environ["AGENTVERSE_API_KEY"] = AGENTVERSE_API_KEY

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
    processing_time: float


class HomeStateRequest(Model):
    """Request for home state changes"""
    actions: list
    request_id: Optional[str] = None


class HomeStateResponse(Model):
    """Response from home state changes"""
    success: bool
    actions_executed: int
    message: str
    processing_time: float


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
    processing_time: float


class TestMessage(Model):
    """Simple test message"""
    content: str
    test_id: str


class TestResponse(Model):
    """Simple test response"""
    success: bool
    echo: str
    agent_name: str


# ============================================================================
# AURA UAGENTS BUREAU SYSTEM
# ============================================================================

class AURAUAgentsBureau:
    """AURA system using uAgents Bureau for coordinated execution"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize AURA backend components
        print("🔧 Initializing AURA Components...")
        self.threat_agent_backend = ThreatAssessmentAgent(openai_api_key=self.openai_api_key)
        self.home_agent_backend = HomeStateAgent(openai_api_key=self.openai_api_key)
        self.orchestrator_backend = AgentOrchestrator(openai_api_key=self.openai_api_key)
        print("✅ AURA backend components initialized")
        
        # Create uAgents
        self.create_uagents()
        
        # Create Bureau and add agents
        self.bureau = Bureau()
        self.bureau.add(self.threat_uagent)
        self.bureau.add(self.home_uagent)
        self.bureau.add(self.orchestrator_uagent)
        self.bureau.add(self.test_client)
        
        print("✅ Bureau created with all agents")
    
    def create_uagents(self):
        """Create all uAgents"""
        
        # Threat Assessment uAgent
        self.threat_uagent = Agent(
            name="threat_oracle",
            seed="threat_seed_aura_2025",
            port=8001
        )
        fund_agent_if_low(self.threat_uagent.wallet.address())
        
        # Home State uAgent
        self.home_uagent = Agent(
            name="home_twin",
            seed="home_seed_aura_2025",
            port=8002
        )
        fund_agent_if_low(self.home_uagent.wallet.address())
        
        # Orchestrator uAgent
        self.orchestrator_uagent = Agent(
            name="aura_coordinator",
            seed="coordinator_seed_aura_2025",
            port=8000
        )
        fund_agent_if_low(self.orchestrator_uagent.wallet.address())
        
        # Test Client uAgent
        self.test_client = Agent(
            name="test_client",
            seed="client_seed_aura_2025",
            port=8003
        )
        fund_agent_if_low(self.test_client.wallet.address())
        
        print("✅ All uAgents created and funded")
        
        # Register message handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register message handlers for all agents"""
        
        # ========================================================================
        # THREAT ASSESSMENT AGENT HANDLERS
        # ========================================================================
        
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
                result = await self.threat_agent_backend.analyze_threats(internal_request)
                
                # Convert response
                response = ThreatAnalysisResponse(
                    success=result.success,
                    threat_level=result.analysis.overall_threat_level.value if result.analysis else "UNKNOWN",
                    threat_types=[t.value for t in result.analysis.threat_types] if result.analysis else [],
                    message=result.message,
                    processing_time=result.processing_time_ms or 0.0
                )
                
                await ctx.send(sender, response)
                ctx.logger.info(f"✅ Threat analysis complete: {result.success}")
                
            except Exception as e:
                ctx.logger.error(f"❌ Threat analysis failed: {e}")
                error_response = ThreatAnalysisResponse(
                    success=False,
                    threat_level="ERROR",
                    threat_types=[],
                    message=f"Error: {str(e)}",
                    processing_time=0.0
                )
                await ctx.send(sender, error_response)
        
        @self.threat_uagent.on_message(model=TestMessage, replies=TestResponse)
        async def handle_threat_test(ctx: Context, sender: str, msg: TestMessage):
            """Handle test messages for threat agent"""
            response = TestResponse(
                success=True,
                echo=f"Threat Agent received: {msg.content}",
                agent_name="threat_oracle"
            )
            await ctx.send(sender, response)
        
        # ========================================================================
        # HOME STATE AGENT HANDLERS
        # ========================================================================
        
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
                result = await self.home_agent_backend.process_request(internal_request)
                
                # Convert response
                response = HomeStateResponse(
                    success=result.success,
                    actions_executed=len(result.action_results) if result.action_results else 0,
                    message=result.message,
                    processing_time=result.processing_time_ms or 0.0
                )
                
                await ctx.send(sender, response)
                ctx.logger.info(f"✅ Home state update complete: {result.success}")
                
            except Exception as e:
                ctx.logger.error(f"❌ Home state update failed: {e}")
                error_response = HomeStateResponse(
                    success=False,
                    actions_executed=0,
                    message=f"Error: {str(e)}",
                    processing_time=0.0
                )
                await ctx.send(sender, error_response)
        
        @self.home_uagent.on_message(model=TestMessage, replies=TestResponse)
        async def handle_home_test(ctx: Context, sender: str, msg: TestMessage):
            """Handle test messages for home agent"""
            response = TestResponse(
                success=True,
                echo=f"Home Agent received: {msg.content}",
                agent_name="home_twin"
            )
            await ctx.send(sender, response)
        
        # ========================================================================
        # ORCHESTRATOR AGENT HANDLERS
        # ========================================================================
        
        @self.orchestrator_uagent.on_message(model=OrchestrationRequest, replies=OrchestrationResponse)
        async def handle_orchestration(ctx: Context, sender: str, msg: OrchestrationRequest):
            """Handle orchestration requests"""
            try:
                ctx.logger.info(f"🎯 Orchestrating threat-to-action for {msg.location}")
                
                # Process the complete pipeline
                result = await self.orchestrator_backend.process_threat_to_action(
                    location=msg.location,
                    include_research=False
                )
                
                # Convert response
                response = OrchestrationResponse(
                    success=result["success"],
                    threat_analysis=result.get("threat_analysis") is not None,
                    home_actions=len(result.get("home_actions", [])),
                    message=result["message"],
                    processing_time=result.get("processing_time_ms", 0.0)
                )
                
                await ctx.send(sender, response)
                ctx.logger.info(f"✅ Orchestration complete: {result['success']}")
                
            except Exception as e:
                ctx.logger.error(f"❌ Orchestration failed: {e}")
                error_response = OrchestrationResponse(
                    success=False,
                    threat_analysis=False,
                    home_actions=0,
                    message=f"Error: {str(e)}",
                    processing_time=0.0
                )
                await ctx.send(sender, error_response)
        
        @self.orchestrator_uagent.on_message(model=TestMessage, replies=TestResponse)
        async def handle_orchestrator_test(ctx: Context, sender: str, msg: TestMessage):
            """Handle test messages for orchestrator agent"""
            response = TestResponse(
                success=True,
                echo=f"Orchestrator received: {msg.content}",
                agent_name="aura_coordinator"
            )
            await ctx.send(sender, response)
        
        # ========================================================================
        # TEST CLIENT HANDLERS AND INTERVALS
        # ========================================================================
        
        @self.test_client.on_interval(10.0)
        async def test_agents_periodically(ctx: Context):
            """Periodically test all agents"""
            ctx.logger.info("🧪 Running periodic agent tests...")
            
            # Test 1: Simple ping test to all agents
            test_msg = TestMessage(content="Ping test", test_id="ping_001")
            
            # Test Threat Agent
            try:
                threat_response = await ctx.send_and_wait(
                    self.threat_uagent.address,
                    test_msg,
                    response_type=TestResponse,
                    timeout=5.0
                )
                ctx.logger.info(f"✅ Threat Agent: {threat_response.echo}")
            except Exception as e:
                ctx.logger.error(f"❌ Threat Agent test failed: {e}")
            
            # Test Home Agent
            try:
                home_response = await ctx.send_and_wait(
                    self.home_uagent.address,
                    test_msg,
                    response_type=TestResponse,
                    timeout=5.0
                )
                ctx.logger.info(f"✅ Home Agent: {home_response.echo}")
            except Exception as e:
                ctx.logger.error(f"❌ Home Agent test failed: {e}")
            
            # Test Orchestrator
            try:
                orch_response = await ctx.send_and_wait(
                    self.orchestrator_uagent.address,
                    test_msg,
                    response_type=TestResponse,
                    timeout=5.0
                )
                ctx.logger.info(f"✅ Orchestrator: {orch_response.echo}")
            except Exception as e:
                ctx.logger.error(f"❌ Orchestrator test failed: {e}")
        
        @self.test_client.on_interval(30.0)
        async def test_threat_analysis(ctx: Context):
            """Test threat analysis functionality"""
            ctx.logger.info("🔬 Testing threat analysis...")
            
            try:
                request = ThreatAnalysisRequest(
                    location="Austin, TX",
                    include_weather=True,
                    include_grid=True
                )
                
                response = await ctx.send_and_wait(
                    self.threat_uagent.address,
                    request,
                    response_type=ThreatAnalysisResponse,
                    timeout=30.0
                )
                
                ctx.logger.info(f"🔍 Threat Analysis: {response.success} - Level: {response.threat_level}")
                ctx.logger.info(f"   Types: {response.threat_types}")
                ctx.logger.info(f"   Time: {response.processing_time:.2f}ms")
                
            except Exception as e:
                ctx.logger.error(f"❌ Threat analysis test failed: {e}")
        
        @self.test_client.on_interval(45.0)
        async def test_home_control(ctx: Context):
            """Test home control functionality"""
            ctx.logger.info("🏠 Testing home control...")
            
            try:
                request = HomeStateRequest(
                    actions=[
                        {
                            "device_type": "thermostat",
                            "action_type": "set",
                            "parameters": {"temperature": 72.0, "mode": "cool"}
                        }
                    ]
                )
                
                response = await ctx.send_and_wait(
                    self.home_uagent.address,
                    request,
                    response_type=HomeStateResponse,
                    timeout=30.0
                )
                
                ctx.logger.info(f"🏠 Home Control: {response.success} - Actions: {response.actions_executed}")
                ctx.logger.info(f"   Time: {response.processing_time:.2f}ms")
                
            except Exception as e:
                ctx.logger.error(f"❌ Home control test failed: {e}")
        
        @self.test_client.on_interval(60.0)
        async def test_full_orchestration(ctx: Context):
            """Test full orchestration functionality"""
            ctx.logger.info("🎯 Testing full orchestration...")
            
            try:
                request = OrchestrationRequest(
                    location="Austin, TX",
                    scenario="heatwave"
                )
                
                response = await ctx.send_and_wait(
                    self.orchestrator_uagent.address,
                    request,
                    response_type=OrchestrationResponse,
                    timeout=60.0
                )
                
                ctx.logger.info(f"🎯 Orchestration: {response.success}")
                ctx.logger.info(f"   Threat Analysis: {response.threat_analysis}")
                ctx.logger.info(f"   Home Actions: {response.home_actions}")
                ctx.logger.info(f"   Time: {response.processing_time:.2f}ms")
                
            except Exception as e:
                ctx.logger.error(f"❌ Orchestration test failed: {e}")
        
        print("✅ All message handlers registered")
    
    def get_agent_addresses(self):
        """Get all agent addresses"""
        return {
            "threat_assessment": self.threat_uagent.address,
            "home_state": self.home_uagent.address,
            "orchestrator": self.orchestrator_uagent.address,
            "test_client": self.test_client.address
        }
    
    def print_system_info(self):
        """Print system information"""
        print("\n🌟 AURA uAgents Bureau System")
        print("=" * 60)
        addresses = self.get_agent_addresses()
        
        print(f"🔍 Threat Assessment Agent:")
        print(f"   Address: {addresses['threat_assessment']}")
        print(f"   Port: 8001")
        
        print(f"🏠 Home State Agent:")
        print(f"   Address: {addresses['home_state']}")
        print(f"   Port: 8002")
        
        print(f"🎯 Orchestrator Agent:")
        print(f"   Address: {addresses['orchestrator']}")
        print(f"   Port: 8000")
        
        print(f"🧪 Test Client:")
        print(f"   Address: {addresses['test_client']}")
        print(f"   Port: 8003")
        
        print("\n🔄 Features:")
        print("   ✅ Bureau-based coordination")
        print("   ✅ Message-based communication")
        print("   ✅ Periodic testing intervals")
        print("   ✅ Full AURA pipeline integration")
        print("   ✅ Error handling and logging")
    
    async def run(self):
        """Run the AURA Bureau system"""
        self.print_system_info()
        print(f"\n🚀 Starting AURA uAgents Bureau...")
        print(f"💡 The system will run periodic tests every 10-60 seconds")
        print(f"⏹️  Press Ctrl+C to stop\n")
        
        await self.bureau.run()


# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def main():
    """Main function"""
    print("🚀 AURA uAgents Bureau System")
    print("=" * 60)
    print("Running AURA agents in a coordinated Bureau with periodic testing")
    print("=" * 60)
    
    try:
        # Create and run the system
        aura_bureau = AURAUAgentsBureau()
        await aura_bureau.run()
        
    except KeyboardInterrupt:
        print("\n⏹️  System stopped by user")
    except Exception as e:
        print(f"❌ System failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
