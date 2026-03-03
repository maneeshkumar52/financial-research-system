"""Main research pipeline with LOCAL_MODE and Service Bus modes."""
import asyncio
import time
import structlog
from shared.config import get_settings
from shared.models import ResearchRequest, SpecialistType, FinalReport
from specialists.financial_analyst import FinancialAnalyst
from specialists.market_researcher import MarketResearcher
from specialists.news_analyst import NewsAnalyst
from specialists.risk_assessor import RiskAssessor
from specialists.esg_analyst import ESGAnalyst
from synthesiser.agent import synthesise
from compliance_gate.agent import review_compliance

logger = structlog.get_logger(__name__)

SPECIALIST_TIMEOUT = 120.0


class ResearchPipeline:
    """
    Fan-out/gather pipeline:
    1. LOCAL_MODE: all 5 specialists run in-process via asyncio.gather
    2. REMOTE_MODE: specialists dispatch via Service Bus
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.specialists = {
            SpecialistType.FINANCIAL_ANALYST: FinancialAnalyst(),
            SpecialistType.MARKET_RESEARCHER: MarketResearcher(),
            SpecialistType.NEWS_ANALYST: NewsAnalyst(),
            SpecialistType.RISK_ASSESSOR: RiskAssessor(),
            SpecialistType.ESG_ANALYST: ESGAnalyst(),
        }

    async def _run_one(self, stype, specialist, request):
        try:
            out = await asyncio.wait_for(
                specialist.analyse(request.topic, {"date_range": request.date_range, "company_name": request.company_name}),
                timeout=SPECIALIST_TIMEOUT,
            )
            return stype, out
        except asyncio.TimeoutError:
            logger.error("specialist_timeout", specialist=stype.value)
            return stype, None
        except Exception as exc:
            logger.error("specialist_error", specialist=stype.value, error=str(exc))
            return stype, None

    async def run(self, request: ResearchRequest) -> FinalReport:
        """Execute the full research pipeline."""
        start = time.time()
        logger.info("pipeline_started", run_id=request.run_id, company=request.company_name)

        # Phase 1: Fan-out (in-process if LOCAL_MODE)
        if self.settings.local_mode:
            tasks = [self._run_one(st, sp, request) for st, sp in self.specialists.items()]
            raw_results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            from orchestrator.service_bus_orchestrator import ServiceBusOrchestrator
            sb_orch = ServiceBusOrchestrator()
            await sb_orch.dispatch_all(request)
            raw_results = [(st, None) for st in self.specialists.keys()]

        specialist_outputs = {}
        for res in raw_results:
            if isinstance(res, Exception):
                continue
            stype, output = res
            if output is not None:
                specialist_outputs[stype.value] = output

        if not specialist_outputs:
            raise ValueError("All specialist agents failed")

        logger.info("specialists_complete", count=len(specialist_outputs))

        # Phase 2: Synthesise
        synthesis = await synthesise(specialist_outputs, request.topic, request.company_name)
        logger.info("synthesis_complete")

        # Phase 3: Compliance gate
        compliance = await review_compliance(synthesis, request.company_name)
        logger.info("compliance_complete", approved=compliance.approved)

        total_time = time.time() - start
        report = FinalReport(run_id=request.run_id, topic=request.topic, company_name=request.company_name, synthesis=synthesis, compliance=compliance, total_pipeline_time=round(total_time, 2))

        # Phase 4: Store (optional)
        await self._store_report(report)

        logger.info("pipeline_complete", run_id=request.run_id, time=round(total_time, 2), approved=compliance.approved)
        return report

    async def _store_report(self, report: FinalReport) -> None:
        """Store report to Cosmos DB if configured."""
        if not self.settings.cosmos_key or self.settings.cosmos_key == "your-cosmos-key":
            logger.info("cosmos_skipped_not_configured")
            return
        try:
            from azure.cosmos.aio import CosmosClient
            async with CosmosClient(url=self.settings.cosmos_endpoint, credential=self.settings.cosmos_key) as client:
                db = client.get_database_client(self.settings.cosmos_database)
                container = db.get_container_client("research-reports")
                doc = report.model_dump()
                doc["id"] = report.run_id
                doc["created_at"] = doc["created_at"].isoformat()
                await container.create_item(body=doc)
                logger.info("report_stored", run_id=report.run_id)
        except Exception as exc:
            logger.error("store_failed", error=str(exc))
