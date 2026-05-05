import re
from typing import Dict, Any, Optional, List

# ==========================================
# MOCKS & STUBS (For demonstration purposes)
# ==========================================
def mock_llm_call(prompt: str) -> str:
    """Stub for the actual LLM API call."""
    if "[TOOL_RESULT]" in prompt:
        return f"Based on the data provided: {prompt.split('[TOOL_RESULT]')[-1].strip()}"
    return f"LLM processed context: '{prompt[:50]}...'"

def mock_tool_execution(tool_name: str, query: str) -> str:
    """Stub for actual tool APIs (Web, Calculator, Python, Memory)."""
    if tool_name == "Calculator":
        return "42"
    elif tool_name == "Web_Search":
        return f"Search results for '{query}': The sky is blue due to Rayleigh scattering."
    elif tool_name == "Python_Exec":
        return "Execution successful. Output: [1, 4, 9, 16]"
    elif tool_name == "Memory_Search":
        return "No previous data found in session."
    return "Tool error."

# ==========================================
# SYSTEM COMPONENTS (Steps 1 through 8)
# ==========================================

class SessionMemory:
    """8️⃣ SESSION MEMORY (TEMPORARY)"""
    def __init__(self):
        self._buffer: List[Dict[str, str]] = []  # Stored in RAM only

    def add(self, role: str, content: str):
        self._buffer.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self._buffer.copy()

    def clear(self):
        """Cleared after session ends."""
        self._buffer.clear()


class InputProcessor:
    """1️⃣ INPUT PROCESSOR"""
    @staticmethod
    def process(user_input: str) -> str:
        # Remove noise, unnecessary formatting, and standardize structure
        cleaned = user_input.strip()
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned) # Collapse multiple newlines
        return cleaned


class IntentDetector:
    """2️⃣ INTENT DETECTOR (MODE FILTER)"""
    BRAINSTORM_KEYWORDS = ["brainstorm", "idea mode", "generate ideas", "brainstorming"]

    @classmethod
    def detect(cls, processed_input: str) -> Dict[str, Any]:
        input_lower = processed_input.lower()
        for kw in cls.BRAINSTORM_KEYWORDS:
            if kw in input_lower:
                return {"mode": "IDEA_MODE", "redirect": True}
        
        return {"mode": "NORMAL_CHAT", "redirect": False}


class ContextBuilder:
    """3️⃣ CONTEXT BUILDER"""
    SYSTEM_PROMPT = "You are NOTEGPT, an intelligent assistant in Normal Chat Mode. Be clear, logical, and concise."

    @classmethod
    def build(cls, history: List[Dict[str, str]], current_input: str, tool_result: Optional[str] = None) -> str:
        context = f"SYSTEM: {cls.SYSTEM_PROMPT}\n\n"
        
        # Add compressed history (simplified for mock)
        for turn in history[-5:]: # Keep last 5 turns for context window management
            context += f"{turn['role'].upper()}: {turn['content']}\n"
            
        context += f"USER: {current_input}\n"
        
        # Prioritize tool outputs if available
        if tool_result:
            context += f"[TOOL_RESULT]: {tool_result}\n"
            
        context += "ASSISTANT:"
        return context


class ToolDecisionEngine:
    """4️⃣ TOOL DECISION ENGINE"""
    @staticmethod
    def decide(processed_input: str) -> Optional[str]:
        input_lower = processed_input.lower()
        
        if any(kw in input_lower for kw in ["calculate", "math", "what is 2+", "sum of"]):
            return "Calculator"
        elif any(kw in input_lower for kw in ["latest", "current events", "who is", "search for", "fact check"]):
            return "Web_Search"
        elif any(kw in input_lower for kw in ["write a script", "code this", "python function", "parse this data"]):
            return "Python_Exec"
        elif any(kw in input_lower for kw in ["remember when i", "earlier you said", "my previous data"]):
            return "Memory_Search"
            
        return None # Bypass tools, go direct to response generation


class KnowledgeToolLayer:
    """5️⃣ KNOWLEDGE / TOOL LAYER"""
    @staticmethod
    def execute(tool_name: str, query: str) -> str:
        # In production, this would route to actual API wrappers
        return mock_tool_execution(tool_name, query)


class LLMReasoningEngine:
    """6️⃣ LLM REASONING ENGINE"""
    @staticmethod
    def generate(context: str) -> str:
        # In production, this calls OpenAI/Anthropic/Claude API
        return mock_llm_call(context)


class ResponseFormatter:
    """7️⃣ RESPONSE FORMATTER"""
    @staticmethod
    def format(raw_output: str) -> str:
        # Improve clarity, readability, and logical structure
        # (Mocking structural improvements like adding bullet points if list-like)
        if "1." in raw_output or "2." in raw_output:
            return "\n💡 **NOTEGPT Response:**\n" + raw_output.replace(". ", ".\n- ")
        return "\n💡 **NOTEGPT Response:**\n" + raw_output.strip()


# ==========================================
# MAIN ORCHESTRATOR (The Full System Flow)
# ==========================================

class NormalChatModeOrchestrator:
    def __init__(self):
        self.memory = SessionMemory()
        
    def process_request(self, user_input: str) -> str:
        """🔁 FULL SYSTEM FLOW"""
        
        # USER INPUT -> 1️⃣ INPUT PROCESSOR
        processed_input = InputProcessor.process(user_input)
        
        # -> 2️⃣ INTENT DETECTOR
        intent = IntentDetector.detect(processed_input)
        if intent["redirect"]:
            return "⚠️ REDIRECT: This request requires Idea Mode. Switching systems..."
            
        # -> 4️⃣ TOOL DECISION ENGINE
        required_tool = ToolDecisionEngine.decide(processed_input)
        
        tool_result = None
        # -> 5️⃣ KNOWLEDGE / TOOL LAYER (if required)
        if required_tool:
            tool_result = KnowledgeToolLayer.execute(required_tool, processed_input)
            
        # -> 3️⃣ CONTEXT BUILDER
        history = self.memory.get_history()
        context = ContextBuilder.build(history, processed_input, tool_result)
        
        # -> 6️⃣ LLM REASONING ENGINE
        raw_response = LLMReasoningEngine.generate(context)
        
        # -> 7️⃣ RESPONSE FORMATTER
        final_response = ResponseFormatter.format(raw_response)
        
        # -> 8️⃣ SESSION MEMORY UPDATE
        self.memory.add("user", processed_input)
        self.memory.add("assistant", final_response)
        
        # OUTPUT RESPONSE
        return final_response
        
    def end_session(self):
        """Simulates session end, clearing temporary memory"""
        self.memory.clear()
        print("🗑️ Session memory cleared.")

# ==========================================
# TESTING THE SYSTEM LOGIC
# ==========================================
if __name__ == "__main__":
    notegpt = NormalChatModeOrchestrator()
    
    # Test 1: Normal Chat (No tools)
    print("--- TEST 1: Normal Chat ---")
    print(notegpt.process_request("Explain the concept of recursion in simple terms."))
    
    # Test 2: Tool Trigger (Math)
    print("\n--- TEST 2: Math Tool Trigger ---")
    print(notegpt.process_request("Calculate what is 6 multiplied by 7"))
    
    # Test 3: Tool Trigger (Web Search)
    print("\n--- TEST 3: Web Search Trigger ---")
    print(notegpt.process_request("Search for the latest news about Mars rovers"))
    
    # Test 4: Intent Filter (Brainstorm Redirection)
    print("\n--- TEST 4: Brainstorm Redirect ---")
    print(notegpt.process_request("I want to brainstorm some ideas for a new app!"))
    
    # Test 5: Memory Integration
    print("\n--- TEST 5: Memory Tool Trigger ---")
    print(notegpt.process_request("Remember when I asked about recursion earlier?"))
    
    # End session
    notegpt.end_session()
