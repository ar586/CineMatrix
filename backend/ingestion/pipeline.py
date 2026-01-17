from agents.orchestrator import AgentOrchestrator

class DataPipeline:
    def __init__(self):
        # Initialize the Orchestrator which builds the StateGraph
        self.orchestrator = AgentOrchestrator()

    def run_pipeline(self, movie_title: str, movie_id: str):
        """
        Run the ingestion pipeline via Agent Orchestrator.
        This replaces the old linear procedural method with a parallel, intelligent Graph.
        """
        print(f"🚀 Starting Intelligent Graph Pipeline for: {movie_title} ({movie_id})")
        
        try:
            # The orchestrator handles parallel fetching, validation (LLM), and result storage.
            self.orchestrator.process_movie(movie_id, movie_title)
            print("✅ Graph Pipeline Execution Complete.")
            
        except Exception as e:
            print(f"❌ Pipeline Failed: {e}")
            raise e
