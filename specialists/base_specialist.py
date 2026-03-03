import time
from abc import ABC, abstractmethod
from typing import List
import structlog
from openai import AsyncAzureOpenAI
from shared.config import get_settings
from shared.models import SpecialistOutput, SpecialistType

logger = structlog.get_logger(__name__)


class BaseSpecialist(ABC):
    """Abstract base class for all specialist agents."""
    specialist_type: SpecialistType = None

    def __init__(self) -> None:
        s = get_settings()
        self.client = AsyncAzureOpenAI(
            azure_endpoint=s.azure_openai_endpoint,
            api_key=s.azure_openai_api_key,
            api_version=s.azure_openai_api_version,
            max_retries=3,
        )
        self.settings = s
        self._total_tokens = 0

    @abstractmethod
    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        ...

    async def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        resp = await self.client.chat.completions.create(
            model=self.settings.azure_openai_deployment,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=temperature,
            max_tokens=1200,
        )
        if resp.usage:
            self._total_tokens += resp.usage.total_tokens
        return resp.choices[0].message.content or ""

    def _extract_findings(self, text: str, max_findings: int = 5) -> List[str]:
        findings = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith(("- ", "• ", "* ")):
                f = line.lstrip("-•* ").strip()
                if len(f) > 10:
                    findings.append(f)
            elif line and line[0].isdigit() and len(line) > 3 and line[1] in ".)":
                f = line[2:].strip()
                if f:
                    findings.append(f)
            if len(findings) >= max_findings:
                break
        return findings or ["Analysis completed — see detailed report for key findings."]
