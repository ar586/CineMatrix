
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

        # 2. Extract Metadata & Analyze
        metadata = {}
        source_ref = {}
        
        if source_type == "reddit":
            source_ref = {"post_id": item.get("post_id") or item.get("id")}
            metadata = {
                "sub_source": "post" if "title" in item else "comment",
                "upvotes": item.get("score", 0),
                "num_comments": item.get("num_comments", 0)
            }
        elif source_type == "youtube":
            source_ref = {"video_id": item.get("video_id") or item.get("id")}
            if "stats" in item:
                 metadata = item["stats"]
            elif "likes" in item:
                 metadata = {"likes": item["likes"], "sub_source": "comment"}

        print(f"Analyzing text length: {len(text)}")
        # Pass source and metadata to engine for context-aware analysis
        output = self.engine.analyze(text, source=source_type, metadata=metadata)

        # 3. Construct DB Object
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
            engagement_weight=metadata if metadata else None,
            model={
                "name": "roberta-deberta-ensemble",
                "version": "1.0",
                "aggregation": "discussion_text"
            },
            processed_at=datetime.utcnow()
        )

        # 4. Save (Deduplicated)
        db = self.db_client.get_db()
        try:
            from backend.database.dedup import bulk_upsert_sentiments
            
            # Convert to dict and ensure _id is handled by dedup logic
            doc = sentiment_analysis.model_dump(by_alias=True)
            
            bulk_upsert_sentiments(db, [doc])
            print(f"Saved sentiment for {source_type} {source_ref}")
        except Exception as e:
            print(f"Error saving to DB: {e}")

if __name__ == "__main__":
    # Example usage
    worker = SentimentWorker()
    # worker.process_item({...}, "reddit", "tt12345")
