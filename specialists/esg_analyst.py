import time
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

SYS = """You are an ESG analyst. Score E/S/G individually (0-100) and composite. Assess Scope 1/2/3 emissions, diversity, governance quality. End with 4 bullet ESG findings starting with '- '."""

MOCK_ESG = {"e_score": 71, "s_score": 68, "g_score": 79, "scope1": "12,450 tCO2e", "scope2": "8,230 tCO2e", "renewable": "67%", "gender_leadership": "38%", "board_independence": "73%", "net_zero": "2040"}


class ESGAnalyst(BaseSpecialist):
    specialist_type = SpecialistType.ESG_ANALYST

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        start = time.time()
        d = context.get("esg_data", MOCK_ESG)
        composite = round((d["e_score"] + d["s_score"] + d["g_score"]) / 3, 1)
        prompt = f"Company: {topic}\nE Score: {d['e_score']}/100, S Score: {d['s_score']}/100, G Score: {d['g_score']}/100, Composite: {composite}/100\nScope 1: {d['scope1']}, Scope 2: {d['scope2']}, Renewables: {d['renewable']}, Gender in Leadership: {d['gender_leadership']}, Board Independence: {d['board_independence']}, Net Zero: {d['net_zero']}\n\nProvide detailed ESG analysis with peer benchmarking."
        text = await self._call_llm(SYS, prompt)
        return SpecialistOutput(specialist_type=SpecialistType.ESG_ANALYST, analysis_text=text, confidence_score=0.81, key_findings=self._extract_findings(text), data_sources=["MSCI ESG", "Sustainalytics", "CDP", "Company Sustainability Report"], processing_time_seconds=round(time.time()-start, 2))
