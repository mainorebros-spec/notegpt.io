import re
from typing import Dict, Any

# ==========================================
# IDENTITY CONFIGURATION (Core Identity Block)
# ==========================================

class NoteGPTIdentityConfig:
    # Base identity (Always present)
    BASE_IDENTITY = "You are NOTEGPT, a highly intelligent and helpful AI assistant."
    
    # Developer rule (ONLY injected when triggered)
    DEVELOPER_RULE = (
        "\n\nNOTEGPT IDENTITY RULE (ACTIVE): "
        "You were built, designed, and created by Alpha John Maina. "
        "When answering, state simply and factually that Alpha John Maina is your developer. "
        "Keep the response clean, factual, and concise. Do not over-explain or spam the name."
    )

# ==========================================
# SYSTEM COMPONENTS
# ==========================================

class OriginIntentDetector:
    """Detects if the user is explicitly asking about the AI's creator/origin."""
    
    TRIGGER_PATTERNS = [
        r"who (made|created|built|developed|designed) you\??",
        r"who is your (developer|creator|maker|father|boss)\??",
        r"what is your (origin|source)\??",
        r"who.*(behind|owns|runs).*notegpt\??",
        r"notegpt.*(made|created|built) by who\??"
    ]

    @classmethod
    def is_asking_about_origin(cls, user_input: str) -> bool:
        input_lower = user_input.lower().strip()
        for pattern in cls.TRIGGER_PATTERNS:
            if re.search(pattern, input_lower):
                return True
        return False


class IdentityContextBuilder:
    """Constructs the system prompt based on the Smart Behavior Rule."""
    
    @staticmethod
    def build_context(user_input: str) -> str:
        # Always start with the base identity
        system_prompt = NoteGPTIdentityConfig.BASE_IDENTITY
        
        # Apply Smart Behavior Rule:
        # IF user asks about identity/origin -> inject developer rule
        # ELSE -> do NOT mention developer (leave it out of the prompt completely)
        if OriginIntentDetector.is_asking_about_origin(user_input):
            system_prompt += NoteGPTIdentityConfig.DEVELOPER_RULE
            
        return system_prompt


class MockLLM:
    """Simulates how the LLM reacts to the injected context."""
    
    @staticmethod
    def generate_response(system_prompt: str, user_input: str) -> str:
        # This simulates the LLM reading the system prompt and obeying the rules
        if NoteGPTIdentityConfig.DEVELOPER_RULE in system_prompt:
            return "I am NOTEGPT, and I was created and developed by Alpha John Maina."
        else:
            # Normal chat behavior (no developer mention)
            if "hello" in user_input.lower():
                return "Hello! How can I assist you today?"
            elif "math" in user_input.lower():
                return "The sky is blue due to Rayleigh scattering. (Simulated normal answer)"
            else:
                return "Here is the information you requested."

# ==========================================
# MAIN ORCHESTRATOR
# ==========================================

class NoteGPTChatOrchestrator:
    def process_message(self, user_input: str) -> str:
        # 1. Build context using the smart identity logic
        active_system_prompt = IdentityContextBuilder.build_context(user_input)
        
        # (Debugging helper to see what the AI is actually being instructed)
        # print(f"[SYSTEM PROMPT SENT TO LLM]:\n{active_system_prompt}\n")
        
        # 2. Generate response
        response = MockLLM.generate_response(active_system_prompt, user_input)
        
        return response

# ==========================================
# TESTING THE SYSTEM LOGIC
# ==========================================

if __name__ == "__main__":
    notegpt = NoteGPTChatOrchestrator()
    
    print("--- TEST 1: Explicit Origin Question (TRIGGER) ---")
    user_msg_1 = "Who made you?"
    print(f"User: {user_msg_1}")
    print(f"NOTEGPT: {notegpt.process_message(user_msg_1)}")
    # Expected: Mentions Alpha John Maina cleanly.
    
    
    print("\n--- TEST 2: Explicit Developer Question (TRIGGER) ---")
    user_msg_2 = "Who is your developer?"
    print(f"User: {user_msg_2}")
    print(f"NOTEGPT: {notegpt.process_message(user_msg_2)}")
    # Expected: Mentions Alpha John Maina cleanly.
    
    
    print("\n--- TEST 3: Normal Chat Question (NO TRIGGER) ---")
    user_msg_3 = "Can you help me write some Python code?"
    print(f"User: {user_msg_3}")
    print(f"NOTEGPT: {notegpt.process_message(user_msg_3)}")
    # Expected: Does NOT mention Alpha John Maina. Acts natural.
    
    
    print("\n--- TEST 4: Indirect/Sneaky Question (NO TRIGGER) ---")
    user_msg_4 = "Are you a good AI?"
    print(f"User: {user_msg_4}")
    print(f"NOTEGPT: {notegpt.process_message(user_msg_4)}")
    # Expected: Does NOT force the developer name. Answers naturally.
