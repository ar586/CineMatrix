import logging
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from typing import Optional

from backend import config

logger = logging.getLogger(__name__)

class ContentValidator:
    def __init__(self):
        api_key = config.GEMINI_API_KEY
        if not api_key:
            logger.warning("GEMINI_API_KEY missing. Validation will be skipped (auto-approve).")
            self.llm = None
        else:
            self.llm = ChatGoogleGenerativeAI(
        model=config.LLM_MODEL, 
                google_api_key=api_key,
                temperature=0
            )

    def validate(self, content: str, topic: str, source_type: str) -> bool:
        """
        Validates if the content is relevant to the topic (movie).
        Returns True if relevant, False otherwise.
        """
        if not self.llm or not content:
            return True # Fail open if no LLM or empty content (let pipeline handle empty)

        try:
            # Truncate content to avoid token limits and speed up
            snippet = content[:2000]
            
            prompt = f"""
            You are a validation agent. Your task is to verify if the provided text data is relevant to the movie '{topic}'.
            
            Context:
            - Source: {source_type}
            
            Data Snippet:
            "{snippet}..."
            
            Task:
            Is this data related to the movie '{topic}'? 
            - If it is a different movie with the same name, or completely unrelated (e.g. "Soyuz 13" vs "13B movie"), return NO.
            - If it is about the movie, return YES.
            
            Response (YES/NO only):
            """
            
            msg = HumanMessage(content=prompt)
            res = self.llm.invoke([msg])
            answer = res.content.strip().upper()
            
            if "YES" in answer:
                logger.info(f"✅ [{source_type}] Validation Passed for '{topic}'")
                return True
            else:
                logger.warning(f"❌ [{source_type}] Validation Failed for '{topic}'. LLM said: {answer}")
                return False
                
        except Exception as e:
            logger.error(f"Validation Error: {e}")
            return True # Fail open on error
