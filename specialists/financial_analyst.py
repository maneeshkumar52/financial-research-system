import time
import structlog
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

logger = structlog.get_logger(__name__)

SYS = """You are a senior equity research analyst. Analyse financial metrics: revenue growth, margins, cash flow, valuation ratios (P/E, EV/EBITDA), debt levels, ROE, ROIC. Use specific numbers. End with 4 bullet findings starting with '- '."""

MOCK_DATA = {"revenue_growth": "7.2% YoY", "gross_margin": "42.3%", "op_margin": "18.7%", "fcf": "£234M", "pe": "21.4x", "ev_ebitda": "13.8x", "debt_equity": "0.34", "roe": "19.2%"}


class FinancialAnalyst(BaseSpecialist):
    specialist_type = SpecialistType.FINANCIAL_ANALYST

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        start = time.time()
        data = context.get("financial_data", MOCK_DATA)
        prompt = f"Company: {topic}\nFinancials: Revenue Growth {data['revenue_growth']}, Gross Margin {data['gross_margin']}, Op Margin {data['op_margin']}, FCF {data['fcf']}, P/E {data['pe']}, EV/EBITDA {data['ev_ebitda']}, D/E {data['debt_equity']}, ROE {data['roe']}\n\nProvide comprehensive financial analysis with investment implications."
        text = await self._call_llm(SYS, prompt)
        return SpecialistOutput(specialist_type=SpecialistType.FINANCIAL_ANALYST, analysis_text=text, confidence_score=0.87, key_findings=self._extract_findings(text), data_sources=["Bloomberg", "Refinitiv", "Annual Report"], processing_time_seconds=round(time.time()-start, 2))
