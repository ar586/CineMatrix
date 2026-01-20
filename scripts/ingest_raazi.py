
from agents.orchestrator import AgentOrchestrator
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # Raazi IMDB ID
    movie_id = "tt7098674" 
    title = "Raazi"
    
    orch = AgentOrchestrator()
    orch.process_movie(movie_id, title)
