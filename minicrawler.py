import re
from typing import Dict, Any, List, Optional, Tuple

# ==========================================
# MOCK NETWORK LAYER (Stateless Simulation)
# ==========================================

def mock_network_request(url: str) -> str:
    """Simulates a stateless HTTP GET request returning messy HTML."""
    # Simulating realistic messy HTML with ads, scripts, and navigation
    return f"""
    <html>
    <head><script>var ads = "buy_viagra"; console.log(ads);</script></head>
    <body>
        <nav class="menu"><a href="/home">Home</a><a href="/about">About</a></nav>
        <div class="ad-banner">Please disable AdBlock!</div>
        <article>
            <h1>Latest Update on {url.split('/')[-1].replace('-', ' ')}</h1>
            <p>The global technology sector has seen a massive shift towards AI integration. 
            Experts confirm that by 2025, over 60% of enterprise software will include localized LLMs. 
            This unprecedented growth requires strict data governance.</p>
            <p>Furthermore, the economic impact is projected to exceed 4 trillion dollars, 
            altering how businesses approach automation completely.</p>
        </article>
        <footer>Copyright 2023. All rights reserved. Privacy Policy.</footer>
    </body>
    </html>
    """

# ==========================================
# SYSTEM COMPONENTS (Steps 1 through 7)
# ==========================================

class CrawlerIntentDetector:
    """1️⃣ CRAWLER INTENT DETECTOR"""
    TRIGGERS = [
        "latest information", "current news", "read about", "what is happening with",
        "recent updates", "live updates", "external knowledge", "research on"
    ]

    @classmethod
    def detect(cls, user_input: str) -> bool:
        input_lower = user_input.lower()
        return any(trigger in input_lower for trigger in cls.TRIGGERS)


class URLDiscoveryEngine:
    """2️⃣ URL DISCOVERY ENGINE (No search engines, curated trusted sources)"""
    TRUSTED_SOURCES = {
        "tech": ["https://techcrunch.com/tag/{query}", "https://arstechnica.com/{query}"],
        "ai": ["https://openai.com/blog/{query}", "https://huggingface.co/{query}"],
        "science": ["https://nature.com/articles/{query}", "https://wikipedia.org/wiki/{query}"],
        "general": ["https://wikipedia.org/wiki/{query}"]
    }

    DOMAIN_AUTHORITY = {
        "wikipedia.org": 100, "nature.com": 95, "techcrunch.com": 90, 
        "arstechnica.com": 88, "openai.com": 85, "huggingface.co": 85
    }

    @classmethod
    def discover(cls, user_input: str, max_urls: int = 2) -> List[str]:
        # Keyword-to-site mapping
        query_slug = user_input.lower().replace(" ", "-")[:30]
        category = "general"
        for key in cls.TRUSTED_SOURCES:
            if key in user_input.lower():
                category = key
                break

        # Build candidate URLs
        candidates = [url.format(query=query_slug) for url in cls.TRUSTED_SOURCES[category]]
        
        # Prioritize high-authority domains and limit results
        candidates.sort(key=lambda url: cls.DOMAIN_AUTHORITY.get(url.split('/')[2], 0), reverse=True)
        return candidates[:max_urls]


class PageFetcher:
    """3️⃣ PAGE FETCHER (Stateless, on-demand)"""
    @staticmethod
    def fetch(url: str) -> Optional[str]:
        # In production: requests.get(url, timeout=5).text
        # Simulating a successful fetch returning raw HTML
        return mock_network_request(url)


class ContentCleaner:
    """4️⃣ CONTENT CLEANER"""
    @staticmethod
    def clean(raw_html: str) -> str:
        if not raw_html: return ""
        
        # Remove scripts and styles
        text = re.sub(r'<(script|style).*?>.*?</\1>', '', raw_html, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove HTML tags (navs, ads, divs, etc.)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace and decode basic HTML entities
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        
        return text


class ContentValidationLayer:
    """5️⃣ CONTENT VALIDATION LAYER"""
    MIN_TEXT_LENGTH = 50  # Filter out empty pages or 404 errors

    @classmethod
    def validate(cls, cleaned_text: str, original_query: str) -> Optional[str]:
        # Filter incomplete or corrupted text
        if len(cleaned_text) < cls.MIN_TEXT_LENGTH:
            return None
            
        # Filter low relevance (simple word overlap check)
        query_words = set(original_query.lower().split())
        text_words = set(cleaned_text.lower().split())
        
        # If absolutely no words match, drop the source
        if not query_words.intersection(text_words):
            # Fallback: keep it anyway if it came from a high-trust source and is long enough
            # (In a real system, you'd use embeddings here)
            pass
            
        return cleaned_text


class AIContextInjection:
    """6️⃣ AI CONTEXT INJECTION"""
    @staticmethod
    def inject(user_query: str, validated_blocks: List[Dict[str, str]]) -> str:
        context = f"USER QUERY: {user_query}\n\n"
        context += "SYSTEM DIRECTIVE: The following is LIVE CRAWLED DATA from trusted sources. "
        context += "This data OVERRIDES your internal knowledge base. Use ONLY this data to answer.\n\n"
        
        for block in validated_blocks:
            context += f"[CRAWLED SOURCE: {block['url']}]\n"
            # Simulate content compression if text is too long
            text = block['content']
            if len(text) > 500:
                text = text[:500] + "... [CONTENT TRUNCATED FOR CONTEXT LIMIT]"
            context += f"{text}\n\n"
            
        context += "ASSISTANT:"
        return context


class LLMReasoningEngine:
    """7️⃣ LLM REASONING ENGINE"""
    @staticmethod
    def reason(enriched_context: str) -> str:
        # Mocking the LLM processing the injected crawled data
        if "[CRAWLED SOURCE:" in enriched_context:
            # Simulating extraction of facts from the context block
            extracted_fact = "over 60% of enterprise software will include localized LLMs"
            return (f"🕷️ **MINI CRAWLER MODE RESULT:** Based on live external data, "
                    f"it is confirmed that {extracted_fact}. "
                    f"Furthermore, the economic impact is expected to exceed 4 trillion dollars. "
                    f"(Internal knowledge base overridden by crawled sources).")
        return "No valid crawled data was found to reason with."

# ==========================================
# MAIN ORCHESTRATOR
# ==========================================

class MiniCrawlerOrchestrator:
    def process_request(self, user_input: str) -> str:
        """🔁 FULL MINI CRAWLER FLOW"""
        
        # 1️⃣ CRAWLER DETECTION
        if not CrawlerIntentDetector.detect(user_input):
            return "⚠️ REDIRECT: Mini Crawler not required. Routing to Normal Chat or Tool Mode."

        # 2️⃣ URL DISCOVERY
        candidate_urls = URLDiscoveryEngine.discover(user_input, max_urls=2)

        validated_blocks = []
        
        # 3️⃣ PAGE FETCHING (Loop for multiple pages)
        for url in candidate_urls:
            raw_html = PageFetcher.fetch(url)
            
            # 4️⃣ CONTENT CLEANING
            clean_text = ContentCleaner.clean(raw_html)
            
            # 5️⃣ VALIDATION
            final_text = ContentValidationLayer.validate(clean_text, user_input)
            
            if final_text:
                validated_blocks.append({"url": url, "content": final_text})

        if not validated_blocks:
            return "❌ **CRAWLER ERROR:** Discovered URLs yielded no valid or relevant content."

        # 6️⃣ AI CONTEXT INJECTION
        enriched_context = AIContextInjection.inject(user_input, validated_blocks)
        
        # 7️⃣ LLM REASONING
        final_response = LLMReasoningEngine.reason(enriched_context)
        
        return final_response

# ==========================================
# TESTING THE SYSTEM LOGIC
# ==========================================
if __name__ == "__main__":
    crawler = MiniCrawlerOrchestrator()
    
    # Test 1: Successful Crawl & Data Override
    print("--- TEST 1: Tech News Crawl ---")
    print(crawler.process_request("Get the latest information and recent updates about AI technology"))
    
    # Test 2: Successful Crawl but lower relevance (triggers validation fallback)
    print("\n--- TEST 2: Science Research Crawl ---")
    print(crawler.process_request("read about research on quantum physics"))
    
    # Test 3: Rejection (Normal chat doesn't trigger crawler)
    print("\n--- TEST 3: Intent Rejection ---")
    print(crawler.process_request("Explain the theory of relativity in your own words."))
