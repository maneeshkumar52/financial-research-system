<div align="center">

# Financial Research System

### Multi-Agent Investment Research Pipeline with FCA Compliance Gate

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-GPT--4o-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![Azure Service Bus](https://img.shields.io/badge/Azure_Service_Bus-7.12-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/service-bus)
[![Azure Cosmos DB](https://img.shields.io/badge/Cosmos_DB-4.7-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/cosmos-db)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*An enterprise-grade multi-agent financial research platform that runs 5 domain-specialist agents in parallel, synthesises their findings into investment-grade reports, and validates output against FCA regulatory compliance rules — mirroring the actual workflow of an equity research team at a financial institution.*

[Architecture](#architecture) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [Specialist Agents](#specialist-agents) · [Compliance Gate](#compliance-gate) · [Deployment](#deployment)

</div>

---

## Why This Exists

Financial research at institutional scale requires multiple domain experts analysing a company simultaneously — equity analysts reviewing financial metrics, market researchers assessing competitive positioning, ESG analysts scoring sustainability, risk officers mapping threat matrices, and news analysts gauging sentiment. Their findings must then be synthesised into a coherent report and validated against regulatory requirements before distribution.

This system automates that entire workflow as a **multi-agent pipeline** — not a generic RAG or chatbot, but a structured research production system with:

- **5 specialist agents** running concurrently via `asyncio.gather` with 120-second timeouts
- **A synthesiser agent** (Chief Strategy Officer persona) that resolves contradictions across specialist findings
- **An FCA compliance gate** enforcing 5 regulatory rules and 4 mandatory disclaimers
- **Dual execution modes**: in-process (LOCAL) or Azure Service Bus distributed (REMOTE)
- **Structured JSON output** from GPT-4o ensuring machine-parseable, integration-ready reports

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Server (:8000)                               │
│                                                                             │
│  POST /api/v1/research                                                      │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              ResearchPipeline.run(request)                          │    │
│  │                                                                     │    │
│  │  ╔═══════════════════════════════════════════════════════════════╗  │    │
│  │  ║  PHASE 1: Fan-Out  (asyncio.gather, 120s timeout each)      ║  │    │
│  │  ║                                                               ║  │    │
│  │  ║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         ║  │    │
│  │  ║  │  Financial   │ │   Market     │ │     ESG      │         ║  │    │
│  │  ║  │  Analyst     │ │  Researcher  │ │   Analyst    │         ║  │    │
│  │  ║  │  (GPT-4o)    │ │  (GPT-4o)    │ │  (GPT-4o)    │         ║  │    │
│  │  ║  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘         ║  │    │
│  │  ║         │                │                │                  ║  │    │
│  │  ║  ┌──────────────┐ ┌──────────────┐                          ║  │    │
│  │  ║  │    Risk      │ │    News      │                          ║  │    │
│  │  ║  │  Assessor    │ │   Analyst    │                          ║  │    │
│  │  ║  │  (GPT-4o)    │ │  (GPT-4o)    │                          ║  │    │
│  │  ║  └──────┬───────┘ └──────┬───────┘                          ║  │    │
│  │  ╚═════════╪════════════════╪══════════════════════════════════╝  │    │
│  │            │                │                                     │    │
│  │            ▼                ▼                                     │    │
│  │  ╔═══════════════════════════════════════════════════════════╗    │    │
│  │  ║  PHASE 2: Synthesis  (Chief Strategy Officer persona)    ║    │    │
│  │  ║  • Consolidates 5 specialist perspectives                ║    │    │
│  │  ║  • Resolves contradictions, identifies consensus         ║    │    │
│  │  ║  • Produces executive summary + findings + risks         ║    │    │
│  │  ╚═════════════════════════════╤═════════════════════════════╝    │    │
│  │                                │                                  │    │
│  │  ╔═════════════════════════════╧═════════════════════════════╗    │    │
│  │  ║  PHASE 3: Compliance Gate  (FCA Compliance Officer)      ║    │    │
│  │  ║  • 5 FCA rules (no guaranteed returns, disclaimers, etc) ║    │    │
│  │  ║  • 4 mandatory disclaimers                               ║    │    │
│  │  ║  • Risk rating: low | medium | high                      ║    │    │
│  │  ╚═════════════════════════════╤═════════════════════════════╝    │    │
│  │                                │                                  │    │
│  │  ╔═════════════════════════════╧═════════════════════════════╗    │    │
│  │  ║  PHASE 4: Persistence  (Cosmos DB or in-memory)          ║    │    │
│  │  ╚═════════════════════════════════════════════════════════════╝    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                     │
│       ▼                                                                     │
│  FinalReport (JSON) → Client                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why Not RAG?

| Aspect | Generic RAG | This System |
|--------|-------------|-------------|
| **Knowledge source** | Vector database / document chunks | Structured financial data (metrics, ratios, ESG scores, news feeds, risk registers) |
| **Architecture** | Single retriever → single generator | 5 parallel specialists → synthesiser → compliance gate (7 LLM agents) |
| **Output** | Free-text answer | Structured JSON: executive summary, key findings, risk factors, recommendations |
| **Quality gate** | None | FCA regulatory compliance with 5 rules + 4 mandatory disclaimers |
| **Agent roles** | Single "assistant" | Domain-specific personas: Senior Equity Analyst, Market Research Analyst, ESG Analyst, Chief Risk Officer, News Analyst, Chief Strategy Officer, FCA Compliance Officer |
| **Error handling** | Crash on failure | Graceful degradation — pipeline continues if any specialist fails |
| **Confidence** | None | Per-specialist confidence scores (0.0–1.0) with source attribution |
| **Scalability** | In-process only | Azure Service Bus async pipeline for distributed workloads |

### Execution Modes

```
┌──────────────────────────────────────────────────────────────┐
│                   LOCAL_MODE=true (Default)                    │
│                                                                │
│  ResearchPipeline                                              │
│       │                                                        │
│       ├──► asyncio.gather(                                     │
│       │      FinancialAnalyst.analyse(),                       │
│       │      MarketResearcher.analyse(),                       │
│       │      ESGAnalyst.analyse(),                             │
│       │      RiskAssessor.analyse(),                           │
│       │      NewsAnalyst.analyse()                             │
│       │    )                                                   │
│       │    ↳ 120s timeout per specialist                       │
│       │    ↳ Failed specialists excluded, pipeline continues   │
│       │                                                        │
│       ├──► synthesise(outputs)                                 │
│       ├──► review_compliance(synthesis)                        │
│       └──► store_report(final_report)                          │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   LOCAL_MODE=false (Remote)                    │
│                                                                │
│  ServiceBusOrchestrator                                        │
│       │                                                        │
│       ├──► publish("financial-analyst", payload)               │
│       ├──► publish("market-researcher", payload)               │
│       ├──► publish("esg-analyst", payload)                     │
│       ├──► publish("risk-assessor", payload)                   │
│       └──► publish("news-analyst", payload)                    │
│            ↳ Each specialist runs as independent worker        │
│            ↳ Results collected via Service Bus queues           │
└──────────────────────────────────────────────────────────────┘
```

---

## Design Decisions

### Why Fan-Out/Fan-In Over Sequential Chains?

| Approach | Latency (5 specialists) | Failure Impact | Implementation |
|----------|------------------------|----------------|----------------|
| **Sequential chain** | 5 × specialist_time | One failure blocks all | Simple but slow |
| **Fan-out/fan-in** ✅ | max(specialist_times) | Graceful degradation | `asyncio.gather` with timeouts |
| **Event-driven** | Variable | Complex error recovery | Requires message broker always |

The fan-out pattern was chosen because specialist analyses are **independent** — a financial analyst's output doesn't depend on the ESG analyst's findings. Running them concurrently reduces total pipeline time from ~25 seconds to ~5 seconds (the slowest specialist's response time).

### Why Structured JSON Output Over Free Text?

```python
# Synthesiser forces JSON structured output from GPT-4o
resp = await self.client.chat.completions.create(
    model=self.settings.azure_openai_deployment,
    messages=messages,
    response_format={"type": "json_object"},  # ← Enforced JSON
    temperature=0.3,
    max_tokens=1500,
)
```

| Output Format | Parseability | Downstream Integration | Consistency |
|---------------|-------------|----------------------|-------------|
| Free text | Regex/heuristic parsing | Brittle | Variable |
| **JSON structured** ✅ | `json.loads()` | Direct API consumption | Enforced schema |
| Function calling | Tool-dependent | OpenAI-specific | Strong |

Both the Synthesiser and Compliance Gate use `response_format={"type": "json_object"}` because research reports must be machine-parseable for downstream systems (portfolio management, risk dashboards, compliance audit trails).

### Why BaseSpecialist ABC Over Simple Functions?

```python
class BaseSpecialist(ABC):
    """Template Method pattern — shared LLM infrastructure, domain-specific analyse()"""

    async def _call_llm(self, system_prompt, user_prompt, temperature=0.3) -> str:
        # Shared: Azure OpenAI client, retry logic, token tracking
        ...

    def _extract_findings(self, text, max_findings=5) -> List[str]:
        # Shared: bullet-point parsing from LLM output
        ...

    @abstractmethod
    async def analyse(self, topic, context) -> SpecialistOutput:
        # Domain-specific: each specialist provides its own prompt + data
        ...
```

| Approach | Code Reuse | Adding New Specialist | Testing |
|----------|-----------|----------------------|---------|
| Standalone functions | None — duplicate LLM setup | Copy-paste entire function | Mock each separately |
| **ABC template method** ✅ | LLM client, retries, extraction shared | Only override `analyse()` | Mock base once |
| Plugin registry | Maximum flexibility | Register callable | Most complex |

The Template Method pattern means adding a 6th specialist (e.g., `TechnicalAnalyst`) requires only ~20 lines — a new class overriding `analyse()` with its domain prompt and mock data.

### Why Dual-Mode Service Bus Abstraction?

```python
class ServiceBusHelper:
    async def publish(self, queue_name, message_dict):
        if not self.connection_string:
            # LOCAL_MODE: in-memory queue for development
            self._local_queues[queue_name].append(message_dict)
            return f"local-{id(message_dict)}"
        # REMOTE: real Azure Service Bus publish
        async with ServiceBusClient.from_connection_string(...) as client:
            ...
```

| Mode | Use Case | Infrastructure Required | Cost |
|------|----------|------------------------|------|
| **LOCAL (in-memory)** | Development, testing, demos | None | Free |
| **REMOTE (Service Bus)** | Production, horizontal scaling | Azure Service Bus namespace | Pay-per-message |

This abstraction allows the same pipeline code to run locally (for development) and in production (for scale) without conditional logic scattered throughout the codebase.

---

## Data Contracts

### Request / Response Models

All models defined in `shared/models.py` using Pydantic v2:

```python
# ── Specialist Type Enum ──────────────────────────────────────────────────
class SpecialistType(str, Enum):
    FINANCIAL_ANALYST  = "financial_analyst"
    MARKET_RESEARCHER  = "market_researcher"
    NEWS_ANALYST       = "news_analyst"
    RISK_ASSESSOR      = "risk_assessor"
    ESG_ANALYST        = "esg_analyst"

# ── Research Request ──────────────────────────────────────────────────────
class ResearchRequest(BaseModel):
    topic: str                                          # "Nvidia AI Chip Market Analysis Q4 2024"
    company_name: str                                   # "Nvidia"
    date_range: str = "last 12 months"                  # Temporal scope
    requested_by: str = "system"                        # Audit trail
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

# ── Specialist Output ─────────────────────────────────────────────────────
class SpecialistOutput(BaseModel):
    specialist_type: SpecialistType                     # Which specialist produced this
    analysis_text: str                                  # Full GPT-4o analysis
    confidence_score: float = Field(ge=0.0, le=1.0)    # 0.0–1.0 confidence
    key_findings: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    processing_time_seconds: float = 0.0

# ── Synthesis Result ──────────────────────────────────────────────────────
class SynthesisResult(BaseModel):
    executive_summary: str                              # 2-3 paragraph executive summary
    detailed_report: str                                # Concatenated specialist context
    key_findings: List[str] = Field(default_factory=list)    # Top 5 findings
    risk_factors: List[str] = Field(default_factory=list)    # Top 3 risks
    recommendations: List[str] = Field(default_factory=list) # Top 4 recommendations
    total_specialist_time: float = 0.0

# ── Compliance Result ─────────────────────────────────────────────────────
class ComplianceResult(BaseModel):
    approved: bool                                      # FCA compliance pass/fail
    issues: List[str] = Field(default_factory=list)     # Specific violations
    required_disclaimers: List[str] = Field(default_factory=list)
    risk_rating: str = "medium"                         # low | medium | high

# ── Final Report ─────────────────────────────────────────────────────────
class FinalReport(BaseModel):
    run_id: str                                         # Pipeline tracking ID
    topic: str                                          # Research topic
    company_name: str                                   # Target company
    synthesis: SynthesisResult                          # Synthesised report
    compliance: ComplianceResult                        # Compliance review
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_pipeline_time: float = 0.0
    status: str = "completed"
```

### Example API Exchange

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Nvidia AI Chip Market Analysis Q4 2024",
    "company_name": "Nvidia",
    "date_range": "last 12 months",
    "requested_by": "portfolio_manager"
  }'
```

**Response:**
```json
{
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "report": {
    "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "topic": "Nvidia AI Chip Market Analysis Q4 2024",
    "company_name": "Nvidia",
    "synthesis": {
      "executive_summary": "Nvidia demonstrates strong financial performance with 7.2% YoY revenue growth...",
      "detailed_report": "=== FINANCIAL_ANALYST === ...",
      "key_findings": [
        "Revenue growth of 7.2% YoY with expanding gross margins at 42.3%",
        "Market share leadership at 23.4% in an £8.2B TAM growing at 11.3% CAGR",
        "ESG composite score of 72.7/100 with net-zero target of 2040",
        "Medium-High cyber and regulatory risk exposure identified",
        "Positive news sentiment at 0.36 driven by record Q3 revenue"
      ],
      "risk_factors": [
        "Regulatory review of data practices could impact operations",
        "Currency exposure rated High probability / Medium impact",
        "Key person dependency following CFO departure"
      ],
      "recommendations": [
        "Maintain overweight position given strong fundamentals and market leadership",
        "Monitor regulatory review outcome — potential downgrade trigger",
        "Assess ESG improvement trajectory for inclusion in sustainable mandates",
        "Hedge currency exposure given High probability rating"
      ],
      "total_specialist_time": 12.45
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
      "risk_rating": "medium"
    },
    "created_at": "2024-11-15T14:30:00.000Z",
    "total_pipeline_time": 5.23,
    "status": "completed"
  }
}
```

---

## Features

| # | Feature | Description | Implementation |
|---|---------|-------------|----------------|
| 1 | **5 Parallel Specialist Agents** | Financial Analyst, Market Researcher, ESG Analyst, Risk Assessor, News Analyst run concurrently | `asyncio.gather` in `ResearchPipeline.run()` |
| 2 | **120s Per-Specialist Timeout** | Prevents runaway LLM calls from blocking the pipeline | `asyncio.wait_for(timeout=120.0)` |
| 3 | **Graceful Degradation** | Pipeline continues even if individual specialists fail | `_run_one()` returns `None` on failure |
| 4 | **FCA Compliance Gate** | 5 regulatory rules validated against every report | `compliance_gate/rules.py` + GPT-4o review |
| 5 | **4 Mandatory Disclaimers** | Automatically appended to compliance output | `REQUIRED_DISCLAIMERS` in `rules.py` |
| 6 | **Synthesis Agent** | Chief Strategy Officer persona consolidates all findings | `synthesiser/agent.py` with JSON structured output |
| 7 | **Structured JSON Output** | GPT-4o forced to return parseable JSON | `response_format={"type": "json_object"}` |
| 8 | **Confidence Scoring** | Each specialist reports 0.0–1.0 confidence with source attribution | `SpecialistOutput.confidence_score` |
| 9 | **Mock Data Per Specialist** | Realistic financial data for offline development | `MOCK_DATA`, `MOCK_ESG`, `MOCK_RISKS`, `MOCK_NEWS` constants |
| 10 | **Dual Execution Mode** | LOCAL (in-process) or REMOTE (Azure Service Bus) | `LOCAL_MODE` env var + `ServiceBusOrchestrator` |
| 11 | **Azure Service Bus Integration** | Per-specialist message queues for distributed execution | `ServiceBusHelper` with publish/subscribe |
| 12 | **In-Memory Queue Fallback** | Service Bus abstraction works locally without Azure | `_local_queues` dict in `ServiceBusHelper` |
| 13 | **Cosmos DB Persistence** | Reports stored with `run_id`-based retrieval | `_store_report()` with async Cosmos client |
| 14 | **In-Memory Store Fallback** | Works without Cosmos DB configured | `_store` dict in `main.py` |
| 15 | **Template Method Pattern** | `BaseSpecialist` ABC shares LLM infrastructure | Subclasses only override `analyse()` |
| 16 | **Structured Logging** | JSON-formatted logs via structlog | `configure_logging()` with ISO timestamps |
| 17 | **Context Variable Logging** | Request-scoped log context | `structlog.contextvars.merge_contextvars` |
| 18 | **Pydantic v2 Models** | 6 typed data models with validation | `shared/models.py` |
| 19 | **Settings Management** | Environment variables with defaults via pydantic-settings | `shared/config.py` with `@lru_cache` singleton |
| 20 | **CORS Middleware** | Cross-origin requests enabled for frontend integration | `CORSMiddleware(allow_origins=["*"])` |
| 21 | **Lifespan Management** | Pipeline initialised once at startup, not per-request | FastAPI `lifespan` context manager |
| 22 | **Health Endpoint** | Liveness/readiness probe for container orchestrators | `GET /health` |
| 23 | **Report Retrieval API** | Fetch completed reports by run_id | `GET /api/v1/report/{run_id}` |
| 24 | **Status Check API** | Query pipeline status for async tracking | `GET /api/v1/status/{run_id}` |
| 25 | **Docker Containerisation** | Production-ready container with Python 3.11 slim | `infra/Dockerfile` |
| 26 | **Docker Compose** | Single-command local deployment | `infra/docker-compose.yml` |
| 27 | **Async Throughout** | Fully async pipeline — FastAPI, OpenAI, Service Bus, Cosmos DB | `async/await` everywhere |
| 28 | **Retry Configuration** | Azure OpenAI client configured with 3 retries | `max_retries=3` in `AsyncAzureOpenAI` |
| 29 | **E2E Pipeline Tests** | Full pipeline tested with mocked LLM responses | `tests/test_pipeline_e2e.py` |
| 30 | **Unit Tests Per Specialist** | Individual specialist output validation | `tests/test_specialists.py` |
| 31 | **Bullet Finding Extraction** | Parses structured findings from free-text LLM output | `_extract_findings()` with multi-format detection |
| 32 | **ESG Composite Scoring** | Automatic E/S/G average calculation | `(e + s + g) / 3` in `ESGAnalyst` |
| 33 | **Risk Registry Formatting** | Probability×Impact matrix text generation | `RiskAssessor` risk text builder |
| 34 | **News Sentiment Averaging** | Aggregate sentiment from multiple news items | `NewsAnalyst` sentiment computation |
| 35 | **Dead Letter Queue Support** | Failed Service Bus messages routed to DLQ | `receiver.dead_letter_message()` in `ServiceBusHelper` |

---

## Prerequisites

<details>
<summary><strong>macOS</strong></summary>

```bash
# Python 3.11+
brew install python@3.11

# Verify
python3.11 --version
# Python 3.11.x

# pip (included with Python 3.11)
pip3 --version

# Docker (optional — for containerised deployment)
brew install --cask docker

# Azure CLI (optional — for Azure resource provisioning)
brew install azure-cli
```

</details>

<details>
<summary><strong>Windows</strong></summary>

```powershell
# Python 3.11+ from python.org
winget install Python.Python.3.11

# Verify
python --version
# Python 3.11.x

# Docker Desktop (optional)
winget install Docker.DockerDesktop

# Azure CLI (optional)
winget install Microsoft.AzureCLI
```

</details>

<details>
<summary><strong>Linux (Ubuntu/Debian)</strong></summary>

```bash
# Python 3.11+
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip

# Verify
python3.11 --version
# Python 3.11.x

# Docker (optional)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Azure CLI (optional)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

</details>

### Required Services

| Service | Required | Purpose | Free Tier |
|---------|----------|---------|-----------|
| **Azure OpenAI** | Yes | GPT-4o for all 7 agent roles | Pay-per-token |
| **Azure Service Bus** | No | Distributed specialist execution (REMOTE mode) | Basic tier available |
| **Azure Cosmos DB** | No | Persistent report storage | 1000 RU/s free |

---

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/maneeshkumar52/financial-research-system.git
cd financial-research-system
```

**Expected output:**
```
Cloning into 'financial-research-system'...
remote: Enumerating objects: 45, done.
remote: Counting objects: 100% (45/45), done.
remote: Compressing objects: 100% (32/32), done.
Receiving objects: 100% (45/45), done.
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows
```

**Expected output:**
```
(.venv) $ python --version
Python 3.11.x
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Collecting fastapi==0.111.0
Collecting uvicorn==0.30.0
Collecting openai==1.40.0
Collecting azure-servicebus==7.12.0
Collecting azure-cosmos==4.7.0
Collecting azure-identity==1.16.0
Collecting pydantic==2.7.0
Collecting pydantic-settings==2.3.0
Collecting structlog==24.2.0
Collecting python-dotenv==1.0.1
Collecting pytest==8.2.0
Collecting pytest-asyncio==0.23.0
Successfully installed fastapi-0.111.0 uvicorn-0.30.0 openai-1.40.0 ...
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT=gpt-4o
SERVICE_BUS_CONNECTION_STRING=
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key
COSMOS_DATABASE=financial-research
LOCAL_MODE=true
LOG_LEVEL=INFO
```

### 5. Start the Server

```bash
uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
{"event": "financial_research_system_starting", "level": "info", "timestamp": "2024-11-15T14:00:00.000Z"}
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
```

### 6. Health Check

```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{"status": "healthy", "service": "financial-research-system", "version": "1.0.0"}
```

### 7. Run a Research Pipeline

```bash
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Nvidia AI Chip Market Analysis Q4 2024",
    "company_name": "Nvidia",
    "date_range": "last 12 months",
    "requested_by": "portfolio_manager"
  }'
```

**Expected output (abbreviated):**
```json
{
  "run_id": "a1b2c3d4-...",
  "status": "completed",
  "report": {
    "topic": "Nvidia AI Chip Market Analysis Q4 2024",
    "company_name": "Nvidia",
    "synthesis": {
      "executive_summary": "Nvidia demonstrates strong financial performance...",
      "key_findings": ["Revenue growth of 7.2% YoY...", ...],
      "risk_factors": ["Regulatory review of data practices...", ...],
      "recommendations": ["Maintain overweight position...", ...]
    },
    "compliance": {
      "approved": true,
      "risk_rating": "medium",
      "required_disclaimers": [...]
    },
    "total_pipeline_time": 5.23
  }
}
```

### 8. Retrieve a Report

```bash
curl http://localhost:8000/api/v1/report/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### 9. Check Pipeline Status

```bash
curl http://localhost:8000/api/v1/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Expected output:**
```json
{"run_id": "a1b2c3d4-...", "status": "completed"}
```

---

## Project Structure

```
financial-research-system/
├── .env.example                          # Environment variable template
├── demo_e2e.py                           # End-to-end demo script
├── pyproject.toml                        # Python project config (pytest settings)
├── requirements.txt                      # Python dependencies (12 packages)
│
├── orchestrator/                         # Pipeline orchestration layer
│   ├── __init__.py
│   ├── main.py                           # FastAPI app, endpoints, lifespan
│   ├── pipeline.py                       # ResearchPipeline — fan-out/fan-in execution
│   └── service_bus_orchestrator.py       # ServiceBusOrchestrator — remote mode dispatch
│
├── specialists/                          # Domain-specialist agents
│   ├── __init__.py
│   ├── base_specialist.py               # BaseSpecialist ABC — shared LLM infrastructure
│   ├── financial_analyst.py             # Senior Equity Research Analyst
│   ├── market_researcher.py             # Market Research Analyst
│   ├── esg_analyst.py                   # ESG Analyst (E/S/G scoring)
│   ├── risk_assessor.py                 # Chief Risk Officer (probability×impact)
│   └── news_analyst.py                  # Financial News Analyst (sentiment)
│
├── compliance_gate/                     # FCA regulatory compliance
│   ├── __init__.py
│   ├── agent.py                         # review_compliance() — GPT-4o FCA review
│   └── rules.py                         # 5 FCA rules + 4 mandatory disclaimers
│
├── synthesiser/                         # Report synthesis
│   ├── __init__.py
│   └── agent.py                         # synthesise() — consolidates specialist outputs
│
├── shared/                              # Shared infrastructure
│   ├── __init__.py
│   ├── models.py                        # 6 Pydantic models (Request, Output, Report, etc.)
│   ├── config.py                        # Settings management (pydantic-settings + lru_cache)
│   ├── service_bus.py                   # ServiceBusHelper — dual-mode message queue
│   └── logging_config.py               # Structured JSON logging (structlog)
│
├── tests/                               # Test suite
│   ├── __init__.py
│   ├── test_specialists.py              # Unit tests for individual specialists
│   └── test_pipeline_e2e.py             # Full pipeline integration test
│
└── infra/                               # Deployment infrastructure
    ├── Dockerfile                        # Python 3.11 slim container
    └── docker-compose.yml               # Single-command local deployment
```

### Module Responsibility Matrix

| Module | Responsibility | Key Classes/Functions | Lines |
|--------|---------------|----------------------|-------|
| `orchestrator/main.py` | FastAPI app, endpoints, lifespan | `lifespan()`, `start_research()`, `get_report()` | 66 |
| `orchestrator/pipeline.py` | Fan-out/fan-in pipeline execution | `ResearchPipeline`, `_run_one()`, `run()` | 97 |
| `orchestrator/service_bus_orchestrator.py` | Remote mode dispatch | `ServiceBusOrchestrator`, `dispatch_all()` | 38 |
| `specialists/base_specialist.py` | Shared LLM infrastructure (ABC) | `BaseSpecialist`, `_call_llm()`, `_extract_findings()` | 55 |
| `specialists/financial_analyst.py` | Equity research analysis | `FinancialAnalyst.analyse()` | 21 |
| `specialists/market_researcher.py` | Market/competitive analysis | `MarketResearcher.analyse()` | 19 |
| `specialists/esg_analyst.py` | ESG scoring (E/S/G composite) | `ESGAnalyst.analyse()` | 22 |
| `specialists/risk_assessor.py` | Risk matrix assessment | `RiskAssessor.analyse()` | 21 |
| `specialists/news_analyst.py` | News sentiment analysis | `NewsAnalyst.analyse()` | 25 |
| `compliance_gate/agent.py` | FCA regulatory review | `review_compliance()` | 51 |
| `compliance_gate/rules.py` | FCA rules + disclaimers | `FCA_RULES`, `REQUIRED_DISCLAIMERS` | 40 |
| `synthesiser/agent.py` | Multi-specialist consolidation | `synthesise()` | 48 |
| `shared/models.py` | Typed data contracts | 6 Pydantic models | 50 |
| `shared/config.py` | Environment configuration | `Settings`, `get_settings()` | 24 |
| `shared/service_bus.py` | Dual-mode message queue | `ServiceBusHelper` | 46 |
| `shared/logging_config.py` | Structured JSON logging | `configure_logging()` | 20 |

---

## Specialist Agents

### Agent Architecture (Template Method Pattern)

```
BaseSpecialist (ABC)
├── _call_llm(system_prompt, user_prompt, temperature=0.3) → str
│   ↳ Azure OpenAI GPT-4o, max_tokens=1200, 3 retries
├── _extract_findings(text, max_findings=5) → List[str]
│   ↳ Parses "- ", "• ", "* ", "1.", "2)" prefixed lines
└── analyse(topic, context) → SpecialistOutput  [ABSTRACT]
    ↳ Each specialist provides domain-specific prompt + data

         ┌─────────────────────┐
         │   BaseSpecialist    │
         │   (ABC)             │
         ├─────────────────────┤
         │ _call_llm()         │
         │ _extract_findings() │
         │ analyse() [abstract]│
         └────────┬────────────┘
                  │
    ┌─────────────┼─────────────┐─────────────┐─────────────┐
    │             │             │             │             │
    ▼             ▼             ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Financial│ │ Market  │ │  ESG    │ │  Risk   │ │  News   │
│Analyst  │ │Researcher│ │ Analyst │ │Assessor │ │ Analyst │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### Specialist Details

| Specialist | Persona | System Prompt Focus | Mock Data | Confidence | Data Sources |
|-----------|---------|-------------------|-----------|------------|-------------|
| **FinancialAnalyst** | Senior Equity Research Analyst | Revenue growth, margins, cash flow, P/E, EV/EBITDA, ROE, ROIC | Revenue 7.2% YoY, margin 42.3%, FCF £234M, P/E 21.4x | 0.87 | Bloomberg, Refinitiv, Annual Report |
| **MarketResearcher** | Market Research Analyst | TAM/SAM, market share, competitors, trends, NPS | Market share 23.4%, TAM £8.2B, CAGR 11.3%, NPS 42 | 0.83 | Gartner, IDC, Primary Research |
| **ESGAnalyst** | ESG Analyst | E/S/G individual + composite scores, Scope 1/2/3, diversity | E:71 S:68 G:79, Scope1 12,450 tCO2e, net-zero 2040 | 0.81 | MSCI ESG, Sustainalytics, CDP |
| **RiskAssessor** | Chief Risk Officer | Regulatory, operational, financial, cyber risk; probability×impact | Cyber Med/High, Regulatory Med/High, Currency High/Med | 0.85 | Risk Register, Audit Reports |
| **NewsAnalyst** | Financial News Analyst | Sentiment (-1.0 to 1.0), key events, regulatory developments | 5 news items, avg sentiment 0.36 | 0.79 | FT, Reuters, Bloomberg News |

### Mock Data Examples

<details>
<summary><strong>Financial Analyst Mock Data</strong></summary>

```python
MOCK_DATA = {
    "revenue_growth": "7.2% YoY",
    "gross_margin": "42.3%",
    "op_margin": "18.7%",
    "fcf": "£234M",
    "pe": "21.4x",
    "ev_ebitda": "13.8x",
    "debt_equity": "0.34",
    "roe": "19.2%"
}
```

</details>

<details>
<summary><strong>ESG Analyst Mock Data</strong></summary>

```python
MOCK_ESG = {
    "e_score": 71,
    "s_score": 68,
    "g_score": 79,
    "scope1": "12,450 tCO2e",
    "scope2": "8,230 tCO2e",
    "renewable": "67%",
    "gender_leadership": "38%",
    "board_independence": "73%",
    "net_zero": "2040"
}
# Composite: (71 + 68 + 79) / 3 = 72.7
```

</details>

<details>
<summary><strong>Risk Assessor Mock Data</strong></summary>

```python
MOCK_RISKS = {
    "cyber": "Medium/High",
    "regulatory": "Medium/High",
    "currency": "High/Medium",
    "key_person": "Medium/Medium",
    "data_privacy": "Medium/High"
}
# Format: Probability/Impact matrix notation
```

</details>

<details>
<summary><strong>News Analyst Mock Data</strong></summary>

```python
MOCK_NEWS = [
    {"date": "2024-11-15", "headline": "Record Q3 revenue, beats consensus by 4%",   "sentiment":  0.8},
    {"date": "2024-11-10", "headline": "CEO announces £150M AI investment over 3y",   "sentiment":  0.7},
    {"date": "2024-10-28", "headline": "Regulatory review of data practices initiated","sentiment": -0.2},
    {"date": "2024-10-15", "headline": "Strategic cloud partnership announced",        "sentiment":  0.6},
    {"date": "2024-09-30", "headline": "CFO departure with succession plan detailed",  "sentiment": -0.1},
]
# Average sentiment: (0.8 + 0.7 - 0.2 + 0.6 - 0.1) / 5 = 0.36
```

</details>

---

## Compliance Gate

### FCA Rules

The compliance gate validates every research report against 5 Financial Conduct Authority rules:

| Rule ID | Description | Severity | Detail |
|---------|-------------|----------|--------|
| **FCA-001** | No guaranteed returns language | Critical | Blocks "guaranteed", "certain return", "risk-free" |
| **FCA-002** | Past performance disclaimer required | High | Historical performance must note it doesn't predict future results |
| **FCA-003** | Clear, fair, not misleading | High | No cherry-picked statistics; balanced presentation required |
| **FCA-004** | Risk warnings with recommendations | High | All investment recommendations need risk disclosures |
| **FCA-005** | No promotional language as research | Medium | Objective tone required throughout |

### Mandatory Disclaimers

Every approved report includes these 4 disclaimers:

```
1. This report is for informational purposes only and does not constitute investment advice.
2. Past performance is not indicative of future results. Investment values may fall as well as rise.
3. For professional investors and qualified counterparties only. Not suitable for retail investors.
4. Contoso Research Limited is authorised and regulated by the FCA (FRN: 123456).
```

### Compliance Review Flow

```
Synthesised Report
       │
       ▼
┌──────────────────────────────────────┐
│  GPT-4o (FCA Compliance Officer)     │
│                                      │
│  Input:                              │
│  • Executive summary                 │
│  • Key findings                      │
│  • Recommendations                   │
│  • FCA rules (5 rules as context)    │
│                                      │
│  Output (JSON structured):           │
│  {                                   │
│    "approved": true/false,           │
│    "issues": [...],                  │
│    "risk_rating": "low|medium|high", │
│    "review_notes": "..."             │
│  }                                   │
└──────────────────────────────────────┘
       │
       ▼
ComplianceResult (Pydantic model)
       │
       ├── approved=true  → Report distributed
       └── approved=false → Report flagged, issues logged
```

---

## API Reference

### Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/health` | Liveness/readiness probe | None |
| `POST` | `/api/v1/research` | Start full research pipeline | None |
| `GET` | `/api/v1/report/{run_id}` | Retrieve completed report | None |
| `GET` | `/api/v1/status/{run_id}` | Check pipeline status | None |

### `POST /api/v1/research`

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | Yes | — | Research topic (e.g., "Nvidia AI Chip Market Analysis Q4 2024") |
| `company_name` | string | Yes | — | Target company name |
| `date_range` | string | No | `"last 12 months"` | Temporal scope for analysis |
| `requested_by` | string | No | `"system"` | Audit trail — who requested the report |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string (UUID) | Pipeline tracking identifier |
| `status` | string | `"completed"` or error status |
| `report` | FinalReport | Full research report with synthesis + compliance |

**Error Responses:**

| Status | Condition | Body |
|--------|-----------|------|
| 500 | All specialists failed | `{"detail": "Pipeline error: All specialist agents failed"}` |
| 500 | Unexpected pipeline error | `{"detail": "Pipeline error: <message>"}` |

### `GET /api/v1/report/{run_id}`

**Response:**

| Status | Condition | Body |
|--------|-----------|------|
| 200 | Report found | `{"report": FinalReport}` |
| 404 | Report not found | `{"detail": "Report not found"}` |

### `GET /api/v1/status/{run_id}`

**Response:**

```json
{"run_id": "...", "status": "completed" | "not_found"}
```

---

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | — | Azure OpenAI resource endpoint URL |
| `AZURE_OPENAI_API_KEY` | Yes | — | Azure OpenAI API key |
| `AZURE_OPENAI_API_VERSION` | No | `2024-02-01` | Azure OpenAI API version |
| `AZURE_OPENAI_DEPLOYMENT` | No | `gpt-4o` | Azure OpenAI model deployment name |
| `SERVICE_BUS_CONNECTION_STRING` | No | — | Azure Service Bus connection string (REMOTE mode) |
| `COSMOS_ENDPOINT` | No | — | Azure Cosmos DB endpoint URL |
| `COSMOS_KEY` | No | `your-cosmos-key` | Azure Cosmos DB key (sentinel value skips storage) |
| `COSMOS_DATABASE` | No | `financial-research` | Cosmos DB database name |
| `LOCAL_MODE` | No | `true` | `true` = in-process execution, `false` = Service Bus dispatch |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Settings Singleton

```python
# shared/config.py
@lru_cache()
def get_settings() -> Settings:
    """Cached singleton — parsed once, reused across all modules."""
    return Settings()
```

All settings are loaded from environment variables (with `.env` file support via `python-dotenv`). The `@lru_cache()` decorator ensures the `.env` file is parsed exactly once.

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

**Expected output:**
```
========================= test session starts =========================
platform darwin -- Python 3.11.x, pytest-8.2.0, pluggy-1.5.0
plugins: asyncio-0.23.0
asyncio: mode=auto
collected 4 items

tests/test_specialists.py::test_financial_analyst_output    PASSED  [ 25%]
tests/test_specialists.py::test_esg_analyst_output          PASSED  [ 50%]
tests/test_specialists.py::test_risk_assessor_output        PASSED  [ 75%]
tests/test_pipeline_e2e.py::test_full_pipeline_local_mode   PASSED  [100%]

========================= 4 passed in 1.23s ===========================
```

### Test Strategy

| Test | Type | What It Tests | Mock Pattern |
|------|------|---------------|-------------|
| `test_financial_analyst_output` | Unit | FinancialAnalyst specialist output shape | `AsyncMock` on OpenAI client |
| `test_esg_analyst_output` | Unit | ESGAnalyst specialist output shape | `AsyncMock` on OpenAI client |
| `test_risk_assessor_output` | Unit | RiskAssessor specialist output shape | `AsyncMock` on OpenAI client |
| `test_full_pipeline_local_mode` | E2E | Full 4-phase pipeline in LOCAL_MODE | 3 mock response types (specialist, synthesis, compliance) |

### E2E Test Flow

```
test_full_pipeline_local_mode()
    │
    ├── Create ResearchRequest("Q4 2024 Analysis", "Test Corp plc")
    │
    ├── Mock 3 response types:
    │   ├── specialist_resp (×10): "Analysis of Test Corp plc..."
    │   ├── synth_resp (×1): {"executive_summary": ..., "key_findings": [...]}
    │   └── compliance_resp (×1): {"approved": true, "issues": [], "risk_rating": "low"}
    │
    ├── Patch AsyncAzureOpenAI → replace each specialist's client
    │
    ├── pipeline.run(request)
    │   ├── Phase 1: 5 specialists run (mocked GPT-4o responses)
    │   ├── Phase 2: Synthesis (mocked JSON response)
    │   ├── Phase 3: Compliance (mocked JSON response)
    │   └── Phase 4: Store (in-memory)
    │
    └── Assert:
        ├── report is not None
        ├── run_id matches request
        ├── company_name == "Test Corp plc"
        ├── synthesis and compliance present
        └── total_pipeline_time >= 0
```

### Run E2E Demo

```bash
python demo_e2e.py
```

This script runs the full pipeline against live Azure OpenAI (requires valid credentials).

---

## Deployment

### Docker

```bash
# Build
cd infra
docker-compose build

# Run (with .env in project root)
docker-compose up
```

**Expected output:**
```
Creating financial-research ... done
Attaching to financial-research
financial-research | {"event": "financial_research_system_starting", ...}
financial-research | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Dockerfile Details

```dockerfile
FROM python:3.11-slim          # Minimal attack surface
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # Layer cache optimisation
COPY . .
EXPOSE 8000
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Decision | Rationale |
|----------|-----------|
| `python:3.11-slim` | 50% smaller than full image, no unnecessary system packages |
| `requirements.txt` copied first | Docker layer caching — dependencies only rebuild when `requirements.txt` changes |
| `--no-cache-dir` | Reduces image size by ~30MB |
| Single `CMD` | One process per container (Docker best practice) |

### Docker Compose

```yaml
version: "3.9"
services:
  financial-research:
    build:
      context: ..
      dockerfile: infra/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ../.env
    environment:
      - LOCAL_MODE=true
```

---

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|---------|
| `openai.AuthenticationError` | Invalid Azure OpenAI key | Verify `AZURE_OPENAI_API_KEY` in `.env` |
| `openai.NotFoundError` | Wrong deployment name | Verify `AZURE_OPENAI_DEPLOYMENT` matches your Azure OpenAI deployment |
| `All specialist agents failed` | All 5 specialists timed out or errored | Check Azure OpenAI endpoint connectivity; increase `SPECIALIST_TIMEOUT` |
| `specialist_timeout` in logs | Single specialist exceeded 120s | GPT-4o latency spike; specialist output still excluded gracefully |
| `compliance_failed` in logs | Compliance GPT-4o call failed | Returns `approved=False, risk_rating="high"` — report flagged but pipeline completes |
| `synthesis_failed` in logs | Synthesis GPT-4o call failed | Falls back to raw specialist findings concatenation |
| `cosmos_skipped_not_configured` | Cosmos DB key is sentinel value | Set real `COSMOS_KEY` or ignore (uses in-memory store) |
| `Connection refused :8000` | Server not running | Run `uvicorn orchestrator.main:app --port 8000` |
| `ModuleNotFoundError` | Dependencies not installed | Run `pip install -r requirements.txt` in active venv |
| `pydantic.ValidationError` | Invalid request body | Check `topic` and `company_name` are non-empty strings |
| Docker build fails | Missing context files | Run `docker-compose build` from `infra/` directory |
| Service Bus connection error | Invalid connection string | Verify `SERVICE_BUS_CONNECTION_STRING` or use `LOCAL_MODE=true` |

---

## Azure Production Mapping

### Resource Mapping

| Component | Azure Service | SKU/Tier | Purpose |
|-----------|--------------|----------|---------|
| **LLM Engine** | Azure OpenAI Service | GPT-4o deployment | All 7 agent roles (5 specialists + synthesiser + compliance) |
| **Message Queue** | Azure Service Bus | Standard | Per-specialist queues for distributed REMOTE mode |
| **Report Storage** | Azure Cosmos DB | Serverless | Persistent report storage with run_id-based retrieval |
| **Container Host** | Azure Container Apps | Consumption | Serverless container hosting for the FastAPI app |
| **Container Registry** | Azure Container Registry | Basic | Docker image storage |
| **Secrets** | Azure Key Vault | Standard | API keys, connection strings |
| **Monitoring** | Azure Monitor + App Insights | — | Structured log ingestion, performance metrics |
| **Identity** | Managed Identity | System-assigned | Passwordless auth to OpenAI, Service Bus, Cosmos DB |

### Service Bus Queue Topology

```
Azure Service Bus Namespace
├── financial-analyst       ← FinancialAnalyst specialist
├── market-researcher       ← MarketResearcher specialist
├── esg-analyst             ← ESGAnalyst specialist
├── risk-assessor           ← RiskAssessor specialist
└── news-analyst            ← NewsAnalyst specialist
    └── $DeadLetterQueue    ← Failed messages (auto-routed)
```

### Cosmos DB Schema

```
Database: financial-research
└── Container: research-reports
    ├── Partition Key: /run_id
    └── Document Structure:
        {
          "id": "<run_id>",
          "run_id": "<uuid>",
          "topic": "...",
          "company_name": "...",
          "synthesis": { ... },
          "compliance": { ... },
          "created_at": "2024-11-15T14:30:00Z",
          "total_pipeline_time": 5.23,
          "status": "completed"
        }
```

### Production Checklist

- [ ] **Azure OpenAI**: Deploy GPT-4o model, note endpoint + deployment name
- [ ] **Service Bus**: Create namespace + 5 queues (financial-analyst, market-researcher, esg-analyst, risk-assessor, news-analyst)
- [ ] **Cosmos DB**: Create account + `financial-research` database + `research-reports` container (partition key: `/run_id`)
- [ ] **Key Vault**: Store `AZURE_OPENAI_API_KEY`, `SERVICE_BUS_CONNECTION_STRING`, `COSMOS_KEY`
- [ ] **Container Apps**: Deploy container with managed identity
- [ ] **Managed Identity**: Grant roles — Cognitive Services OpenAI User, Service Bus Data Sender/Receiver, Cosmos DB Data Contributor
- [ ] **Set `LOCAL_MODE=false`** for Service Bus distributed execution
- [ ] **Set `LOG_LEVEL=INFO`** (or `WARNING` for reduced log volume)
- [ ] **CORS**: Restrict `allow_origins` from `["*"]` to specific frontend domains
- [ ] **Authentication**: Add API key or OAuth middleware to endpoints
- [ ] **Rate Limiting**: Add request throttling for `/api/v1/research`

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.111.0 | Web framework / REST API layer |
| `uvicorn` | 0.30.0 | ASGI server for FastAPI |
| `openai` | 1.40.0 | Azure OpenAI GPT-4o client (async) |
| `azure-servicebus` | 7.12.0 | Azure Service Bus messaging |
| `azure-cosmos` | 4.7.0 | Azure Cosmos DB persistence |
| `azure-identity` | 1.16.0 | Azure authentication / managed identity |
| `pydantic` | 2.7.0 | Data validation / typed models |
| `pydantic-settings` | 2.3.0 | Settings management from environment variables |
| `structlog` | 24.2.0 | Structured JSON logging |
| `python-dotenv` | 1.0.1 | `.env` file loading |
| `pytest` | 8.2.0 | Test framework |
| `pytest-asyncio` | 0.23.0 | Async test support |

---

## Pipeline Observability

### Structured Log Events

All logs are JSON-formatted via structlog with ISO timestamps:

| Event | Phase | Meaning |
|-------|-------|---------|
| `financial_research_system_starting` | Startup | FastAPI lifespan initialising pipeline |
| `financial_research_system_stopping` | Shutdown | Graceful shutdown |
| `pipeline_started` | Phase 1 | Research request received, fan-out beginning |
| `specialist_timeout` | Phase 1 | Individual specialist exceeded 120s — excluded from results |
| `specialist_error` | Phase 1 | Individual specialist threw exception — excluded from results |
| `specialists_complete` | Phase 1 | All specialists finished (success + failures) |
| `synthesis_complete` | Phase 2 | Synthesiser produced consolidated report |
| `synthesis_failed` | Phase 2 | Synthesis GPT-4o call failed — fallback to raw findings |
| `compliance_complete` | Phase 3 | Compliance review finished |
| `compliance_failed` | Phase 3 | Compliance review failed — report flagged as high risk |
| `report_stored` | Phase 4 | Report persisted to Cosmos DB |
| `cosmos_skipped_not_configured` | Phase 4 | Cosmos DB not configured — using in-memory store |
| `store_failed` | Phase 4 | Cosmos DB write failed — report still returned to client |
| `pipeline_complete` | Done | Full pipeline finished — total time logged |
| `local_queue_publish` | Service Bus | Message published to in-memory queue (LOCAL_MODE) |
| `service_bus_publish_failed` | Service Bus | Azure Service Bus publish failed |
| `dispatched_to_all_specialists` | Service Bus | All 5 specialist queues received messages |

### Example Log Output

```json
{
  "event": "pipeline_started",
  "level": "info",
  "timestamp": "2024-11-15T14:30:00.123Z",
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "topic": "Nvidia AI Chip Market Analysis Q4 2024",
  "company_name": "Nvidia"
}
{
  "event": "specialists_complete",
  "level": "info",
  "timestamp": "2024-11-15T14:30:05.456Z",
  "successful": 5,
  "failed": 0,
  "total_time": 5.33
}
{
  "event": "pipeline_complete",
  "level": "info",
  "timestamp": "2024-11-15T14:30:07.789Z",
  "total_pipeline_time": 7.66,
  "compliance_approved": true,
  "risk_rating": "medium"
}
```

---

## Adding a New Specialist

The Template Method pattern makes adding a new specialist straightforward. Here's how to add a `TechnicalAnalyst`:

### 1. Create the Specialist

```python
# specialists/technical_analyst.py
from specialists.base_specialist import BaseSpecialist
from shared.models import SpecialistType, SpecialistOutput

class TechnicalAnalyst(BaseSpecialist):
    specialist_type = SpecialistType.TECHNICAL_ANALYST  # Add to enum first

    SYSTEM_PROMPT = """You are a technical analyst. Analyse price trends, moving averages,
    RSI, MACD, support/resistance levels. End with 4 bullet findings starting with '- '."""

    MOCK_DATA = {
        "50d_ma": "£142.30", "200d_ma": "£128.50",
        "rsi": 62, "macd": "bullish crossover",
        "support": "£135.00", "resistance": "£155.00"
    }

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        prompt = f"Analyse {topic} for {context.get('company_name', 'Unknown')}.\nData: {self.MOCK_DATA}"
        text = await self._call_llm(self.SYSTEM_PROMPT, prompt)
        return SpecialistOutput(
            specialist_type=self.specialist_type,
            analysis_text=text,
            confidence_score=0.82,
            key_findings=self._extract_findings(text),
            data_sources=["TradingView", "Bloomberg Terminal"],
        )
```

### 2. Register in Pipeline

```python
# orchestrator/pipeline.py — add to self.specialists dict
self.specialists[SpecialistType.TECHNICAL_ANALYST] = TechnicalAnalyst()
```

### 3. Add Enum Value

```python
# shared/models.py
class SpecialistType(str, Enum):
    ...
    TECHNICAL_ANALYST = "technical_analyst"
```

That's it — 3 files, ~25 lines of new code. The pipeline automatically includes the new specialist in fan-out execution.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**[⬆ Back to Top](#financial-research-system)**

*Part of [Prompt to Production](https://github.com/maneeshkumar52) — Chapter 20, Project 4*

</div>