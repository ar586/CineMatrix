import logging
import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.getcwd())

from agents.orchestrator import AgentOrchestrator

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    from backend import config
    
    # initialize
    orch = AgentOrchestrator()
    
    # Run for Dangal
    # IMDB ID for Dangal is tt5074352
    orch.process_movie("tt5074352", "Dangal")
