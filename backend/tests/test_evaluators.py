import pytest
from app.evaluator.grounding import GroundingEvaluator
from app.evaluator.translation import TranslationEvaluator
from app.evaluator.trajectory import TrajectoryEvaluator
from app.evaluator.base import EvaluationContext


@pytest.mark.asyncio
async def test_grounding_supported():
    evaluator = GroundingEvaluator()
    context = EvaluationContext(
        test_case={
            "required_facts": [{"type": "deadline", "expected": "30 calendar days"}]
        },
        agent_result={
            "final_answer": "The application must be submitted within 30 calendar days.",
            "retrieved_documents": [
                {"document_id": "DOC-CP-001", "section_id": "§4", "content": "Applications must be submitted at least 30 calendar days prior."}
            ]
        }
    )
    result = await evaluator.evaluate(context)
    assert result.status == "SUPPORTED"
    assert result.score == 1.0


@pytest.mark.asyncio
async def test_grounding_unsupported_claim():
    evaluator = GroundingEvaluator()
    context = EvaluationContext(
        test_case={
            "required_facts": [{"type": "deadline", "expected": "30 calendar days"}]
        },
        agent_result={
            "final_answer": "The application must be submitted within 30 calendar days. Non-compliance results in immediate lifetime asset forfeiture without right of legal representation.",
            "retrieved_documents": [
                {"document_id": "DOC-CP-001", "section_id": "§4", "content": "Applications must be submitted at least 30 calendar days prior."}
            ]
        }
    )
    result = await evaluator.evaluate(context)
    assert result.status in ["UNSUPPORTED", "CONTRADICTED"]
    assert any(c["status"] == "UNSUPPORTED" for c in result.details["claims"])


@pytest.mark.asyncio
async def test_translation_fidelity():
    evaluator = TranslationEvaluator()
    # English test should pass without translation
    en_context = EvaluationContext(
        test_case={"language": "en", "expected_answer": "30 calendar days"},
        agent_result={"final_answer": "30 calendar days"}
    )
    en_res = await evaluator.evaluate(en_context)
    assert en_res.status == "PASS"

    # Kannada test with major drift
    kn_context = EvaluationContext(
        test_case={
            "language": "kn",
            "expected_answer": "§4 ರ ಪ್ರಕಾರ 30 ಕ್ಯಾಲೆಂಡರ್ ದಿನಗಳು",
            "required_facts": [{"type": "deadline", "expected": "30 calendar days"}]
        },
        agent_result={"final_answer": "§4 ರ ಪ್ರಕಾರ [DRIFT_ANOMALY] 60 calendar days"}
    )
    kn_res = await evaluator.evaluate(kn_context)
    assert kn_res.status == "MAJOR_DRIFT"
    assert kn_res.score < 0.60


@pytest.mark.asyncio
async def test_trajectory_loop_and_retrieval():
    evaluator = TrajectoryEvaluator()

    # Normal trajectory
    ok_context = EvaluationContext(
        test_case={"source_documents": [{"document_id": "DOC-CP-001"}]},
        agent_result={
            "trace": [
                {"step": 1, "event_type": "agent_start"},
                {"step": 2, "event_type": "retrieval", "input_data": {"query": "permits"}},
                {"step": 3, "event_type": "generation", "output_data": {"text": "Answer"}},
                {"step": 4, "event_type": "agent_end"}
            ]
        }
    )
    ok_res = await evaluator.evaluate(ok_context)
    assert ok_res.status == "PASS"

    # Missing retrieval
    no_ret_context = EvaluationContext(
        test_case={"source_documents": [{"document_id": "DOC-CP-001"}]},
        agent_result={
            "trace": [
                {"step": 1, "event_type": "agent_start"},
                {"step": 2, "event_type": "generation"},
                {"step": 3, "event_type": "agent_end"}
            ]
        }
    )
    no_ret_res = await evaluator.evaluate(no_ret_context)
    assert no_ret_res.status == "FAIL"

    # Repeated loop
    loop_context = EvaluationContext(
        test_case={"source_documents": [{"document_id": "DOC-CP-001"}]},
        agent_result={
            "trace": [
                {"step": 1, "event_type": "agent_start"},
                {"step": 2, "event_type": "retrieval"},
                {"step": 3, "event_type": "retrieval"},  # Consecutive redundant loop
                {"step": 4, "event_type": "generation"},
                {"step": 5, "event_type": "agent_end"}
            ]
        }
    )
    loop_res = await evaluator.evaluate(loop_context)
    assert loop_res.status == "WARNING"
    assert loop_res.details["loop_detected"] is True
