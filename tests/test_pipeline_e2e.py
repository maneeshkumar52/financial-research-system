"""End-to-end pipeline test in LOCAL_MODE."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from shared.models import ResearchRequest


@pytest.mark.asyncio
async def test_full_pipeline_local_mode():
    """Test pipeline runs end-to-end in LOCAL_MODE."""
    request = ResearchRequest(topic="Q4 2024 Analysis", company_name="Test Corp plc")

    specialist_resp = MagicMock()
    specialist_resp.choices[0].message.content = "Strong performance.\n- Revenue grew 7% YoY\n- Good margins\n- Solid ESG score"
    specialist_resp.usage.total_tokens = 200

    synth_resp = MagicMock()
    synth_resp.choices[0].message.content = '{"executive_summary":"Test Corp demonstrates strong fundamentals across all domains.","key_findings":["Revenue growth 7%","Strong margins","Good ESG","Low debt","Positive sentiment"],"risk_factors":["Regulatory risk","Cyber risk","FX exposure"],"recommendations":["Maintain overweight","Monitor regulatory","Increase renewables target"]}'
    synth_resp.usage.total_tokens = 300

    compliance_resp = MagicMock()
    compliance_resp.choices[0].message.content = '{"approved":true,"issues":[],"risk_rating":"low","review_notes":"Meets FCA standards"}'
    compliance_resp.usage.total_tokens = 100

    side_effects = [specialist_resp] * 10 + [synth_resp, compliance_resp]

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=side_effects)

    mock_oai_class = MagicMock(return_value=mock_client)

    with patch("openai.AsyncAzureOpenAI", mock_oai_class), \
         patch("specialists.base_specialist.AsyncAzureOpenAI", mock_oai_class):

        from orchestrator.pipeline import ResearchPipeline
        pipeline = ResearchPipeline()
        # Replace each specialist's client directly so the mock is used
        for sp in pipeline.specialists.values():
            sp.client = mock_client

        report = await pipeline.run(request)

        assert report is not None
        assert report.run_id == request.run_id
        assert report.company_name == "Test Corp plc"
        assert report.synthesis is not None
        assert report.compliance is not None
        # total_pipeline_time may be 0.0 in fast mocked tests, so just check it's non-negative
        assert report.total_pipeline_time >= 0
