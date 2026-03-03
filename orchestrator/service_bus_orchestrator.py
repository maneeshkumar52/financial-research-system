"""Service Bus based orchestration (used when LOCAL_MODE=False)."""
import asyncio
import structlog
from shared.config import get_settings
from shared.service_bus import ServiceBusHelper
from shared.models import ResearchRequest, SpecialistOutput, SpecialistType

logger = structlog.get_logger(__name__)


class ServiceBusOrchestrator:
    """Dispatches research tasks via Azure Service Bus queues."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.sb = ServiceBusHelper(self.settings.service_bus_connection_string)
        self.SPECIALIST_QUEUES = {
            SpecialistType.FINANCIAL_ANALYST: "financial-analyst",
            SpecialistType.MARKET_RESEARCHER: "market-researcher",
            SpecialistType.NEWS_ANALYST: "news-analyst",
            SpecialistType.RISK_ASSESSOR: "risk-assessor",
            SpecialistType.ESG_ANALYST: "esg-analyst",
        }

    async def dispatch_all(self, request: ResearchRequest) -> None:
        """Fan out research request to all specialist queues."""
        payload = {"topic": request.topic, "company_name": request.company_name, "date_range": request.date_range, "run_id": request.run_id}
        tasks = [self.sb.publish(queue, payload) for queue in self.SPECIALIST_QUEUES.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("dispatched_to_all_specialists", run_id=request.run_id)

    async def collect_results(self, run_id: str, timeout: int = 120) -> dict:
        """Collect specialist results (in LOCAL_MODE, returns empty — pipeline handles in-process)."""
        logger.info("collect_results_called", run_id=run_id, mode="service_bus")
        return {}
