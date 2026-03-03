import time
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

SYS = """You are a Chief Risk Officer. Assess risk across: regulatory, operational, financial, cyber, reputational, strategic. Use probability×impact matrix. End with 4 bullet risk findings starting with '- '."""

MOCK_RISKS = {"cyber": "Medium/High", "regulatory": "Medium/High", "currency": "High/Medium", "key_person": "Medium/Medium", "data_privacy": "Medium/High"}


class RiskAssessor(BaseSpecialist):
    specialist_type = SpecialistType.RISK_ASSESSOR

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        start = time.time()
        risks = context.get("risk_data", MOCK_RISKS)
        risk_text = "\n".join(f"- {k.replace('_',' ').title()}: Prob/Impact={v}" for k, v in risks.items())
        prompt = f"Company: {topic}\n\nRisk Registry:\n{risk_text}\n\nConduct comprehensive risk assessment with probability-impact scoring and mitigation recommendations."
        text = await self._call_llm(SYS, prompt)
        return SpecialistOutput(specialist_type=SpecialistType.RISK_ASSESSOR, analysis_text=text, confidence_score=0.85, key_findings=self._extract_findings(text), data_sources=["Enterprise Risk Register", "Audit Reports", "Regulatory Filings"], processing_time_seconds=round(time.time()-start, 2))
