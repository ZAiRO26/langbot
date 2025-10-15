"""
Ollama Local LLM Client for LinkedIn Automation Agent
Updated to use local Ollama instead of Perplexity AI
"""

from ollama_client import OllamaOpenAIClient
import logging
from typing import List

logger = logging.getLogger(__name__)

class PerplexityClient:
    """
    Wrapper class to maintain compatibility while using Ollama backend
    """
    
    def __init__(self):
        """Initialize with Ollama client instead of Perplexity"""
        self.ollama_client = OllamaOpenAIClient()
        logger.info("Initialized PerplexityClient with Ollama backend")
        
    async def generate_linkedin_post(self, topic: str, context: str = "") -> str:
        """Generate LinkedIn post using Ollama"""
        return await self.ollama_client.generate_linkedin_post(topic, context)
    
    async def generate_comment(self, post_content: str, author_name: str = "") -> str:
        """Generate comment using Ollama"""
        return await self.ollama_client.generate_comment(post_content, author_name)
    

    
    async def analyze_post_sentiment(self, post_content: str) -> str:
        """Analyze post sentiment using Ollama"""
        return await self.ollama_client.analyze_post_sentiment(post_content)
    
    async def suggest_topics(self, industry: str = "technology", count: int = 5) -> List[str]:
        """Suggest topics using Ollama"""
        return await self.ollama_client.suggest_topics(industry, count)
    
    def test_connection(self) -> bool:
        """Test Ollama connection"""
        return self.ollama_client.test_connection()