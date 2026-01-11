
from ml.pipelines.discussion_builder import DiscussionBuilder
from ml.pipelines.sentiment_engine import SentimentEngine
from ml.schemas.source_sentiment import SentimentInput
from backend.database.models import SentimentAnalysis
from backend.database.client import MongoDBClient
from datetime import datetime

class SentimentWorker:
    def __init__(self):
        self.builder = DiscussionBuilder()
        self.engine = SentimentEngine()
        self.db_client = MongoDBClient()

    def process_item(self, item: dict, source_type: str, movie_id: str):
        """
        Process a raw item (post/video) -> SentimentAnalysis -> DB
        """
        # 1. Build Text
        text = self.builder.build_text(item, source_type)
        if not text:
            print(f"Skipping empty text for item in {source_type}")
            return

        # 2. Analyze
        print(f"Analyzing text length: {len(text)}")
        output = self.engine.analyze(text)

        # 3. Construct DB Object
        # Extract ID specific to source
        source_ref = {}
        if source_type == "reddit":
            source_ref = {"post_id": item.get("id")}
        elif source_type == "youtube":
            source_ref = {"video_id": item.get("id")}

        # Create Pydantic model
        sentiment_analysis = SentimentAnalysis(
            movie_id=movie_id,
            source=source_type,
            source_ref=source_ref,
            sentiment={
                "label": output.label,
                "score": output.score,
                "confidence": output.confidence
            },
            aspects=output.aspects,
            engagement_weight=item.get("engagement", {}), # passed pre-formatted or extract here?
            # Assuming item has engagement dict or we parse it. 
            # For simplicity let's assume ingestion layer passes it or we extract.
            # DiscussionBuilder doesn't extract structure, just text.
            # Let's extract basic engagement here or expect it in item.
            model={
                "name": "roberta-deberta-ensemble",
                "version": "1.0",
                "aggregation": "discussion_text"
            },
            processed_at=datetime.utcnow()
        )

        # 4. Save
        db = self.db_client.get_db()
        try:
            db.source_sentiments.insert_one(sentiment_analysis.model_dump(by_alias=True))
            print(f"Saved sentiment for {source_type} {source_ref}")
        except Exception as e:
            print(f"Error saving to DB: {e}")

if __name__ == "__main__":
    # Example usage
    worker = SentimentWorker()
    # worker.process_item({...}, "reddit", "tt12345")
