"""Tests for specialist agents."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from shared.models import SpecialistType


@pytest.mark.asyncio
async def test_financial_analyst_output():
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = "Strong financial performance.\n- Revenue grew 7.2% YoY indicating solid top-line growth\n- Operating margin of 18.7% demonstrates operational efficiency\n- P/E of 21.4x reflects modest premium to sector average"
    mock_resp.usage.total_tokens = 200
    with patch("openai.AsyncAzureOpenAI") as mock_oai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
        mock_oai.return_value = mock_client
        from specialists.financial_analyst import FinancialAnalyst
        a = FinancialAnalyst()
        a.client = mock_client
        result = await a.analyse("Test Corp", {})
        assert result.specialist_type == SpecialistType.FINANCIAL_ANALYST
        assert len(result.analysis_text) > 10
        assert 0.0 <= result.confidence_score <= 1.0
        assert len(result.key_findings) > 0


@pytest.mark.asyncio
async def test_esg_analyst_output():
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = "Good ESG performance.\n- E score 71 reflects solid decarbonisation progress\n- S score 68 shows room for diversity improvement\n- G score 79 demonstrates best-in-class governance"
    mock_resp.usage.total_tokens = 180
    with patch("openai.AsyncAzureOpenAI") as mock_oai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
        mock_oai.return_value = mock_client
        from specialists.esg_analyst import ESGAnalyst
        a = ESGAnalyst()
        a.client = mock_client
        result = await a.analyse("Test Corp", {})
        assert result.specialist_type == SpecialistType.ESG_ANALYST
        assert result.confidence_score > 0


@pytest.mark.asyncio
async def test_risk_assessor_output():
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = "Moderate risk profile.\n- Cyber risk is highest priority requiring immediate attention\n- Currency exposure partially mitigated by hedging strategy\n- Regulatory risk elevated due to ongoing data review"
    mock_resp.usage.total_tokens = 190
    with patch("openai.AsyncAzureOpenAI") as mock_oai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
        mock_oai.return_value = mock_client
        from specialists.risk_assessor import RiskAssessor
        a = RiskAssessor()
        a.client = mock_client
        result = await a.analyse("Test Corp", {})
        assert result.specialist_type == SpecialistType.RISK_ASSESSOR
        assert len(result.key_findings) > 0
