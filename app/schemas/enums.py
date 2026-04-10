from enum import Enum


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentName(str, Enum):
    SUPERVISOR = "supervisor"
    PATENT = "patent_agent"
    LITERATURE = "literature_agent"
    ADMET = "admet_agent"
    CROSSREF = "crossref_agent"
    REPORT = "report_assembler"


class SourceType(str, Enum):
    LITERATURE = "literature"
    PATENT = "patent"
    ASSAY = "assay"
    COMPUTED = "computed"
    MEMORY = "memory"


class MeasurementType(str, Enum):
    IC50 = "IC50"
    KD = "Kd"
    EC50 = "EC50"
    INHIBITION = "inhibition"
    OCCUPANCY = "occupancy"
    UNKNOWN = "unknown"


class AssayCategory(str, Enum):
    ENZYMATIC = "enzymatic"
    BINDING = "binding"
    CELLULAR = "cellular"
    OCCUPANCY = "occupancy"
    UNKNOWN = "unknown"


class ArtifactType(str, Enum):
    EVIDENCE_BRIEF = "evidence_brief"


class ReviewDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RERUN_REQUESTED = "rerun_requested"