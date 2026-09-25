import os
import json
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.project import Project
from app.models.agent import Agent
from app.models.dataset import Dataset, TestCase
from app.models.document import Document


async def seed_demo_data(session: AsyncSession) -> Dict[str, Any]:
    """
    Populates database with default demonstration project, agents, documents, and test cases.
    Idempotent: avoids duplicate seeding if project already exists.
    """
    # 1. Check if default project exists
    q = select(Project).where(Project.name == "Aethelgard Civic Reliability")
    res = await session.execute(q)
    existing_project = res.scalars().first()

    if existing_project:
        # Fetch associated agents and dataset
        ag_q = select(Agent).where(Agent.project_id == existing_project.id)
        ag_res = await session.execute(ag_q)
        agents = ag_res.scalars().all()

        ds_q = select(Dataset).where(Dataset.project_id == existing_project.id)
        ds_res = await session.execute(ds_q)
        dataset = ds_res.scalars().first()

        return {
            "project_id": existing_project.id,
            "baseline_agent_id": agents[0].id if agents else None,
            "optimized_agent_id": agents[1].id if len(agents) > 1 else None,
            "dataset_id": dataset.id if dataset else None,
            "message": "Existing demo data loaded."
        }

    # 2. Create Project
    project = Project(
        name="Aethelgard Civic Reliability",
        description="Benchmark workspace for assessing AI agent statutory compliance, evidence grounding, and multilingual fidelity across civic directives."
    )
    session.add(project)
    await session.flush()

    # 3. Create Documents
    doc_dir = os.path.join(settings.DATA_DIR, "demo_documents")
    if os.path.exists(doc_dir):
        for fname in sorted(os.listdir(doc_dir)):
            if fname.endswith(".json"):
                with open(os.path.join(doc_dir, fname), "r", encoding="utf-8") as f:
                    d_data = json.load(f)
                    doc_obj = Document(
                        project_id=project.id,
                        document_id=d_data.get("document_id"),
                        title=d_data.get("title"),
                        authority=d_data.get("authority", ""),
                        enacted_date=d_data.get("enacted_date", ""),
                        sections=d_data.get("sections", []),
                        metadata_json=d_data.get("metadata", {})
                    )
                    session.add(doc_obj)
    await session.flush()

    # 4. Create Agents (Baseline vs Optimized)
    baseline_agent = Agent(
        project_id=project.id,
        name="CivicTrust RAG Assistant (Baseline)",
        description="Demo agent under test with simulated failure modes for citation mismatch, translation drift, and wrong deadlines.",
        adapter_type="demo",
        version="1.0.0-baseline",
        model="agenttrust-demo-hybrid",
        supported_languages=["en", "kn", "hi", "te"],
        config_json={
            "simulation_rates": {
                "wrong_fact_rate": 0.15,
                "citation_error_rate": 0.12,
                "translation_drift_rate": 0.18,
                "unsupported_claim_rate": 0.12,
                "retrieval_skip_rate": 0.06,
                "loop_anomaly_rate": 0.06
            }
        }
    )
    session.add(baseline_agent)

    optimized_agent = Agent(
        project_id=project.id,
        name="CivicTrust RAG Assistant (Optimized)",
        description="Improved agent under test with corrected statutory prompt constraints, verified citations, and zero simulated drift.",
        adapter_type="demo",
        version="2.0.0-optimized",
        model="agenttrust-demo-hybrid",
        supported_languages=["en", "kn", "hi", "te"],
        config_json={
            "simulation_rates": {
                "wrong_fact_rate": 0.0,
                "citation_error_rate": 0.0,
                "translation_drift_rate": 0.0,
                "unsupported_claim_rate": 0.0,
                "retrieval_skip_rate": 0.0,
                "loop_anomaly_rate": 0.0
            }
        }
    )
    session.add(optimized_agent)
    await session.flush()

    # 5. Create Dataset & Test Cases
    dataset = Dataset(
        project_id=project.id,
        name="Aethelgard Civic Directives Test Suite",
        description="32 structured test cases covering public permits, environmental compliance, procurement, and privacy in English, Kannada, Hindi, and Telugu.",
        version="1.0.0"
    )
    session.add(dataset)
    await session.flush()

    test_cases_file = os.path.join(settings.DATA_DIR, "demo_test_cases.json")
    if os.path.exists(test_cases_file):
        with open(test_cases_file, "r", encoding="utf-8") as f:
            cases_data = json.load(f)
            for c in cases_data:
                tc = TestCase(
                    dataset_id=dataset.id,
                    external_id=c.get("id"),
                    language=c.get("language", "en"),
                    category=c.get("category", "general"),
                    question=c.get("question"),
                    expected_answer=c.get("expected_answer"),
                    source_documents=c.get("source_documents", []),
                    required_facts=c.get("required_facts", []),
                    potential_traps=c.get("potential_traps", [])
                )
                session.add(tc)

    await session.commit()

    return {
        "project_id": project.id,
        "baseline_agent_id": baseline_agent.id,
        "optimized_agent_id": optimized_agent.id,
        "dataset_id": dataset.id,
        "message": "Demo project, agents, documents, and 32 test cases seeded successfully."
    }
