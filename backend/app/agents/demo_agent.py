import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.agents.base import BaseAgentAdapter, AgentRunResult
from app.services.retrieval import get_document_store


class DemoAgentAdapter(BaseAgentAdapter):
    """
    Built-in demonstration AI agent.
    Performs document retrieval, tool calling, and response synthesis
    with configurable, deterministic failure simulation modes.
    """

    def __init__(self, failure_modes: Optional[Dict[str, float]] = None):
        # Default baseline simulation failure rates
        self.failure_modes = failure_modes or {
            "wrong_fact_rate": 0.15,
            "citation_error_rate": 0.12,
            "translation_drift_rate": 0.18,
            "unsupported_claim_rate": 0.12,
            "retrieval_skip_rate": 0.06,
            "loop_anomaly_rate": 0.06
        }
        self.doc_store = get_document_store()

    def _should_fail(self, mode_key: str, seed_key: str) -> bool:
        """Deterministic pseudo-random check based on test case ID."""
        rate = self.failure_modes.get(mode_key, 0.0)
        if rate <= 0.0:
            return False
        # Hash seed string to get deterministic float in [0, 1]
        hash_val = abs(hash(f"{seed_key}:{mode_key}")) % 1000
        return (hash_val / 1000.0) < rate

    async def run(self, test_case: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> AgentRunResult:
        start_time = time.time()
        test_id = test_case.get("id", "UNKNOWN")
        lang = test_case.get("language", "en")
        question = test_case.get("question", "")
        expected = test_case.get("expected_answer", "")
        source_docs = test_case.get("source_documents", [])

        # Override failure modes if provided in runtime config
        if config and "simulation_rates" in config:
            self.failure_modes.update(config["simulation_rates"])

        trace = []
        step = 1

        # 1. Agent Start
        trace.append({
            "step": step,
            "event_type": "agent_start",
            "input_data": {"question": question, "language": lang, "test_id": test_id},
            "output_data": {"status": "initialized"},
            "metadata_json": {"agent": "DemoAgent", "version": "1.0.0"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        step += 1

        # 2. Retrieval Evaluation & Execution
        skip_retrieval = self._should_fail("retrieval_skip_rate", test_id)
        loop_retrieval = self._should_fail("loop_anomaly_rate", test_id)
        retrieved_docs = []

        if not skip_retrieval:
            target_ids = [d.get("document_id") for d in source_docs if d.get("document_id")]
            retrieved_docs = self.doc_store.retrieve(query=question, top_k=2, target_doc_ids=target_ids)

            trace.append({
                "step": step,
                "event_type": "retrieval",
                "input_data": {"query": question, "target_documents": target_ids},
                "output_data": {"retrieved_count": len(retrieved_docs), "documents": retrieved_docs},
                "metadata_json": {"store": "AethelgardPolicyStore"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            step += 1

            # Simulated repeated retrieval loop anomaly
            if loop_retrieval:
                trace.append({
                    "step": step,
                    "event_type": "retrieval",
                    "input_data": {"query": question, "retry_count": 1},
                    "output_data": {"retrieved_count": len(retrieved_docs), "documents": retrieved_docs},
                    "metadata_json": {"anomaly": "redundant_loop"},
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                step += 1

        # 3. Tool Execution: Statutory Compliance Calculator
        trace.append({
            "step": step,
            "event_type": "tool_call",
            "input_data": {
                "tool_name": "statutory_compliance_calculator",
                "parameters": {"test_id": test_id, "jurisdiction": "Aethelgard Metropolitan Region"}
            },
            "output_data": {},
            "metadata_json": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        step += 1

        trace.append({
            "step": step,
            "event_type": "tool_result",
            "input_data": {"tool_name": "statutory_compliance_calculator"},
            "output_data": {"status": "SUCCESS", "applicable_jurisdiction": "Aethelgard Metropolitan Region", "verified": True},
            "metadata_json": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        step += 1

        # 4. Generate Final Answer with Configured Failure Injections
        final_answer = expected
        citations = []

        # Determine target document & section for citations
        first_doc = source_docs[0] if source_docs else {}
        doc_id = first_doc.get("document_id", "DOC-CP-001")
        sec_id = first_doc.get("section_id", "§4")

        # Citation error injection
        if self._should_fail("citation_error_rate", test_id):
            if test_id.endswith("2") or test_id.endswith("7"):
                citations = ["DOC-CP-001 §99"]  # Invalid section
            else:
                citations = ["DOC-MISMATCH-999 §1"]  # Invalid source document
        else:
            citations = [f"{doc_id} {sec_id}"]

        # Wrong fact injection
        if self._should_fail("wrong_fact_rate", test_id):
            if "30 calendar days" in final_answer:
                final_answer = final_answer.replace("30 calendar days", "60 calendar days")
            elif "14 business days" in final_answer:
                final_answer = final_answer.replace("14 business days", "90 calendar days")
            elif "5,000 credits" in final_answer:
                final_answer = final_answer.replace("5,000 credits", "500 credits")
            elif "2 hours" in final_answer:
                final_answer = final_answer.replace("2 hours", "48 hours")
            elif "§4" in final_answer:
                final_answer = final_answer.replace("§4", "§18")
            elif "2,500 square meters" in final_answer:
                final_answer = final_answer.replace("2,500 square meters", "10,000 square meters")

        # Unsupported claim injection
        if self._should_fail("unsupported_claim_rate", test_id):
            final_answer += " Furthermore, non-compliance results in immediate lifetime asset forfeiture without right of legal representation."

        # Translation drift injection (for non-English)
        if lang != "en" and self._should_fail("translation_drift_rate", test_id):
            final_answer += " [DRIFT_ANOMALY] The submission must be completed within 60 calendar days."

        trace.append({
            "step": step,
            "event_type": "generation",
            "input_data": {"prompt_tokens": 340, "retrieved_count": len(retrieved_docs)},
            "output_data": {"answer_snippet": final_answer[:120], "citations": citations},
            "metadata_json": {"model": "agenttrust-demo-hybrid"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        step += 1

        if lang != "en":
            trace.append({
                "step": step,
                "event_type": "translation",
                "input_data": {"target_language": lang},
                "output_data": {"status": "completed"},
                "metadata_json": {"service": "DemoTranslationEngine"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            step += 1

        # 5. Agent End
        latency_ms = int((time.time() - start_time) * 1000)
        trace.append({
            "step": step,
            "event_type": "agent_end",
            "input_data": {},
            "output_data": {"status": "SUCCESS", "latency_ms": latency_ms},
            "metadata_json": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        return AgentRunResult(
            final_answer=final_answer,
            language=lang,
            retrieved_documents=retrieved_docs,
            citations=citations,
            trace=trace,
            metadata={
                "simulation": True,
                "injected_failures": {
                    "skip_retrieval": skip_retrieval,
                    "loop_anomaly": loop_retrieval,
                    "wrong_fact": self._should_fail("wrong_fact_rate", test_id),
                    "citation_error": self._should_fail("citation_error_rate", test_id),
                    "translation_drift": lang != "en" and self._should_fail("translation_drift_rate", test_id),
                    "unsupported_claim": self._should_fail("unsupported_claim_rate", test_id)
                }
            },
            latency_ms=max(12, latency_ms),
            status="SUCCESS"
        )
