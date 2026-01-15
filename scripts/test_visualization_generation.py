"""
Standalone test for visualization generation
Tests the visualization node without requiring the full orchestrator pipeline
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import backend.config  # Load env
from agents.nodes.visualization_node import VisualizationGenerator

def test_visualization_generation():
    """Test generating visualizations for a movie"""
    
    # Test with a known movie
    movie_id = "tt1457767"  # The Conjuring
    movie_title = "The Conjuring"
    
    print(f"🎨 Testing visualization generation for {movie_title}...")
    
    try:
        generator = VisualizationGenerator()
        generator.generate_and_cache(movie_id, movie_title)
        print(f"✅ Successfully generated and cached visualizations!")
        
        # Verify they were saved
        db = generator.db_client.get_db()
        if db is not None:
            count = db.visualization_components.count_documents({"movie_id": movie_id})
            print(f"📊 Found {count} visualizations in database")
            
            # Show a sample
            sample = db.visualization_components.find_one({"movie_id": movie_id})
            if sample:
                print(f"\n📝 Sample visualization:")
                print(f"   ID: {sample.get('component_id')}")
                print(f"   Type: {sample.get('type')}")
                print(f"   Priority: {sample.get('priority')}")
                print(f"   Title: {sample.get('spec', {}).get('title', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_visualization_generation()
