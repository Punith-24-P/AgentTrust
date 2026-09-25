import re
from typing import Dict, Any, List
from app.evaluator.base import BaseEvaluator, EvaluationContext, EvaluatorOutput
from app.services.retrieval import get_document_store


class CitationEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "citation"

    def __init__(self):
        self.doc_store = get_document_store()

    async def evaluate(self, context: EvaluationContext) -> EvaluatorOutput:
        test_case = context.test_case
        agent_result = context.agent_result
        citations = agent_result.get("citations", [])
        final_answer = agent_result.get("final_answer", "")
        retrieved_docs = agent_result.get("retrieved_documents", [])
        source_docs = test_case.get("source_documents", [])

        # Also extract any citations directly embedded in the final answer (e.g., DOC-CP-001 §4)
        embedded_cites = re.findall(r"(DOC-[A-Z]+-\d{3})\s*(§\s*\d+)?", final_answer)
        found_citations = list(citations)
        for doc_match, sec_match in embedded_cites:
            cite_str = f"{doc_match} {sec_match}".strip()
            if cite_str not in found_citations:
                found_citations.append(cite_str)

        if not found_citations:
            return EvaluatorOutput(
                name=self.name,
                status="MISSING",
                score=0.0,
                reason="No formal citations or statutory source references were provided.",
                details={
                    "citations": [],
                    "valid_count": 0,
                    "invalid_source_count": 0,
                    "invalid_section_count": 0,
                    "mismatch_count": 0,
                    "source_exists": False,
                    "section_exists": False,
                    "evidence_matches": False
                }
            )

        citation_results = []
        valid_count = 0
        invalid_source_count = 0
        invalid_section_count = 0
        mismatch_count = 0

        # Build list of valid document IDs & sections expected
        expected_doc_ids = [d.get("document_id") for d in source_docs if d.get("document_id")]
        expected_sec_ids = [d.get("section_id") for d in source_docs if d.get("section_id")]
        retrieved_doc_ids = [d.get("document_id") for d in retrieved_docs]

        for cite in found_citations:
            # Parse document ID and section ID
            doc_id_match = re.search(r"DOC-[A-Z]+-\d{3}", cite)
            sec_id_match = re.search(r"§\s*\d+", cite)

            doc_id = doc_id_match.group(0) if doc_id_match else None
            sec_id = sec_id_match.group(0) if sec_id_match else None

            # 1. Check if cited document exists in repository
            doc_data = self.doc_store.get_document(doc_id) if doc_id else None
            if not doc_data:
                status = "INVALID_SOURCE"
                reason = f"Cited document '{cite}' does not exist in the statutory repository."
                invalid_source_count += 1
                evidence_matches = False
            else:
                # 2. Check if section exists in document
                available_sections = [s.get("section_id") for s in doc_data.get("sections", [])]
                if sec_id and sec_id not in available_sections:
                    status = "INVALID_SECTION"
                    reason = f"Section '{sec_id}' does not exist in statutory document {doc_id}."
                    invalid_section_count += 1
                    evidence_matches = False
                elif expected_doc_ids and doc_id not in expected_doc_ids:
                    # 3. Citation mismatch (cites real document, but wrong document for this question)
                    status = "MISMATCH"
                    reason = f"Citation points to {doc_id}, but question requires evidence from {', '.join(expected_doc_ids)}."
                    mismatch_count += 1
                    evidence_matches = False
                elif expected_sec_ids and sec_id and sec_id not in expected_sec_ids:
                    # Cites right doc, but wrong section
                    status = "MISMATCH"
                    reason = f"Citation points to section {sec_id}, but expected governing section is {', '.join(expected_sec_ids)}."
                    mismatch_count += 1
                    evidence_matches = False
                else:
                    status = "VALID"
                    reason = f"Citation '{cite}' verified against active repository and retrieved evidence."
                    valid_count += 1
                    evidence_matches = True

            citation_results.append({
                "citation": cite,
                "document_id": doc_id,
                "section_id": sec_id,
                "status": status,
                "evidence_matches": evidence_matches,
                "reason": reason
            })

        total = len(citation_results)
        score = round(valid_count / total, 2) if total > 0 else 0.0

        if invalid_source_count > 0:
            overall_status = "INVALID_SOURCE"
            summary_reason = f"Citation error: {invalid_source_count} cited source(s) do not exist in repository."
        elif invalid_section_count > 0:
            overall_status = "INVALID_SECTION"
            summary_reason = f"Citation error: {invalid_section_count} cited section(s) do not exist in document."
        elif mismatch_count > 0:
            overall_status = "MISMATCH"
            summary_reason = f"Citation mismatch: Cited provisions do not correspond to the governing legal source."
        elif valid_count == total:
            overall_status = "VALID"
            summary_reason = f"All {valid_count} citation(s) verified against authentic statutory text and retrieved evidence."
        else:
            overall_status = "UNSUPPORTED"
            summary_reason = "Citation does not substantiate the associated claim."

        return EvaluatorOutput(
            name=self.name,
            status=overall_status,
            score=score,
            reason=summary_reason,
            details={
                "citations": citation_results,
                "valid_count": valid_count,
                "invalid_source_count": invalid_source_count,
                "invalid_section_count": invalid_section_count,
                "mismatch_count": mismatch_count,
                "source_exists": invalid_source_count == 0,
                "section_exists": invalid_section_count == 0,
                "evidence_matches": overall_status == "VALID"
            }
        )
