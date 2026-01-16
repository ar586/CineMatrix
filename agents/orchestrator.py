import os
import sys
import logging
from langgraph.graph import StateGraph, END

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
        
        print("DEBUG: Initializing SentimentNode...", flush=True)
        # Initialize logic class for sentiment which needs __init__
        sentiment_processor = SentimentNode()
        self.workflow.add_node("sentiment", sentiment_processor)
        print("DEBUG: SentimentNode initialized", flush=True)
        
        # Add visualization node
        self.workflow.add_node("visualization", visualization_agent_node)
        
        # Define Edges (Parallel Fetching -> Sentiment Analysis)
        self.workflow.set_entry_point("reddit") # Start with one, but we want parallel. 
        # Actually LangGraph entry point is single. We can use a "fan out" pattern or just valid START->all.
        # But 'set_entry_point' takes one node. 
        # To run parallel, we usually use a 'start' node that does nothing or start with one and use parallel branches?
        # Better: set_entry_point to a dummy node or allow standard fan-out.
        # In this version of LangGraph, we can just set edges from START.
        
        self.workflow.set_entry_point("reddit") 
        # Wait, if I want parallel, I should probably put them in a map or use a Supervisor.
        # For simplicity in this iteration: I will chain them or use the map capabilities if available.
        # But wait, 'set_entry_point' implies sequential start?
        # Actually, let's use a simple sequential chain first to guarantee stability, or use a "router".
        # Or, simpler: Just define edges.
        # Using a specialized "fetch_all" map is better, but let's stick to a robust graph:
        # User request: "agents will now make only fetching... then computing".
        # Let's fan-out from a specialized start node if possible.
        # LangGraph allows START -> Node.
        
        # We'll try to run them in parallel branches if possible, but sequential is safer for now without 'Parallel' construct handy.
        # Let's run: Reddit -> YouTube -> Wiki -> IMDB -> Sentiment.
        # It's slower but simple.
        
        # Sequential workflow: Reddit → YouTube → Wiki → IMDB → TMDB → Firecrawl → News Insight → Sentiment → Visualization → END
        self.workflow.add_edge("reddit", "youtube")
        self.workflow.add_edge("youtube", "wiki")
        self.workflow.add_edge("wiki", "imdb")
        self.workflow.add_edge("imdb", "tmdb")
        self.workflow.add_edge("tmdb", "firecrawl")
        self.workflow.add_edge("firecrawl", "news_insight")
        self.workflow.add_edge("news_insight", "sentiment")
        self.workflow.add_edge("sentiment", "visualization")
        self.workflow.add_edge("visualization", END)
        
        self.app = self.workflow.compile()

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
            result = self.app.invoke(initial_state)
            
            # Since sentiment node does the saving, we just log completion
            errs = result.get("errors", [])
            if errs:
                logger.warning(f"⚠️ Completed with errors: {errs}")
            else:
                logger.info("✅ Pipeline Completed Successfully.")
                
        except Exception as e:
            logger.error(f"❌ Pipeline Failed: {e}")

if __name__ == "__main__":
    import backend.config # Ensure env vars loaded
    orch = AgentOrchestrator()
    orch.process_movie("tt1375666", "Inception")
