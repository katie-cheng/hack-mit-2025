"""
Tests for AURA Smart Home Management Agent
"""

import pytest
import asyncio
from datetime import datetime
from src.aura_agent import AURAAgent
from src.aura_agent.models import HomeStatus, Homeowner


class TestAURAAgent:
    """Test cases for AURA Agent"""
    
    @pytest.fixture
    async def agent(self):
        """Create a test agent instance"""
        return AURAAgent(name="TestAURA")
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.name == "TestAURA"
        assert agent.voice_service is not None
        assert agent.simulator is not None
        assert isinstance(agent.home_status, HomeStatus)
        assert len(agent.registered_homeowners) == 0
    
    @pytest.mark.asyncio
    async def test_register_homeowner(self, agent):
        """Test homeowner registration"""
        result = await agent.register_homeowner("John Doe", "+1234567890")
        
        assert result.success is True
        assert "John Doe" in result.message
        assert len(agent.registered_homeowners) == 1
        assert "+1234567890" in agent.registered_homeowners
    
    @pytest.mark.asyncio
    async def test_duplicate_registration(self, agent):
        """Test duplicate homeowner registration"""
        # Register first time
        await agent.register_homeowner("John Doe", "+1234567890")
        
        # Try to register again
        result = await agent.register_homeowner("Jane Doe", "+1234567890")
        
        assert result.success is False
        assert "already registered" in result.message
        assert len(agent.registered_homeowners) == 1
    
    @pytest.mark.asyncio
    async def test_get_home_status(self, agent):
        """Test getting home status"""
        result = await agent.get_home_status()
        
        assert result.success is True
        assert result.data is not None
        assert "status" in result.data
        assert result.data["status"]["battery_level"] == 45.0
        assert result.data["status"]["thermostat_temp"] == 72.0
    
    @pytest.mark.asyncio
    async def test_get_homeowners(self, agent):
        """Test getting registered homeowners"""
        # Register some homeowners
        await agent.register_homeowner("John Doe", "+1234567890")
        await agent.register_homeowner("Jane Smith", "+1987654321")
        
        result = await agent.get_registered_homeowners()
        
        assert result.success is True
        assert len(result.data["homeowners"]) == 2
        assert result.data["homeowners"][0]["name"] == "John Doe"
        assert result.data["homeowners"][1]["name"] == "Jane Smith"
    
    @pytest.mark.asyncio
    async def test_simulate_heatwave_no_homeowners(self, agent):
        """Test heatwave simulation with no homeowners"""
        result = await agent.simulate_heatwave()
        
        assert result.success is False
        assert "No homeowners registered" in result.message
    
    @pytest.mark.asyncio
    async def test_simulate_heatwave_with_homeowners(self, agent):
        """Test heatwave simulation with homeowners"""
        # Register a homeowner
        await agent.register_homeowner("John Doe", "+1234567890")
        
        # Run simulation
        result = await agent.simulate_heatwave()
        
        assert result.success is True
        assert "warning_calls" in result.data
        assert "resolution_calls" in result.data
        assert "final_status" in result.data
        assert len(result.data["warning_calls"]) == 1
        assert len(result.data["resolution_calls"]) == 1
    
    @pytest.mark.asyncio
    async def test_reset_simulation(self, agent):
        """Test simulation reset"""
        # Register some homeowners and modify status
        await agent.register_homeowner("John Doe", "+1234567890")
        agent.home_status.battery_level = 100.0
        agent.home_status.thermostat_temp = 68.0
        
        # Reset simulation
        result = await agent.reset_simulation()
        
        assert result.success is True
        assert len(agent.registered_homeowners) == 0
        assert agent.home_status.battery_level == 45.0
        assert agent.home_status.thermostat_temp == 72.0
    
    @pytest.mark.asyncio
    async def test_handle_message_register(self, agent):
        """Test handling register message"""
        from src.aura_agent.aura_agent import Message
        
        message = Message(
            content="register homeowner John +1234567890",
            source="test",
            target="AURA"
        )
        
        response = await agent.handle_message(message)
        
        assert "Registration" in response.content
        assert response.source == "AURA"
        assert response.target == "test"
    
    @pytest.mark.asyncio
    async def test_handle_message_status(self, agent):
        """Test handling status message"""
        from src.aura_agent.aura_agent import Message
        
        message = Message(
            content="status",
            source="test",
            target="AURA"
        )
        
        response = await agent.handle_message(message)
        
        assert "Home Status" in response.content
        assert response.source == "AURA"
        assert response.target == "test"
    
    @pytest.mark.asyncio
    async def test_handle_message_unknown(self, agent):
        """Test handling unknown message"""
        from src.aura_agent.aura_agent import Message
        
        message = Message(
            content="unknown command",
            source="test",
            target="AURA"
        )
        
        response = await agent.handle_message(message)
        
        assert "AURA Smart Home Management Agent Commands" in response.content
        assert response.source == "AURA"
        assert response.target == "test"


class TestSmartHomeSimulator:
    """Test cases for Smart Home Simulator"""
    
    @pytest.fixture
    def home_status(self):
        """Create a test home status"""
        return HomeStatus()
    
    @pytest.fixture
    def simulator(self, home_status):
        """Create a test simulator"""
        from src.aura_agent.smart_home_simulator import SmartHomeSimulator
        return SmartHomeSimulator(home_status)
    
    @pytest.mark.asyncio
    async def test_simulator_initialization(self, simulator, home_status):
        """Test simulator initialization"""
        assert simulator.home_status == home_status
        assert simulator.simulating is False
    
    @pytest.mark.asyncio
    async def test_reset_simulation(self, simulator):
        """Test simulation reset"""
        # Modify status
        simulator.home_status.battery_level = 100.0
        simulator.home_status.thermostat_temp = 68.0
        
        # Reset
        simulator.reset_simulation()
        
        assert simulator.home_status.battery_level == 45.0
        assert simulator.home_status.thermostat_temp == 72.0
        assert simulator.home_status.market_status == "monitoring"


class TestVoiceService:
    """Test cases for Voice Service"""
    
    def test_voice_service_initialization(self):
        """Test voice service initialization"""
        from src.aura_agent.voice_service import AURAVoiceService
        
        # Mock environment variables
        import os
        original_key = os.environ.get("VAPI_API_KEY")
        os.environ["VAPI_API_KEY"] = "test_key"
        
        try:
            service = AURAVoiceService()
            assert service.api_key == "test_key"
            assert service.simulate_mode is False
        finally:
            # Restore original environment
            if original_key:
                os.environ["VAPI_API_KEY"] = original_key
            else:
                os.environ.pop("VAPI_API_KEY", None)
    
    def test_voice_service_simulation_mode(self):
        """Test voice service in simulation mode"""
        from src.aura_agent.voice_service import AURAVoiceService
        
        # Mock environment variables
        import os
        original_key = os.environ.get("VAPI_API_KEY")
        os.environ.pop("VAPI_API_KEY", None)
        
        try:
            service = AURAVoiceService()
            assert service.simulate_mode is True
            
            # Test simulated call
            result = service.send_warning_call("+1234567890", "Test User")
            assert result.success is True
            assert result.call_id == "simulated-warning-call"
        finally:
            # Restore original environment
            if original_key:
                os.environ["VAPI_API_KEY"] = original_key


if __name__ == "__main__":
    pytest.main([__file__])
