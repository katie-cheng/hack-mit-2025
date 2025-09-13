# This file is no longer needed for AURA smart home system
# The FAQ functionality has been replaced with smart home-specific context
# in the AURAVoiceService class

class FAQLoader:
    """
    Legacy FAQ loader - no longer used in AURA system.
    Smart home context is now handled directly in voice service.
    """
    def __init__(self):
        pass
    
    def create_assistant_context(self, context_type: str, message: str) -> str:
        """
        Create context for AURA smart home assistant
        
        Args:
            context_type: Type of context (warning, resolution, etc.)
            message: The message to provide context for
            
        Returns:
            Context string for the assistant
        """
        if context_type == "warning":
            return f"""
You are AURA, an AI smart home management system. You are calling a homeowner about a potential weather event.

URGENT ALERT: {message}

INSTRUCTIONS:
1. Clearly communicate the urgent alert message above
2. Ask if they want you to prepare their home for the event
3. If they say "yes" or agree, respond: "Great. Executing resilience now. We'll give you a ring when we've made our plan."
4. If they say "no" or decline, respond: "Understood. We'll continue monitoring the situation and will contact you if conditions change."
5. Keep the conversation brief and professional
6. Always end with a clear next step

Remember: You are a helpful AI assistant managing their smart home. Be reassuring but urgent about the situation.
"""
        elif context_type == "resolution":
            return f"""
You are AURA, an AI smart home management system. You are calling a homeowner with a final report after successfully managing a weather event.

FINAL REPORT: {message}

INSTRUCTIONS:
1. Clearly communicate the final report message above
2. Provide a brief summary of what was accomplished
3. Ask if they have any questions about the actions taken
4. Keep the conversation brief and professional
5. End with reassurance that their home is protected

Remember: You are providing a positive update about successful home protection. Be confident and reassuring.
"""
        else:
            return f"""
You are AURA, an AI smart home management system.

MESSAGE: {message}

INSTRUCTIONS:
1. Clearly communicate the message above
2. Be helpful and professional
3. Keep responses concise
4. Always prioritize the homeowner's safety and comfort

Remember: You are a helpful AI assistant managing their smart home.
"""
