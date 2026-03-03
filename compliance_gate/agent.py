import json
import structlog
from shared.config import get_settings
from shared.models import SynthesisResult, ComplianceResult

logger = structlog.get_logger(__name__)

FCA_RULES = [
    "FCA-001: No guaranteed returns language — block phrases like 'guaranteed', 'certain return', 'risk-free'",
    "FCA-002: Past performance disclaimer — all historical performance must note it does not predict future results",
    "FCA-003: Clear, fair, not misleading — no cherry-picked statistics, balanced presentation required",
    "FCA-004: Risk warnings with recommendations — all investment recommendations need risk disclosures",
    "FCA-005: No promotional language masquerading as research — objective tone required",
]

REQUIRED_DISCLAIMERS = [
    "This report is for informational purposes only and does not constitute investment advice.",
    "Past performance is not indicative of future results. Investment values may fall as well as rise.",
    "For professional investors and qualified counterparties only. Not suitable for retail investors.",
    "Contoso Research Limited is authorised and regulated by the FCA (FRN: 123456).",
]

SYS = """You are an FCA compliance officer reviewing research reports. Check against FCA rules. Respond ONLY with JSON:
{"approved": <bool>, "issues": ["<specific issue>"], "risk_rating": "<low|medium|high>", "review_notes": "<summary>"}"""


async def review_compliance(synthesis: SynthesisResult, company_name: str) -> ComplianceResult:
    """Review synthesised report for FCA compliance."""
    settings = get_settings()
    from openai import AsyncAzureOpenAI
    client = AsyncAzureOpenAI(azure_endpoint=settings.azure_openai_endpoint, api_key=settings.azure_openai_api_key, api_version=settings.azure_openai_api_version, max_retries=3)

    report = f"Executive Summary:\n{synthesis.executive_summary}\n\nFindings:\n" + "\n".join(f"- {f}" for f in synthesis.key_findings) + "\n\nRecommendations:\n" + "\n".join(synthesis.recommendations)
    rules = "\n".join(FCA_RULES)
    prompt = f"Company: {company_name}\n\nREPORT:\n{report}\n\nFCA RULES:\n{rules}\n\nReview for compliance. Be specific about any violations found."

    try:
        resp = await client.chat.completions.create(model=settings.azure_openai_deployment, messages=[{"role": "system", "content": SYS}, {"role": "user", "content": prompt}], response_format={"type": "json_object"}, temperature=0.1, max_tokens=800)
        parsed = json.loads(resp.choices[0].message.content)
        logger.info("compliance_review_done", approved=parsed.get("approved"), risk=parsed.get("risk_rating"))
        return ComplianceResult(approved=parsed.get("approved", True), issues=parsed.get("issues", []), required_disclaimers=REQUIRED_DISCLAIMERS, risk_rating=parsed.get("risk_rating", "medium"))
    except Exception as exc:
        logger.error("compliance_failed", error=str(exc))
        return ComplianceResult(approved=False, issues=[f"Review failed: {str(exc)}"], required_disclaimers=REQUIRED_DISCLAIMERS, risk_rating="high")
