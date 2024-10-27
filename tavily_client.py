import os
from tavily import TavilyClient
import streamlit as st


class TavilyClientApi:
    def __init__(self):
        self.api_key = st.secrets["TAVILY_SECRET_KEY"]
        self.tavily_client = TavilyClient(api_key=self.api_key)

    async def get_info_company(self, prompt: str) -> str:
        response = self.tavily_client.search(query=prompt, max_results=3, search_depth="advanced")
        return response['results']