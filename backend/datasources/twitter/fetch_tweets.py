
from .client import GrokClient
from .parser import GrokParser

class TwitterFetcher:
    def __init__(self):
        self.client = GrokClient()
        self.parser = GrokParser()

    def get_discussions(self, title):
        """
        Ask Grok to search X for the movie and return a summary.
        """
        if not self.client.api_key:
            print("XAI_API_KEY is missing. Skipping Twitter/Grok fetch.")
            return None

        prompt = f"""
        Search X (Twitter) for recent discussions, reviews, and sentiment regarding the movie "{title}".
        
        Provide a summary in the following JSON format ONLY:
        {{
            "sentiment": "Positive" | "Negative" | "Mixed",
            "score": <0-100 integer representing positive sentiment magnitude>,
            "summary": "<A concise paragraph summarizing what people are saying>",
            "trending_topics": ["<topic1>", "<topic2>", ...],
            "recent_tweets": [
                {{"user": "<username>", "text": "<tweet_text>"}},
                ...
            ]
        }}
        """

        messages = [
            {"role": "system", "content": "You are a helpful assistant that analyzes social media trends on X. Output valid JSON only."},
            {"role": "user", "content": prompt}
        ]

        response_text = self.client.chat_completion(messages)
        return self.parser.parse_response(response_text)

if __name__ == "__main__":
    fetcher = TwitterFetcher()
    title = "Inception"
    print(f"Asking Grok about {title} on X...")
    data = fetcher.get_discussions(title)
    
    if data:
        print(f"Sentiment: {data.get('sentiment')} ({data.get('score')}/100)")
        print(f"Summary: {data.get('summary')}")
        print("Topics:", data.get('trending_topics'))
    else:
        print("No data returned.")
