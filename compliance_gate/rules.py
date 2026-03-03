"""FCA compliance rules as structured dicts for programmatic access."""

FCA_RULES = [
    {
        "rule_id": "FCA-001",
        "description": "No guaranteed returns language",
        "detail": "Block phrases like 'guaranteed', 'certain return', 'risk-free'",
        "severity": "critical",
    },
    {
        "rule_id": "FCA-002",
        "description": "Past performance disclaimer required",
        "detail": "All historical performance must note it does not predict future results",
        "severity": "high",
    },
    {
        "rule_id": "FCA-003",
        "description": "Clear, fair, not misleading",
        "detail": "No cherry-picked statistics; balanced presentation required",
        "severity": "high",
    },
    {
        "rule_id": "FCA-004",
        "description": "Risk warnings with recommendations",
        "detail": "All investment recommendations need risk disclosures",
        "severity": "high",
    },
    {
        "rule_id": "FCA-005",
        "description": "No promotional language masquerading as research",
        "detail": "Objective tone required throughout",
        "severity": "medium",
    },
]

REQUIRED_DISCLAIMERS = [
    "This report is for informational purposes only and does not constitute investment advice.",
    "Past performance is not indicative of future results. Investment values may fall as well as rise.",
    "For professional investors and qualified counterparties only. Not suitable for retail investors.",
    "Contoso Research Limited is authorised and regulated by the FCA (FRN: 123456).",
]
