from sentiment_analyzer import ValueExpression
from tavily_client import TavilyClientApi


class NewAnalyzer:
    def __init__(self, tavily_client: TavilyClientApi):
        self.tavily_client = tavily_client

    async def analyze(self, expression: ValueExpression):
        prompt = (
        f"Provide a detailed analysis of systemic risks associated with {expression.content}. "
        f"Specifically, focus on how this company influences market indices like the Bloomberg 500 or S&P 500, "
        f"and include any significant statistics regarding its performance this year."
        )
        return await self.tavily_client.get_info_company(prompt)