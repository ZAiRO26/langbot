"""
Ollama Local LLM Client for LinkedIn Automation Agent
Replaces Perplexity AI with local Ollama instance
"""

import requests
import json
import logging
from typing import List, Dict, Any
from asyncio_throttle import Throttler
import asyncio

logger = logging.getLogger(__name__)

class OllamaOpenAIClient:
    """
    Ollama client compatible with OpenAI format for local LLM inference
    """
    
    def __init__(self, base_url: str = "http://localhost:11434/v1", 
                 model: str = "deepseek-r1:8b"):
        self.base_url = base_url
        self.model = model
        self.api_key = "ollama"  # Dummy key for compatibility
        
        # Rate limiting for local requests (more lenient than API limits)
        self.throttler = Throttler(rate_limit=10, period=1)  # 10 requests per second
        
        logger.info(f"Initialized Ollama client with model: {model}")
    
    def chat_complete(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Send chat completion request to Ollama
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            # Increased timeout for deepseek-r1:8b model which can be slower
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=180  # 3 minutes timeout for local model
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                logger.debug(f"Ollama response received: {len(result)} characters")
                return result
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama connection error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def generate_linkedin_post(self, topic: str, context: str = "") -> str:
        """
        Generate a LinkedIn post about a specific topic
        
        Args:
            topic: The main topic for the post
            context: Additional context or recent trends
            
        Returns:
            Generated LinkedIn post content
        """
        async with self.throttler:
            system_prompt = """You are a LinkedIn content expert. Create engaging, professional LinkedIn posts that:
            - Are ~500 words (aim 450–550 words)
            - Include relevant hashtags (3–5)
            - Start with a strong, concise hook
            - Provide specific, practical value to professionals
            - End with a thoughtful question to encourage discussion
            - Use professional, warm, and concise tone
            - Avoid emojis and excessive exclamation marks"""
            
            user_prompt = f"Create a LinkedIn post about: {topic}\n\nRequirements: Write about 500 words, professional tone, concrete examples, a brief CTA, 3–5 relevant hashtags, and end with a question."
            if context:
                user_prompt += f"\n\nAdditional context: {context}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            try:
                return self.chat_complete(messages, temperature=0.8)
            except Exception as e:
                logger.error(f"Failed to generate LinkedIn post: {str(e)}")
                return f"Exciting developments in {topic}! What are your thoughts on this trend? #LinkedIn #Professional"
    
    async def generate_comment(self, post_content: str, author_name: str = "") -> str:
        """
        Generate a thoughtful comment for a LinkedIn post
        
        Args:
            post_content: The content of the post to comment on
            author_name: Name of the post author (optional)
            
        Returns:
            Generated comment text
        """
        async with self.throttler:
            system_prompt = """You are a LinkedIn engagement expert. Write precise, human-like comments that:
            - Are 25–40 words long
            - Reference a specific detail from the post
            - Avoid generic platitudes and hashtags
            - Use first-person, professional tone
            - Ask one brief follow-up question when appropriate
            - No emojis or exclamation floods"""
            
            user_prompt = f"Write a concise, specific comment for this LinkedIn post (25–40 words):\n\n{post_content[:500]}"
            if author_name:
                user_prompt += f"\n\nPost author: {author_name}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            try:
                return self.chat_complete(messages, temperature=0.7)
            except Exception as e:
                logger.error(f"Failed to generate comment: {str(e)}")
                return "Great insights! Thanks for sharing your perspective on this."
    
    async def analyze_post_sentiment(self, post_content: str) -> str:
        """
        Analyze the sentiment and tone of a LinkedIn post
        
        Args:
            post_content: The post content to analyze
            
        Returns:
            Sentiment analysis (positive, neutral, negative, professional, etc.)
        """
        async with self.throttler:
            system_prompt = """You are a sentiment analysis expert. Analyze LinkedIn posts and return:
            - Overall sentiment: positive, neutral, negative
            - Tone: professional, casual, promotional, educational, personal
            - Engagement potential: high, medium, low
            - Key themes (1-3 words)
            
            Format: sentiment|tone|engagement|themes"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this LinkedIn post:\n\n{post_content[:300]}"}
            ]
            
            try:
                return self.chat_complete(messages, temperature=0.3)
            except Exception as e:
                logger.error(f"Failed to analyze sentiment: {str(e)}")
                return "neutral|professional|medium|general"
    
    async def suggest_topics(self, industry: str = "technology", count: int = 5) -> List[str]:
        """
        Suggest trending topics for LinkedIn content
        
        Args:
            industry: Industry focus for topics
            count: Number of topics to suggest
            
        Returns:
            List of suggested topics
        """
        async with self.throttler:
            system_prompt = f"""You are a LinkedIn content strategist. Suggest {count} trending topics for {industry} professionals that are:
            - Currently relevant and timely
            - Engaging for professional audience
            - Not overly technical or niche
            - Good for generating discussion
            
            Return only the topic titles, one per line."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Suggest {count} LinkedIn content topics for {industry} industry"}
            ]
            
            try:
                response = self.chat_complete(messages, temperature=0.8)
                topics = [topic.strip() for topic in response.split('\n') if topic.strip()]
                return topics[:count]  # Ensure we don't exceed requested count
            except Exception as e:
                logger.error(f"Failed to suggest topics: {str(e)}")
                # Fallback topics
                return [
                    "Digital Transformation Trends",
                    "Remote Work Best Practices", 
                    "Leadership in Uncertain Times",
                    "Professional Development Tips",
                    "Industry Innovation Updates"
                ][:count]
    
    def test_connection(self) -> bool:
        """
        Test connection to Ollama server
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_messages = [
                {"role": "user", "content": "Hello, are you working?"}
            ]
            response = self.chat_complete(test_messages, temperature=0.1)
            logger.info("Ollama connection test successful")
            return True
        except Exception as e:
            logger.error(f"Ollama connection test failed: {str(e)}")
            return False

# Usage example and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_ollama():
        client = OllamaOpenAIClient()
        
        # Test connection
        if not client.test_connection():
            print("❌ Ollama connection failed!")
            return
        
        print("✅ Ollama connection successful!")
        
        # Test post generation
        try:
            post = await client.generate_linkedin_post("AI in business automation")
            print(f"\n📝 Generated Post:\n{post}")
        except Exception as e:
            print(f"❌ Post generation failed: {e}")
        
        # Test comment generation
        try:
            comment = await client.generate_comment("Just launched our new AI product!")
            print(f"\n💬 Generated Comment:\n{comment}")
        except Exception as e:
            print(f"❌ Comment generation failed: {e}")
    
    asyncio.run(test_ollama())