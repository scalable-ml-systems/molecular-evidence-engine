from pprint import pprint

from app.agents.admet_agent import ADMETAgent
from app.agents.base import RunRequest
from app.agents.crossref_agent import CrossRefAgent
from app.agents.literature_agent import LiteratureAgent
from app.agents.patent_agent import PatentAgent
from app.bootstrap import build_tool_registry
from app.orchestrator.runtime import InMemoryRunRepository, SupervisorRuntime


def main() -> None:
    repository = InMemoryRunRepository()
    tool_registry = build_tool_registry()

    runtime = SupervisorRuntime(
        repository=repository,
        patent_agent=PatentAgent(tool_registry),
        literature_agent=LiteratureAgent(tool_registry),
        admet_agent=ADMETAgent(tool_registry),
        crossref_agent=CrossRefAgent(tool_registry),
    )

    artifact = runtime.run(RunRequest(query="acalabrutinib"))

    print("\n=== REGISTERED TOOLS ===")
    pprint(tool_registry.list_tools())

    print("\n=== FINAL RUNS ===")
    pprint(repository.runs)

    print("\n=== FINAL WORKSPACES ===")
    pprint(repository.workspaces)

    print("\n=== FINAL ARTIFACTS ===")
    pprint(repository.artifacts)

    print("\n=== FINAL REVIEWS ===")
    pprint(repository.reviews)

    print("\n=== RETURNED ARTIFACT SUMMARY ===")
    pprint(artifact.model_dump())


if __name__ == "__main__":
    main()