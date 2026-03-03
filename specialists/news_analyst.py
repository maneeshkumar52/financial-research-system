import time
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

SYS = """You are a financial news analyst. Analyse news sentiment (-1.0 to 1.0), key events, management statements, regulatory developments. End with 4 bullet findings starting with '- '."""

MOCK_NEWS = [
    {"date": "2024-11-15", "headline": "Record Q3 revenue, beats consensus by 4%", "sentiment": 0.8},
    {"date": "2024-11-10", "headline": "CEO announces £150M AI investment over 3 years", "sentiment": 0.7},
    {"date": "2024-10-28", "headline": "Regulatory review of data practices initiated", "sentiment": -0.2},
    {"date": "2024-10-15", "headline": "Strategic cloud partnership announced", "sentiment": 0.6},
    {"date": "2024-09-30", "headline": "CFO departure with succession plan detailed", "sentiment": -0.1},
]


class NewsAnalyst(BaseSpecialist):
    specialist_type = SpecialistType.NEWS_ANALYST

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        start = time.time()
        news = context.get("news_data", MOCK_NEWS)
        news_text = "\n".join(f"- [{n['date']}] {n['headline']} (sentiment: {n['sentiment']})" for n in news)
        avg = sum(n["sentiment"] for n in news) / len(news)
        prompt = f"Company: {topic}\nAvg Sentiment: {avg:.2f}\n\nRecent News:\n{news_text}\n\nAnalyse narrative, key themes, and investor implications."
        text = await self._call_llm(SYS, prompt)
        return SpecialistOutput(specialist_type=SpecialistType.NEWS_ANALYST, analysis_text=text, confidence_score=0.79, key_findings=self._extract_findings(text), data_sources=["FT", "Reuters", "Bloomberg News"], processing_time_seconds=round(time.time()-start, 2))
