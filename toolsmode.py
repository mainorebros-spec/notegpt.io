import re
import json
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple

# ==========================================
# TOOL INTEGRATION STUBS (Stateless)
# ==========================================

class ToolType(Enum):
    WEB = "Web_Tool"
    READER = "Reader_Tool"
    CALCULATOR = "Calculator_Tool"
    PYTHON = "Python_Tool"
    MEMORY = "Memory_Tool"

class StatelessToolExecutor:
    """Mock stateless tools. No data is saved between executions."""
    
    @staticmethod
    def execute_web(query: str) -> str:
        # Simulates returning raw, slightly noisy web data
        return json.dumps({
            "status": "success",
            "results": [
                {"title": "Weather Today", "snippet": f"The weather for '{query}' is 72°F and sunny.", "noise": "<img src='ad.jpg'>"},
                {"title": "Old Forecast", "snippet": "Yesterday it rained.", "noise": "<script>alert('hi')</script>"}
            ]
        })

    @staticmethod
    def execute_calculator(expression: str) -> str:
        # Simulates raw math output
        try:
            # Safe eval for mock purposes only
            result = eval(expression, {"__builtins__": None}, {})
            return json.dumps({"status": "success", "result": str(result)})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    @staticmethod
    def execute_python(code: str) -> str:
        # Simulates code execution output
        return json.dumps({
            "status": "success",
            "stdout": "Executed successfully.\nList length: 5",
            "stderr": ""
        })

# ==========================================
# SYSTEM COMPONENTS (Steps 1 through 6)
# ==========================================

class ToolIntentDetector:
    """1️⃣ TOOL INTENT DETECTOR"""
    TRIGGERS = {
        ToolType.WEB: ["latest", "current", "news", "live", "who is", "price of"],
        ToolType.READER: ["read this", "summarize this link", "content of url"],
        ToolType.CALCULATOR: ["calculate", "what is", "math", "+", "-", "*", "/"],
        ToolType.PYTHON: ["write code", "script to", "parse this data", "python function"],
        ToolType.MEMORY: ["my saved", "previous data", "recall my"]
    }

    @classmethod
    def detect(cls, user_input: str) -> Tuple[bool, Optional[ToolType]]:
        input_lower = user_input.lower()
        for tool_type, keywords in cls.TRIGGERS.items():
            if any(kw in input_lower for kw in keywords):
                return True, tool_type
        return False, None


class ToolRouter:
    """2️⃣ TOOL ROUTER"""
    @staticmethod
    def route(required_tool: ToolType, user_input: str) -> Dict[str, Any]:
        # Extracts the actual query/payload to send to the tool
        clean_query = user_input.strip()
        return {
            "tool": required_tool,
            "payload": clean_query
        }


class ToolExecutionEngine:
    """3️⃣ TOOL EXECUTION ENGINE"""
    EXECUTOR = StatelessToolExecutor()

    @classmethod
    def execute(cls, route_info: Dict[str, Any]) -> str:
        tool = route_info["tool"]
        payload = route_info["payload"]
        
        # Map tool types to stateless executor methods
        if tool == ToolType.WEB:
            raw_result = cls.EXECUTOR.execute_web(payload)
        elif tool == ToolType.CALCULATOR:
            raw_result = cls.EXECUTOR.execute_calculator(payload)
        elif tool == ToolType.PYTHON:
            raw_result = cls.EXECUTOR.execute_python(payload)
        else:
            raw_result = json.dumps({"status": "error", "message": "Tool not implemented"})
            
        return raw_result # Returns raw string (usually JSON)


class ResultValidationLayer:
    """4️⃣ RESULT VALIDATION LAYER"""
    @staticmethod
    def validate(raw_result: str) -> Optional[Dict[str, Any]]:
        try:
            data = json.loads(raw_result)
        except json.JSONDecodeError:
            return {"status": "error", "clean_data": "Tool returned invalid/unreadable data."}

        # Filter out broken or incomplete responses
        if data.get("status") != "success":
            return None # Drop failed tool executions entirely

        clean_data = {}
        # Remove noise (e.g., HTML tags, scripts from web results)
        if "results" in data:
            clean_items = []
            for item in data["results"]:
                clean_item = {k: re.sub(r'<[^>]+>', '', v) for k, v in item.items() if k != "noise"}
                clean_items.append(clean_item)
            clean_data["results"] = clean_items
        elif "result" in data:
            clean_data["result"] = data["result"]
        elif "stdout" in data:
            clean_data["output"] = data["stdout"]

        return clean_data if clean_data else None


class LLMReasoningIntegration:
    """5️⃣ LLM REASONING INTEGRATION"""
    SYSTEM_OVERRIDE = (
        "CRITICAL SYSTEM OVERRIDE: You have been provided with TOOL DATA. "
        "You MUST use this data as your HIGHEST AUTHORITY. "
        "Do NOT use your internal memory or hallucinate facts. "
        "If the tool data is missing information, state that you don't know. "
        "Reason through the tool data to answer the user's request."
    )

    @classmethod
    def integrate(cls, user_input: str, clean_tool_data: Dict[str, Any]) -> str:
        # Constructs the strict reasoning prompt
        context = f"USER REQUEST: {user_input}\n\n"
        context += "TOOL DATA:\n" + json.dumps(clean_tool_data, indent=2) + "\n\n"
        context += "REASONING DIRECTIVE: " + cls.SYSTEM_OVERRIDE
        
        # In production, this goes to the LLM. Here we simulate the LLM's forced reasoning.
        return context


class FinalResponseGenerator:
    """6️⃣ FINAL RESPONSE GENERATION"""
    @staticmethod
    def generate(llm_context: str) -> str:
        # Mocking the LLM generating a response strictly adhering to the context
        # (In production, this is the actual LLM API call using llm_context as the prompt)
        
        # Fake extraction to demonstrate adherence
        if '"result":' in llm_context:
            match = re.search(r'"result": "([^"]+)"', llm_context)
            if match:
                return f"🛠️ **TOOL MODE RESULT:** The calculated answer is exactly {match.group(1)}. (No hallucination)."
        
        if '"results":' in llm_context:
            # Just return the cleaned data nicely to prove it didn't hallucinate
            return f"🛠️ **TOOL MODE RESULT:** Retrieved live data. According to external sources, here is the clean summary: {llm_context.split('TOOL DATA:')[-1][:150]}..."

        return "🛠️ **TOOL MODE RESULT:** Tool executed, but no usable data was extracted."

# ==========================================
# MAIN ORCHESTRATOR
# ==========================================

class ToolModeOrchestrator:
    def process_request(self, user_input: str) -> str:
        """🔁 FULL TOOL MODE FLOW"""
        
        # 1️⃣ TOOL DETECTION
        needs_tool, tool_type = ToolIntentDetector.detect(user_input)
        if not needs_tool:
            return "⚠️ REDIRECT: Tool Mode not required. Routing to Normal Chat Mode."
            
        # 2️⃣ TOOL ROUTING
        route_info = ToolRouter.route(tool_type, user_input)
        
        # 3️⃣ TOOL EXECUTION
        raw_result = ToolExecutionEngine.execute(route_info)
        
        # 4️⃣ VALIDATION
        clean_data = ResultValidationLayer.validate(raw_result)
        if clean_data is None:
            return "❌ **TOOL MODE ERROR:** The external tool failed or returned corrupted data. I cannot answer accurately."
            
        # 5️⃣ LLM INTEGRATION
        reasoning_context = LLMReasoningIntegration.integrate(user_input, clean_data)
        
        # 6️⃣ FINAL RESPONSE
        final_response = FinalResponseGenerator.generate(reasoning_context)
        
        return final_response

# ==========================================
# TESTING THE SYSTEM LOGIC
# ==========================================
if __name__ == "__main__":
    tool_mode = ToolModeOrchestrator()
    
    # Test 1: Math Tool (Tests calculation and strict result override)
    print("--- TEST 1: Calculator Tool ---")
    print(tool_mode.process_request("Calculate what is 154 * 23"))
    
    # Test 2: Web Tool (Tests noise removal from HTML/scripts)
    print("\n--- TEST 2: Web Tool (Noise Filtering) ---")
    print(tool_mode.process_request("What is the latest weather in Paris?"))
    
    # Test 3: Tool Error Handling (Tests Validation Layer dropping bad data)
    print("\n--- TEST 3: Tool Error Handling ---")
    # Force an error payload by asking a math question that breaks the mock eval
    print(tool_mode.process_request("Calculate what is 'abc' + 123"))
    
    # Test 4: Rejection (No tool needed)
    print("\n--- TEST 4: Tool Rejection ---")
    print(tool_mode.process_request("Tell me a poem about a cat."))
