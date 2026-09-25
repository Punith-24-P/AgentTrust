import pytest
from app.evaluator.citation import CitationEvaluator
from app.evaluator.base import EvaluationContext


@pytest.mark.asyncio
async def test_citation_evaluator_valid():
    evaluator = CitationEvaluator()
    context = EvaluationContext(
        test_case={
            "id": "EN-001",
            "source_documents": [{"document_id": "DOC-CP-001", "section_id": "§4"}]
        },
        agent_result={
            "final_answer": "Under §4 of DOC-CP-001, permits require 30 days notice.",
            "citations": ["DOC-CP-001 §4"],
            "retrieved_documents": [{"document_id": "DOC-CP-001", "section_id": "§4"}]
        }
    )
    result = await evaluator.evaluate(context)
    assert result.status == "VALID"
    assert result.score == 1.0


@pytest.mark.asyncio
async def test_citation_evaluator_invalid_source():
    evaluator = CitationEvaluator()
    context = EvaluationContext(
        test_case={
            "id": "EN-001",
            "source_documents": [{"document_id": "DOC-CP-001", "section_id": "§4"}]
        },
        agent_result={
            "final_answer": "Under §4 of fake document.",
            "citations": ["DOC-FAKE-999 §4"],
            "retrieved_documents": []
        }
    )
    result = await evaluator.evaluate(context)
    assert result.status == "INVALID_SOURCE"
    assert result.score == 0.0


@pytest.mark.asyncio
async def test_citation_evaluator_mismatch():
    evaluator = CitationEvaluator()
    context = EvaluationContext(
        test_case={
            "id": "EN-001",
            "source_documents": [{"document_id": "DOC-CP-001", "section_id": "§4"}]
        },
        agent_result={
            "final_answer": "Under §18 of DOC-CP-001.",
            "citations": ["DOC-CP-001 §18"],
            "retrieved_documents": [{"document_id": "DOC-CP-001", "section_id": "§4"}]
        }
    )
    result = await evaluator.evaluate(context)
    assert result.status == "MISMATCH"
