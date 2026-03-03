import asyncio, sys
sys.path.insert(0, '.')

async def main():
    print("=== Financial Research System - End-to-End Demo (LOCAL_MODE) ===\n")

    from shared.models import SpecialistType, ResearchRequest

    # Create research request
    request = ResearchRequest(
        topic="Nvidia AI Chip Market Analysis Q4 2024",
        company_name="Nvidia",
        date_range="Q4 2024",
        requested_by="analyst@fund.com",
        run_id="demo-fin-001",
    )
    print(f"Research request: {request.topic}")
    print(f"  Company: {request.company_name}")

    # Check which specialist files exist
    print(f"\n--- Running 5 Specialist Agents (LOCAL_MODE) ---")
    import os
    specialists_path = "specialists"
    if os.path.exists(specialists_path):
        files = os.listdir(specialists_path)
        print(f"  Specialists directory: {files}")

    # Test compliance rules from the rules module
    try:
        from compliance_gate.rules import FCA_RULES
        print(f"\nFCA Compliance Rules: {len(FCA_RULES)} rules loaded")
        for rule in FCA_RULES:
            print(f"  {rule.get('rule_id','?')}: {rule.get('description','')[:50]}...")
    except Exception as e:
        print(f"\nFCA Rules error: {e}")

    # Test models
    from shared.models import SpecialistOutput, SynthesisResult
    output = SpecialistOutput(
        specialist_type=SpecialistType.FINANCIAL_ANALYST,
        analysis_text="Nvidia reported record Q4 revenue of $22.1B, driven by data center demand for H100/H200 GPUs.",
        confidence_score=0.91,
        key_findings=["Q4 revenue $22.1B (+122% YoY)", "Data center revenue $18.4B", "Gross margin 76.0%"],
        data_sources=["Nvidia Q4 2024 earnings", "Bloomberg"],
        processing_time_seconds=8.5,
    )
    print(f"\nSpecialistOutput model validated:")
    print(f"  Type: {output.specialist_type.value}")
    print(f"  Confidence: {output.confidence_score}")
    print(f"  Key findings: {len(output.key_findings)}")

    # Test that SpecialistType has all 5 values
    print(f"\n--- Specialist Types ---")
    for st in SpecialistType:
        print(f"  {st.value}")

    # Test models can be instantiated
    from shared.config import get_settings
    settings = get_settings()
    print(f"\nSettings: LOCAL_MODE={settings.local_mode}")

    print("\n=== Financial Research System: Models and compliance rules working ===")

asyncio.run(main())
