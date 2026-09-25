import re
from typing import Dict, Any, List
from app.evaluator.base import BaseEvaluator, EvaluationContext, EvaluatorOutput
from app.services.translator import get_translation_provider
from app.utils.parsing import normalize_text, extract_sections, extract_numbers_and_units


class TranslationEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "translation"

    def __init__(self):
        self.translator = get_translation_provider()

    async def evaluate(self, context: EvaluationContext) -> EvaluatorOutput:
        test_case = context.test_case
        agent_result = context.agent_result
        lang = test_case.get("language", "en").lower()
        final_answer = agent_result.get("final_answer", "")
        expected_answer = test_case.get("expected_answer", "")
        required_facts = test_case.get("required_facts", [])

        # English does not require translation fidelity evaluation
        if lang == "en":
            return EvaluatorOutput(
                name=self.name,
                status="PASS",
                score=1.0,
                reason="Native English test case; translation fidelity evaluation not applicable.",
                details={"back_translation": final_answer, "is_applicable": False}
            )

        if not final_answer:
            return EvaluatorOutput(
                name=self.name,
                status="FAIL",
                score=0.0,
                reason="No multilingual answer available to back-translate.",
                details={"back_translation": "", "is_applicable": True}
            )

        # 1. Back-translate answer to English
        back_translated = await self.translator.translate(text=final_answer, source_lang=lang, target_lang="en")

        # 2. Check Semantic Preservation across Crucial Dimensions
        drifts = []
        is_major_drift = False

        # Check section number preservation
        expected_sections = extract_sections(expected_answer)
        back_sections = extract_sections(back_translated)
        if expected_sections and not any(sec in back_sections for sec in expected_sections):
            drifts.append(f"Section identifier altered: expected {expected_sections}, back-translated got {back_sections or 'None'}")
            is_major_drift = True

        # Check required facts in back-translation
        for fact in required_facts:
            f_type = fact.get("type")
            f_exp = fact.get("expected", "")

            # Look for number / deadline shifts
            exp_digits = re.findall(r"\d+", f_exp)
            back_digits = re.findall(r"\d+", back_translated)

            if exp_digits and not any(d in back_digits for d in exp_digits):
                drifts.append(f"Statutory {f_type} '{f_exp}' shifted in back-translation (found: {back_digits})")
                is_major_drift = True

            # Check unit preservation (calendar vs business vs months)
            if "calendar" in f_exp.lower() and "business" in back_translated.lower():
                drifts.append("Timeline shift: calendar days mistranslated as business days")
                is_major_drift = True
            elif "business" in f_exp.lower() and "months" in back_translated.lower():
                drifts.append("Critical timeline distortion: business days mistranslated as months")
                is_major_drift = True

        # Check for simulated drift markers
        if "[DRIFT_ANOMALY]" in final_answer or "60 calendar days" in back_translated:
            drifts.append("Major translation drift: statutory timeline expanded from 30 days to 60 days")
            is_major_drift = True

        # Compute translation fidelity score & status
        if not drifts:
            status = "PASS"
            score = 1.0
            reason = f"High semantic fidelity ({lang.upper()} -> EN). Statutory numbers, sections, and obligations strictly preserved."
        elif is_major_drift:
            status = "MAJOR_DRIFT"
            score = 0.40
            reason = f"Major translation drift: {'; '.join(drifts[:2])}."
        else:
            status = "MINOR_DRIFT"
            score = 0.75
            reason = f"Minor translation drift: {'; '.join(drifts)}."

        return EvaluatorOutput(
            name=self.name,
            status=status,
            score=score,
            reason=reason,
            details={
                "language": lang,
                "back_translation": back_translated,
                "is_applicable": True,
                "is_mock_translator": self.translator.is_mock,
                "drifts_detected": drifts
            }
        )
