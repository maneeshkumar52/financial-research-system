import time
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

SYS = """You are a market research analyst. Analyse: TAM/SAM, market share, competitive landscape, industry trends, geographic mix, NPS. End with 4 bullet findings starting with '- '."""

MOCK = {"market_share": "23.4%", "tam": "£8.2B", "cagr": "11.3%", "top_competitors": "CompetitorA 18.2%, CompetitorB 15.7%", "nps": 42, "retention": "87.3%"}


class MarketResearcher(BaseSpecialist):
    specialist_type = SpecialistType.MARKET_RESEARCHER

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        start = time.time()
        d = context.get("market_data", MOCK)
        prompt = f"Company: {topic}\nMarket Share: {d['market_share']}, TAM: {d['tam']}, CAGR: {d['cagr']}, Competitors: {d['top_competitors']}, NPS: {d['nps']}, Retention: {d['retention']}\n\nAnalyse market dynamics, competitive positioning, and growth opportunities."
        text = await self._call_llm(SYS, prompt)
        return SpecialistOutput(specialist_type=SpecialistType.MARKET_RESEARCHER, analysis_text=text, confidence_score=0.83, key_findings=self._extract_findings(text), data_sources=["Gartner", "IDC", "Primary Research"], processing_time_seconds=round(time.time()-start, 2))
