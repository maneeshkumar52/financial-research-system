import json
import structlog
from shared.config import get_settings
from shared.models import SpecialistOutput, SynthesisResult

logger = structlog.get_logger(__name__)

SYS = """You are a Chief Strategy Officer synthesising specialist research for institutional investors.
Combine all 5 specialist perspectives into a unified, actionable report.
Identify consensus findings and contradictions. Write in objective, professional language.
Respond ONLY with JSON:
{
  "executive_summary": "<2-3 paragraphs>",
  "key_findings": ["<5 findings>"],
  "risk_factors": ["<3 risks>"],
  "recommendations": ["<4 recommendations>"]
}"""


async def synthesise(specialist_outputs: dict, topic: str, company_name: str) -> SynthesisResult:
    """Synthesise all specialist outputs into a unified research report."""
    settings = get_settings()
    from openai import AsyncAzureOpenAI
    client = AsyncAzureOpenAI(azure_endpoint=settings.azure_openai_endpoint, api_key=settings.azure_openai_api_key, api_version=settings.azure_openai_api_version, max_retries=3)

    total_time = sum(o.processing_time_seconds for o in specialist_outputs.values() if hasattr(o, 'processing_time_seconds'))
    context = ""
    for name, output in specialist_outputs.items():
        if hasattr(output, 'key_findings'):
            context += f"\n=== {name.upper()} ===\nConfidence: {output.confidence_score:.0%}\nFindings:\n" + "\n".join(f"- {f}" for f in output.key_findings) + "\n"

    prompt = f"Research Topic: {topic}\nCompany: {company_name}\n\nSPECIALIST INPUTS:\n{context}\n\nSynthesise into a comprehensive investment-grade report."
    try:
        resp = await client.chat.completions.create(model=settings.azure_openai_deployment, messages=[{"role": "system", "content": SYS}, {"role": "user", "content": prompt}], response_format={"type": "json_object"}, temperature=0.3, max_tokens=1500)
        parsed = json.loads(resp.choices[0].message.content)
        return SynthesisResult(executive_summary=parsed.get("executive_summary", ""), detailed_report=context, key_findings=parsed.get("key_findings", []), risk_factors=parsed.get("risk_factors", []), recommendations=parsed.get("recommendations", []), total_specialist_time=total_time)
    except Exception as exc:
        logger.error("synthesis_failed", error=str(exc))
        all_findings = []
        for o in specialist_outputs.values():
            if hasattr(o, 'key_findings'):
                all_findings.extend(o.key_findings[:2])
        return SynthesisResult(executive_summary=f"Research for {company_name} completed across 5 specialist domains.", detailed_report=context, key_findings=all_findings[:5], risk_factors=["Review individual specialist reports for risk details"], recommendations=["Consult specialist reports for recommendations"], total_specialist_time=total_time)
