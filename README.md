# Financial Research System

**Project 4, Chapter 20 of "Prompt to Production" by Maneesh Kumar**

A Multi-Agent Financial Research System that orchestrates five specialist AI agents in parallel to produce investment-grade research reports with built-in FCA compliance gating.

---

## Architecture

```
                        ResearchRequest
                              |
                    [Orchestrator / Pipeline]
                              |
              ┌───────────────┼───────────────────┐
              |               |                   |
     [Fan-out via asyncio.gather — LOCAL_MODE]     |
              |               |                   |
   ┌──────────┴───┐  ┌────────┴──────┐  ┌─────────┴───────┐
   | Financial    |  | Market        |  | News            |
   | Analyst      |  | Researcher    |  | Analyst         |
   └──────────────┘  └───────────────┘  └─────────────────┘
              |               |                   |
   ┌──────────┴───┐  ┌────────┴──────┐
   | Risk         |  | ESG           |
   | Assessor     |  | Analyst       |
   └──────────────┘  └───────────────┘
              |               |
              └───────────────┘
                      |
              [Synthesiser Agent]
              (Chief Strategy Officer LLM)
                      |
             [Compliance Gate]
             (FCA Review Agent)
                      |
               [Final Report]
```

---

## LOCAL_MODE

By default `LOCAL_MODE=true`. This means all five specialist agents run **in-process** using `asyncio.gather` — no Azure Service Bus is required. Perfect for local development, testing, and CI pipelines.

Set `LOCAL_MODE=false` to switch to Service Bus-based fan-out where each specialist runs as a separate microservice.

---

## The Five Specialists

| Specialist | Role | Key Metrics |
|---|---|---|
| **Financial Analyst** | Equity research, valuations | P/E, EV/EBITDA, FCF, ROE, margins |
| **Market Researcher** | TAM/SAM, competitive landscape | Market share, CAGR, NPS, retention |
| **News Analyst** | Sentiment analysis, event tracking | Sentiment score (-1 to +1), key events |
| **Risk Assessor** | Enterprise risk, probability-impact | Cyber, regulatory, FX, key-person risk |
| **ESG Analyst** | Environmental, Social, Governance | E/S/G scores, Scope 1/2/3, net-zero targets |

---

## Quick Start — Local Development

### 1. Install dependencies

```bash
cd financial-research-system
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

Required variables:
```
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
LOCAL_MODE=true
```

### 3. Start the API server

```bash
uvicorn orchestrator.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

---

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy", "service": "financial-research-system", "version": "1.0.0"}
```

### Start Research

```bash
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Q4 2024 Financial Analysis",
    "company_name": "Acme Technologies plc",
    "date_range": "last 12 months",
    "requested_by": "portfolio-team"
  }'
```

### Sample Response

```json
{
  "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "completed",
  "report": {
    "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "topic": "Q4 2024 Financial Analysis",
    "company_name": "Acme Technologies plc",
    "synthesis": {
      "executive_summary": "Acme Technologies demonstrates strong fundamentals...",
      "key_findings": [
        "Revenue grew 7.2% YoY, beating sector average of 4.1%",
        "Market share expanded to 23.4% in a £8.2B TAM",
        "News sentiment positive at +0.36, driven by Q3 beat and AI investment",
        "Composite ESG score of 72.7 places company in top quartile",
        "Cyber and regulatory risks remain elevated requiring active monitoring"
      ],
      "risk_factors": [
        "Regulatory review of data practices could result in operational changes",
        "Key-person risk following CFO departure",
        "Currency exposure in international revenues"
      ],
      "recommendations": [
        "Maintain overweight position — strong fundamentals justify premium",
        "Monitor regulatory developments quarterly",
        "Engage with management on Scope 3 emissions roadmap",
        "Review hedging strategy for GBP/USD exposure"
      ],
      "total_specialist_time": 12.4
    },
    "compliance": {
      "approved": true,
      "issues": [],
      "required_disclaimers": [
        "This report is for informational purposes only and does not constitute investment advice.",
        "Past performance is not indicative of future results. Investment values may fall as well as rise.",
        "For professional investors and qualified counterparties only. Not suitable for retail investors.",
        "Contoso Research Limited is authorised and regulated by the FCA (FRN: 123456)."
      ],
      "risk_rating": "low"
    },
    "total_pipeline_time": 14.2,
    "status": "completed"
  }
}
```

### Retrieve a Report

```bash
curl http://localhost:8000/api/v1/report/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

### Check Status

```bash
curl http://localhost:8000/api/v1/status/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

---

## Docker

### Build and run with Docker Compose

```bash
cd financial-research-system
docker-compose -f infra/docker-compose.yml up --build
```

### Build image directly

```bash
docker build -f infra/Dockerfile -t financial-research-system:latest .
docker run -p 8000:8000 --env-file .env financial-research-system:latest
```

---

## Running Tests

```bash
# From the project root
pytest tests/ -v

# With coverage
pip install pytest-cov
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## Project Structure

```
financial-research-system/
├── shared/               # Config, models, logging, service bus helper
├── specialists/          # Five specialist agent implementations
├── synthesiser/          # Synthesis agent (Chief Strategy Officer)
├── compliance_gate/      # FCA compliance review agent
├── orchestrator/         # Pipeline, FastAPI app, Service Bus orchestrator
├── tests/                # Unit and E2E tests
├── infra/                # Dockerfile and docker-compose
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
└── pyproject.toml        # Pytest configuration
```

---

## Book Reference

This project is **Project 4** from **Chapter 20** of:

> **Prompt to Production** by Maneesh Kumar
>
> *Building Production-Grade Agentic AI Systems with Azure OpenAI*

The chapter demonstrates multi-agent fan-out patterns, specialist decomposition, synthesis pipelines, and compliance gating — all running locally without cloud infrastructure using `LOCAL_MODE=true`.

---

## Key Design Patterns

- **Fan-out / Gather**: All specialists run concurrently with `asyncio.gather`, reducing latency from ~60s serial to ~12s parallel
- **Specialist Decomposition**: Each domain expert has a focused system prompt and mock data, making testing easy
- **Graceful Degradation**: Individual specialist failures do not abort the pipeline; partial results flow through
- **Compliance Gating**: Every report passes through an FCA-aware LLM reviewer before delivery
- **Local-first Design**: `LOCAL_MODE=true` runs everything in-process; flip to `false` for distributed Service Bus mode
