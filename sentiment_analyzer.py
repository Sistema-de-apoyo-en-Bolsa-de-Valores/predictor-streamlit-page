from pydantic import BaseModel
from model import ValueExpression
from open_ai_client import OpenAIClient

class SentimentAnalyzer:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    async def analyze(self, expression: ValueExpression) -> str:
        prompt = f'You receive multiple titles of news. Then you have to make a sentiment analysis of the following titles:{expression.content}, only response "POSITIVE" or "NEGATIVE"'
        return await self.openai_client.get_sentiment(prompt)
    
