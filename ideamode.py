import re
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# ==========================================
# DATA MODELS & ENUMS
# ==========================================

class UserTier(Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"

class CreativityMode(Enum):
    SAFE = "safe"
    BALANCED = "balanced"
    HIGH_CREATIVITY = "high_creativity"

class Category(Enum):
    BUSINESS = "Business"
    STARTUP = "Startup"
    CONTENT_CREATION = "Content creation"
    EDUCATION = "Education"
    TECHNOLOGY = "Technology"
    APP_DEVELOPMENT = "App development"
    SOCIAL_MEDIA = "Social media"
    GENERAL_CREATIVITY = "General creativity"

@dataclass
class StructuredIdea:
    title: str
    description: str
    target_audience: str
    core_value: str
    monetization: str
    difficulty: str
    relevance_score: float = 0.0

# ==========================================
# SYSTEM COMPONENTS (Steps 1 through 8)
# ==========================================

class IdeaModeDetector:
    """1️⃣ IDEA MODE DETECTOR"""
    TRIGGER_KEYWORDS = [
        "brainstorm", "ideas for", "give me ideas", "suggest some", 
        "come up with", "idea generation", "create a concept", "what are some ways"
    ]

    @classmethod
    def detect(cls, user_input: str) -> Dict[str, Any]:
        input_lower = user_input.lower()
        for kw in cls.TRIGGER_KEYWORDS:
            if kw in input_lower:
                return {"active": True, "redirect": False}
        return {"active": False, "redirect_to": "NORMAL_CHAT"}

class TopicExtractor:
    """2️⃣ TOPIC EXTRACTOR"""
    @staticmethod
    def extract(user_input: str) -> str:
        # Normalize and remove trigger words to isolate the core topic
        clean_text = user_input.lower()
        noise_words = [
            "i need", "give me", "some", "ideas for", "about", 
            "can you brainstorm", "please", "what are some"
        ]
        for word in noise_words:
            clean_text = clean_text.replace(word, "")
        return clean_text.strip().capitalize()

class CategoryClassifier:
    """3️⃣ CATEGORY CLASSIFIER"""
    MAPPING = {
        "business": Category.BUSINESS, "startup": Category.STARTUP,
        "app": Category.APP_DEVELOPMENT, "software": Category.TECHNOLOGY,
        "tiktok": Category.SOCIAL_MEDIA, "youtube": Category.CONTENT_CREATION,
        "school": Category.EDUCATION, "course": Category.EDUCATION,
        "tech": Category.TECHNOLOGY, "ai": Category.TECHNOLOGY
    }

    @classmethod
    def classify(cls, topic: str) -> Category:
        for keyword, category in cls.MAPPING.items():
            if keyword in topic.lower():
                return category
        return Category.GENERAL_CREATIVITY

class TierLimitController:
    """4️⃣ TIER & LIMIT CONTROLLER"""
    LIMITS = {
        UserTier.FREE: {"max_ideas": 3, "depth": "brief"},
        UserTier.PRO: {"max_ideas": 7, "depth": "standard"},
        UserTier.PREMIUM: {"max_ideas": 15, "depth": "detailed"}
    }

    @classmethod
    def get_limits(cls, tier: UserTier) -> Dict[str, Any]:
        return cls.LIMITS.get(tier, cls.LIMITS[UserTier.FREE])

class CreativityEngine:
    """5️⃣ CREATIVITY ENGINE"""
    @staticmethod
    def generate_raw_ideas(topic: str, category: Category, limits: Dict, creativity: CreativityMode) -> List[Dict]:
        # In production, this constructs a strict JSON prompt for the LLM.
        # We simulate the LLM returning a list of raw idea dictionaries here.
        raw_ideas = []
        count = limits["max_ideas"] + 4 # Generate extra for the ranking/filtering step to discard later
        
        creativity_prefix = {
            CreativityMode.SAFE: "Practical",
            CreativityMode.BALANCED: "Mixed",
            CreativityMode.HIGH_CREATIVITY: "Unconventional"
        }[creativity]

        for i in range(count):
            raw_ideas.append({
                "title": f"{creativity_prefix} {category.value} Idea {i+1} for '{topic}'",
                "description": f"A {creativity_prefix.lower()} approach to {topic} in the {category.value} space. {'Highly innovative' if creativity == CreativityMode.HIGH_CREATIVITY else 'Standard execution'}.",
                "target_audience": f"Target audience for idea {i+1}",
                "core_value": f"Core value proposition {i+1}",
                "monetization": f"Revenue model {i+1}",
                "difficulty": random.choice(["Easy", "Medium", "Hard"])
            })
        return raw_ideas

class IdeaStructuringEngine:
    """6️⃣ IDEA STRUCTURING ENGINE"""
    @staticmethod
    def structure(raw_ideas: List[Dict]) -> List[StructuredIdea]:
        structured_list = []
        for idea in raw_ideas:
            # Enforce required fields, drop malformed data
            if all(key in idea for key in ["title", "description", "target_audience", "core_value", "monetization", "difficulty"]):
                structured_list.append(StructuredIdea(**idea))
        return structured_list

class RankingFilteringEngine:
    """7️⃣ RANKING & FILTERING ENGINE"""
    @staticmethod
    def process(ideas: List[StructuredIdea], max_limit: int, topic: str) -> List[StructuredIdea]:
        # 1. Score relevance (Mocked: in production, use an embedding similarity check)
        for idea in ideas:
            score = random.uniform(0.5, 1.0)
            if topic.lower() in idea.title.lower(): score += 0.2 # Boost if exact topic match
            idea.relevance_score = min(score, 1.0)

        # 2. Remove duplicates (Mocked: simple title similarity check)
        unique_ideas = []
        seen_titles = set()
        for idea in ideas:
            normalized_title = re.sub(r'[^a-z0-9]', '', idea.title.lower())
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_ideas.append(idea)

        # 3. Rank best ideas first (Descending order by relevance score)
        ranked_ideas = sorted(unique_ideas, key=lambda x: x.relevance_score, reverse=True)

        # 4. Enforce user tier limit
        return ranked_ideas[:max_limit]

class ResponseFormatter:
    """8️⃣ RESPONSE FORMATTER"""
    @staticmethod
    def format(ideas: List[StructuredIdea], category: Category) -> str:
        if not ideas:
            return "💡 **NOTEGPT Idea Mode:** Could not generate valid ideas for this request."
            
        output = f"💡 **NOTEGPT Idea Mode** | Category: {category.value}\n"
        output += "━" * 50 + "\n\n"

        for i, idea in enumerate(ideas, 1):
            output += f"**{i}. {idea.title}**\n"
            output += f"   📝 *Description:* {idea.description}\n"
            output += f"   🎯 *Target Audience:* {idea.target_audience}\n"
            output += f"   💎 *Core Value:* {idea.core_value}\n"
            output += f"   💰 *Monetization:* {idea.monetization}\n"
            output += f"   📈 *Difficulty:* {idea.difficulty}\n"
            output += "-" * 40 + "\n"
            
        return output

# ==========================================
# MAIN ORCHESTRATOR (The Full Idea Mode Flow)
# ==========================================

class IdeaModeOrchestrator:
    def __init__(self, user_tier: UserTier = UserTier.FREE, creativity_mode: CreativityMode = CreativityMode.BALANCED):
        self.user_tier = user_tier
        self.creativity_mode = creativity_mode

    def process_request(self, user_input: str) -> str:
        """🔁 FULL IDEA MODE FLOW"""

        # 1️⃣ IDEA MODE DETECTOR
        detection = IdeaModeDetector.detect(user_input)
        if not detection["active"]:
            return f"⚠️ REDIRECT: Normal chat request detected. Rerouting to {detection['redirect_to']}..."

        # 2️⃣ TOPIC EXTRACTION
        topic = TopicExtractor.extract(user_input)

        # 3️⃣ CATEGORY CLASSIFICATION
        category = CategoryClassifier.classify(topic)

        # 4️⃣ TIER LIMIT CHECK
        limits = TierLimitController.get_limits(self.user_tier)

        # 5️⃣ CREATIVITY GENERATION
        raw_ideas = CreativityEngine.generate_raw_ideas(topic, category, limits, self.creativity_mode)

        # 6️⃣ IDEA STRUCTURING
        structured_ideas = IdeaStructuringEngine.structure(raw_ideas)

        # 7️⃣ RANKING & FILTERING
        final_ideas = RankingFilteringEngine.process(structured_ideas, limits["max_ideas"], topic)

        # 8️⃣ RESPONSE FORMATTING
        final_output = ResponseFormatter.format(final_ideas, category)

        # FINAL OUTPUT
        return final_output

# ==========================================
# TESTING THE SYSTEM LOGIC
# ==========================================
if __name__ == "__main__":
    # Instantiate with different tier/mode settings to see the controller in action
    print("--- TEST 1: Free Tier (Should output 3 ideas) ---")
    free_bot = IdeaModeOrchestrator(user_tier=UserTier.FREE, creativity_mode=CreativityMode.SAFE)
    print(free_bot.process_request("Can you brainstorm some ideas for an app"))

    print("\n--- TEST 2: Premium Tier & High Creativity (Should output 15 ideas) ---")
    premium_bot = IdeaModeOrchestrator(user_tier=UserTier.PREMIUM, creativity_mode=CreativityMode.HIGH_CREATIVITY)
    # We just print the first 500 chars to prove it generated 15 without spamming the console
    result_premium = premium_bot.process_request("I need ideas for a startup using AI in education")
    print(result_premium[:500] + "\n... [TRUNCATED FOR BREVITY, TOTAL IDEAS: 15]")

    print("\n--- TEST 3: Normal Chat Rejection ---")
    print(free_bot.process_request("What is the capital of France?"))
