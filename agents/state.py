from typing import List, Dict, TypedDict, Annotated
import operator

class SourceSentiment(TypedDict):
    source: str
    text: str
    url: str
    metadata: Dict

class AgentState(TypedDict):
    movie_title: str
    movie_id: str
    # aggregated signals from all agents
    signals: Annotated[List[SourceSentiment], operator.add]
    # logs or errors during execution
    errors: Annotated[List[str], operator.add]
    # news articles from Firecrawl
    news_articles: Annotated[List[Dict], operator.add]
    # cast info for better query generation
    cast: List[str]
