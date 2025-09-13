#!/usr/bin/env python3
"""
Simple script to run the AURA Agent for testing
"""

import asyncio
import os
from dotenv import load_dotenv
from src.aura_agent import AURAAgent

# Load environment variables
load_dotenv()


async def main():
    """Main function to run the agent"""
    print("🚀 Starting AURA Smart Home Management Agent...")
    
    # Create agent
    agent = AURAAgent(name="AURA")
    
    print("✅ Agent initialized successfully!")
    print(f"📊 Home Status: {agent.home_status.dict()}")
    print(f"👥 Registered Homeowners: {len(agent.registered_homeowners)}")
    
    # Interactive mode
    print("\n🎯 Interactive Mode - Available Commands:")
    print("- register <name> <phone> - Register homeowner")
    print("- status - Get home status")
    print("- homeowners - List homeowners")
    print("- simulate - Simulate heatwave")
    print("- reset - Reset simulation")
    print("- quit - Exit")
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command == "quit":
                break
            elif command.startswith("register"):
                parts = command.split()
                if len(parts) >= 3:
                    name = parts[1]
                    phone = parts[2]
                    result = await agent.register_homeowner(name, phone)
                    print(f"📝 {result.message}")
                else:
                    print("❌ Usage: register <name> <phone>")
            
            elif command == "status":
                result = await agent.get_home_status()
                print(f"🏠 Home Status: {result.data['status']}")
            
            elif command == "homeowners":
                result = await agent.get_registered_homeowners()
                if result.data['homeowners']:
                    for homeowner in result.data['homeowners']:
                        print(f"👤 {homeowner['name']} - {homeowner['phone_number']}")
                else:
                    print("👥 No homeowners registered")
            
            elif command == "simulate":
                result = await agent.simulate_heatwave()
                print(f"🌡️ {result.message}")
                if result.success:
                    print(f"📊 Final Status: {result.data['final_status']}")
            
            elif command == "reset":
                result = await agent.reset_simulation()
                print(f"🔄 {result.message}")
            
            else:
                print("❌ Unknown command. Type 'quit' to exit.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
