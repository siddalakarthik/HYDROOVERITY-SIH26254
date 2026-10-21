"""Select an explicit operational service inside the existing request transaction."""

from .services.administration import AdministrationService
from .services.assets import AssetService
from .services.complaints import ComplaintService
from .services.evidence import EvidenceService
from .services.incidents import IncidentService
from .services.organizations import OrganizationService
from .services.repairs import RepairService
from .services.verification import VerificationService
from .services.work_orders import WorkOrderService

SERVICES = {
    "Organization": OrganizationService,
    "Administration": AdministrationService,
    "Water zones": AssetService,
    "Pipeline assets": AssetService,
    "Complaints": ComplaintService,
    "Incidents": IncidentService,
    "Work orders": WorkOrderService,
    "Repairs": RepairService,
    "Verification": VerificationService,
    "Evidence": EvidenceService,
}


class Operations:
    def __init__(self, scope):
        self.service = SERVICES[scope.op["group"]](scope)

    @property
    def result(self):
        return self.service.result

    def run(self, body, parent=None):
        if self.service.s.op["group"] == "Administration":
            self.service.governance_reason = body.get("reason")
        return self.service.run(body, parent)
