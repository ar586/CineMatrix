import os
import sys
import logging
from langgraph.graph import StateGraph, END, START

# Ensure backend modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.state import AgentState
from agents.nodes.sentiment_node import SentimentNode  # Import first to avoid segfault with LangChain/Google
from agents.nodes.reddit_node import reddit_agent_node
from agents.nodes.youtube_node import youtube_agent_node
from agents.nodes.wiki_node import wiki_agent_node
from agents.nodes.imdb_node import imdb_agent_node
from agents.nodes.tmdb_node import tmdb_agent_node
from agents.nodes.firecrawl_node import firecrawl_agent_node
from agents.nodes.news_insight_node import news_insight_node
from agents.nodes.trends_node import trends_agent_node
from agents.nodes.visualization_node import visualization_agent_node

# Basic Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        print("DEBUG: AgentOrchestrator.__init__ started", flush=True)
        # Initialize Graph
        self.workflow = StateGraph(AgentState)
        
        # Add Nodes
        self.workflow.add_node("reddit", reddit_agent_node)
        self.workflow.add_node("youtube", youtube_agent_node)
        self.workflow.add_node("wiki", wiki_agent_node)
        self.workflow.add_node("imdb", imdb_agent_node)
        self.workflow.add_node("tmdb", tmdb_agent_node)
        self.workflow.add_node("firecrawl", firecrawl_agent_node)
        self.workflow.add_node("news_insight", news_insight_node)
        self.workflow.add_node("trends", trends_agent_node)
        
        # Initialize class-based nodes
        sentiment_processor = SentimentNode()
        self.workflow.add_node("sentiment", sentiment_processor)
        self.workflow.add_node("visualization", visualization_agent_node)
        
        # --- Define Edges ---
        
        # 1. Start all fetchers in PARALLEL
        # This satisfies the requirement for efficiency and resilience.
        # If one fails (returns error/empty), others continue.
        self.workflow.add_edge(START, "reddit")
        self.workflow.add_edge(START, "youtube")
        self.workflow.add_edge(START, "wiki")
        self.workflow.add_edge(START, "imdb")
        self.workflow.add_edge(START, "tmdb")
        self.workflow.add_edge(START, "firecrawl")
        self.workflow.add_edge(START, "trends")
        
        # 2. Connect Signal Producers to Sentiment Analysis
        # Note: In LangGraph, if multiple nodes point to 'sentiment', it may trigger multiple times
        # or merge state depending on execution. State aggregation handles the 'signals' list safely.
        self.workflow.add_edge("reddit", "sentiment")
        self.workflow.add_edge("youtube", "sentiment")
        self.workflow.add_edge("wiki", "sentiment")
        self.workflow.add_edge("imdb", "sentiment")
        
        # 3. Connect News Data Flow
        self.workflow.add_edge("firecrawl", "news_insight")
        # News insight saves to DB directly, but we can connect to visualization
        self.workflow.add_edge("news_insight", "visualization")
        
        # 4. Connect Meta/Trends to Visualization
        self.workflow.add_edge("tmdb", "visualization")
        self.workflow.add_edge("trends", "visualization")
        
        # 5. Connect Sentiment to Visualization
        self.workflow.add_edge("sentiment", "visualization")
        
        # 6. End
        self.workflow.add_edge("visualization", END)
        
        self.app = self.workflow.compile()
        print("DEBUG: AgentOrchestrator Graph Compiled", flush=True)

    def process_movie(self, movie_id: str, movie_title: str):
        """
        Run the agentic pipeline.
        """
        logger.info(f"🎬 Processing Movie: {movie_title} ({movie_id})")
        
        initial_state = {
            "movie_title": movie_title,
            "movie_id": movie_id,
            "signals": [],
            "errors": [],
            "cast": [],
            "news_articles": []
        }
        
        try:
            # Invoke the graph
            # This will run the parallel workflow
            result = self.app.invoke(initial_state)
            
            errs = result.get("errors", [])
            if errs:
                logger.warning(f"⚠️ Pipeline finished with some errors: {errs}")
            else:
                logger.info("✅ Pipeline Completed Successfully.")
                
            return result
                
        except Exception as e:
            logger.error(f"❌ Pipeline Critical Failure: {e}")
            raise e

if __name__ == "__main__":
    import backend.config # Ensure env vars loaded
    orch = AgentOrchestrator()
    orch.process_movie("tt1375666", "Inception")
