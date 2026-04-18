# Financial Research System

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

Multi-agent financial research platform with specialist analysts (market, financial, ESG, risk, news), compliance gating, and synthesized report generation — powered by Azure OpenAI, Service Bus orchestration, and Cosmos DB.

## Architecture

```
Research Request
        │
        ▼
┌───────────────────────────────────────────┐
│  FastAPI Service (:8000)                  │
│                                           │
│  ResearchPipeline (orchestrator)          │
│       │                                   │
│       ├──► MarketResearcher              │──► Market trends & positioning
│       ├──► FinancialAnalyst              │──► Financial metrics & ratios
│       ├──► ESGAnalyst                    │──► ESG scoring & sustainability
│       ├──► RiskAssessor                  │──► Risk factor identification
│       └──► NewsAnalyst                   │──► News sentiment & events
│       │                                   │
│       ▼                                   │
│  ComplianceGate ──► Rule validation      │──► Fact-checking & bias detection
│       │                                   │
│       ▼                                   │
│  Synthesiser ──► GPT-4o                  │──► Final consolidated report
└───────────────────────────────────────────┘
        │
        ▼
Cosmos DB (report storage) + Service Bus (async orchestration)
```

## Key Features

- **5 Specialist Agents** — Market researcher, financial analyst, ESG analyst, risk assessor, and news analyst run in parallel
- **Compliance Gate** — Rule-based validation checks for factual consistency, bias detection, and data quality
- **Report Synthesis** — GPT-4o consolidates specialist outputs into executive-ready research reports
- **Service Bus Orchestration** — Azure Service Bus enables async pipeline execution for long-running research
- **Cosmos DB Persistence** — Research reports and pipeline state stored in Cosmos DB
- **Extensible Specialist Pattern** — `BaseSpecialist` ABC for adding new domain analysts
- **LOCAL_MODE** — Full pipeline runs locally without Azure dependencies

## Step-by-Step Flow

### Step 1: Research Request
Client submits a `ResearchRequest` with company/topic, research_type, and scope parameters via `POST /research`.

### Step 2: Specialist Analysis (Parallel)
`ResearchPipeline` dispatches the request to all 5 specialists simultaneously. Each specialist generates a domain-specific analysis using GPT-4o.

### Step 3: Compliance Gate
`ComplianceGate` validates all specialist outputs against rules in `rules.py`: checks for unsupported claims, conflicting data, and bias indicators.

### Step 4: Report Synthesis
`Synthesiser` receives all validated specialist outputs and generates a consolidated `FinalReport` with executive summary, key findings, risk factors, and recommendations.

### Step 5: Persistence
Final report is stored in Cosmos DB with metadata (pipeline_id, timestamp, specialist_scores).

## Repository Structure

```
financial-research-system/
├── orchestrator/
│   ├── main.py                  # FastAPI app entry point
│   ├── pipeline.py              # ResearchPipeline — multi-agent orchestration
│   └── service_bus_orchestrator.py  # Async Service Bus pipeline
├── specialists/
│   ├── base_specialist.py       # BaseSpecialist ABC
│   ├── market_researcher.py     # Market trends analysis
│   ├── financial_analyst.py     # Financial metrics & ratios
│   ├── esg_analyst.py           # ESG scoring
│   ├── risk_assessor.py         # Risk factor identification
│   └── news_analyst.py          # News sentiment analysis
├── compliance_gate/
│   ├── agent.py                 # Compliance validation agent
│   └── rules.py                 # Validation rule definitions
├── synthesiser/
│   └── agent.py                 # Report synthesis agent
├── shared/
│   ├── config.py                # Environment settings
│   ├── models.py                # ResearchRequest, FinalReport, etc.
│   ├── service_bus.py           # Azure Service Bus client
│   └── logging_config.py        # Structured logging
├── tests/
│   ├── test_specialists.py
│   └── test_pipeline_e2e.py
├── infra/
│   ├── Dockerfile
│   └── docker-compose.yml
├── demo_e2e.py
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
git clone https://github.com/maneeshkumar52/financial-research-system.git
cd financial-research-system
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Set LOCAL_MODE=true for local testing
uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | Model deployment (gpt-4o) |
| `LOCAL_MODE` | No | Run without Azure (default: true) |
| `COSMOS_ENDPOINT` | No | Cosmos DB for report storage |
| `SERVICE_BUS_CONNECTION_STRING` | No | Azure Service Bus for async |

## Testing

```bash
pytest -q
python demo_e2e.py
```

## License

MIT
