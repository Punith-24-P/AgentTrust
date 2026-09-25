from typing import List, Dict, Any, Optional


class MetricsEngine:
    """
    Computes dynamic metrics, language breakdowns, severity counts,
    and before/after comparison deltas. Never hard-codes results.
    """

    @staticmethod
    def compute_run_metrics(evaluation_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_tests = len(evaluation_records)
        if total_tests == 0:
            return {
                "composite_score": 0.0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "overall_pass_rate": 0.0,
                "correctness": {"score": 0.0, "pass_rate": 0.0, "total": 0, "passed": 0, "failed": 0},
                "grounding": {"score": 0.0, "supported_rate": 0.0, "claims_total": 0, "supported": 0, "unsupported": 0, "contradicted": 0},
                "citation": {"score": 0.0, "valid_rate": 0.0, "citations_total": 0, "valid": 0, "invalid": 0, "mismatch": 0, "missing": 0},
                "translation": {"score": 0.0, "pass_rate": 0.0, "minor_drift_rate": 0.0, "major_drift_rate": 0.0, "evaluated_tests": 0},
                "trajectory": {"score": 0.0, "retrieval_rate": 0.0, "loop_rate": 0.0, "pass_rate": 0.0},
                "severity_breakdown": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "language_breakdown": {}
            }

        passed_tests = sum(1 for r in evaluation_records if r.get("overall_status") == "PASS")
        composite_scores = [r.get("composite_score", 0.0) for r in evaluation_records]
        avg_composite = round(sum(composite_scores) / total_tests, 3)

        # 1. Correctness
        corr_scores = [r.get("correctness", {}).get("score", 0.0) for r in evaluation_records]
        corr_passed = sum(1 for r in evaluation_records if r.get("correctness", {}).get("status") == "PASS")
        corr_rate = round(corr_passed / total_tests, 3)
        corr_avg_score = round(sum(corr_scores) / total_tests, 3)

        # 2. Grounding
        total_claims = sum(r.get("grounding", {}).get("claims_count", 0) for r in evaluation_records)
        supported_claims = sum(r.get("grounding", {}).get("supported", 0) for r in evaluation_records)
        unsupported_claims = sum(r.get("grounding", {}).get("unsupported", 0) for r in evaluation_records)
        contradicted_claims = sum(r.get("grounding", {}).get("contradicted", 0) for r in evaluation_records)
        ground_scores = [r.get("grounding", {}).get("score", 0.0) for r in evaluation_records]
        ground_avg_score = round(sum(ground_scores) / total_tests, 3)
        supported_rate = round(supported_claims / total_claims, 3) if total_claims > 0 else 1.0

        # 3. Citation
        total_cites = 0
        valid_cites = 0
        mismatch_cites = 0
        missing_cites = sum(1 for r in evaluation_records if r.get("citation", {}).get("status") == "MISSING")
        invalid_cites = 0

        for r in evaluation_records:
            cite_data = r.get("citation", {})
            c_list = cite_data.get("citations", [])
            total_cites += len(c_list)
            for c in c_list:
                status = c.get("status")
                if status == "VALID":
                    valid_cites += 1
                elif status == "MISMATCH":
                    mismatch_cites += 1
                elif status in ["INVALID_SOURCE", "INVALID_SECTION"]:
                    invalid_cites += 1

        cite_scores = [r.get("citation", {}).get("score", 0.0) for r in evaluation_records]
        cite_avg_score = round(sum(cite_scores) / total_tests, 3)
        valid_cite_rate = round(valid_cites / max(total_cites, 1), 3) if total_cites > 0 else 0.0

        # 4. Translation
        multilingual_records = [r for r in evaluation_records if r.get("language") != "en"]
        num_multi = len(multilingual_records)
        if num_multi > 0:
            trans_passed = sum(1 for r in multilingual_records if r.get("translation", {}).get("status") == "PASS")
            trans_minor = sum(1 for r in multilingual_records if r.get("translation", {}).get("status") == "MINOR_DRIFT")
            trans_major = sum(1 for r in multilingual_records if r.get("translation", {}).get("status") == "MAJOR_DRIFT")
            trans_scores = [r.get("translation", {}).get("score", 0.0) for r in multilingual_records]
            trans_avg_score = round(sum(trans_scores) / num_multi, 3)
            trans_pass_rate = round(trans_passed / num_multi, 3)
            trans_minor_rate = round(trans_minor / num_multi, 3)
            trans_major_rate = round(trans_major / num_multi, 3)
        else:
            trans_avg_score = 1.0
            trans_pass_rate = 1.0
            trans_minor_rate = 0.0
            trans_major_rate = 0.0

        # 5. Trajectory
        traj_retrieval_ok = sum(1 for r in evaluation_records if r.get("trajectory", {}).get("retrieval_executed", True))
        traj_loops = sum(1 for r in evaluation_records if r.get("trajectory", {}).get("loop_detected", False))
        traj_passed = sum(1 for r in evaluation_records if r.get("trajectory", {}).get("status") == "PASS")
        traj_scores = [r.get("trajectory", {}).get("score", 0.0) for r in evaluation_records]
        traj_avg_score = round(sum(traj_scores) / total_tests, 3)

        # Severity breakdown
        severities = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for r in evaluation_records:
            sev = r.get("severity", "LOW")
            severities[sev] = severities.get(sev, 0) + 1

        # Language breakdown
        language_breakdown = {}
        languages = sorted(list(set(r.get("language", "en") for r in evaluation_records)))
        for l in languages:
            l_recs = [r for r in evaluation_records if r.get("language") == l]
            l_total = len(l_recs)
            l_passed = sum(1 for r in l_recs if r.get("overall_status") == "PASS")
            l_corr_score = sum(r.get("correctness", {}).get("score", 0.0) for r in l_recs) / l_total
            l_ground_score = sum(r.get("grounding", {}).get("score", 0.0) for r in l_recs) / l_total
            l_cite_score = sum(r.get("citation", {}).get("score", 0.0) for r in l_recs) / l_total
            l_trans_score = sum(r.get("translation", {}).get("score", 0.0) for r in l_recs) / l_total if l != "en" else None
            l_traj_score = sum(r.get("trajectory", {}).get("score", 0.0) for r in l_recs) / l_total
            l_composite = sum(r.get("composite_score", 0.0) for r in l_recs) / l_total

            language_breakdown[l] = {
                "total_tests": l_total,
                "passed_tests": l_passed,
                "pass_rate": round(l_passed / l_total, 3),
                "composite_score": round(l_composite, 3),
                "correctness_score": round(l_corr_score, 3),
                "grounding_score": round(l_ground_score, 3),
                "citation_score": round(l_cite_score, 3),
                "translation_score": round(l_trans_score, 3) if l_trans_score is not None else 1.0,
                "trajectory_score": round(l_traj_score, 3)
            }

        return {
            "composite_score": avg_composite,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "overall_pass_rate": round(passed_tests / total_tests, 3),
            "correctness": {
                "score": corr_avg_score,
                "pass_rate": corr_rate,
                "total": total_tests,
                "passed": corr_passed,
                "failed": total_tests - corr_passed
            },
            "grounding": {
                "score": ground_avg_score,
                "supported_rate": supported_rate,
                "claims_total": total_claims,
                "supported": supported_claims,
                "unsupported": unsupported_claims,
                "contradicted": contradicted_claims
            },
            "citation": {
                "score": cite_avg_score,
                "valid_rate": valid_cite_rate,
                "citations_total": total_cites,
                "valid": valid_cites,
                "invalid": invalid_cites,
                "mismatch": mismatch_cites,
                "missing": missing_cites
            },
            "translation": {
                "score": trans_avg_score,
                "pass_rate": trans_pass_rate,
                "minor_drift_rate": trans_minor_rate,
                "major_drift_rate": trans_major_rate,
                "evaluated_tests": num_multi
            },
            "trajectory": {
                "score": traj_avg_score,
                "retrieval_rate": round(traj_retrieval_ok / total_tests, 3),
                "loop_rate": round(traj_loops / total_tests, 3),
                "pass_rate": round(traj_passed / total_tests, 3)
            },
            "severity_breakdown": severities,
            "language_breakdown": language_breakdown
        }

    @staticmethod
    def compare_runs(before_metrics: Dict[str, Any], after_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically calculates differences between baseline and after runs.
        Honest calculation: negative deltas (regressions) are clearly recorded.
        """
        keys = ["composite_score", "overall_pass_rate"]
        metric_deltas = {}

        for k in keys:
            b_val = float(before_metrics.get(k, 0.0))
            a_val = float(after_metrics.get(k, 0.0))
            delta = round(a_val - b_val, 3)
            metric_deltas[k] = {
                "before": b_val,
                "after": a_val,
                "delta": delta,
                "improved": delta >= 0
            }

        # Sub-evaluator scores
        eval_keys = ["correctness", "grounding", "citation", "translation", "trajectory"]
        for ek in eval_keys:
            b_score = float(before_metrics.get(ek, {}).get("score", 0.0))
            a_score = float(after_metrics.get(ek, {}).get("score", 0.0))
            delta = round(a_score - b_score, 3)
            metric_deltas[f"{ek}_score"] = {
                "before": b_score,
                "after": a_score,
                "delta": delta,
                "improved": delta >= 0
            }

        # Language deltas
        lang_deltas = {}
        all_langs = set(before_metrics.get("language_breakdown", {}).keys()).union(
            after_metrics.get("language_breakdown", {}).keys()
        )
        for lang in sorted(list(all_langs)):
            b_l = before_metrics.get("language_breakdown", {}).get(lang, {})
            a_l = after_metrics.get("language_breakdown", {}).get(lang, {})
            b_comp = float(b_l.get("composite_score", 0.0))
            a_comp = float(a_l.get("composite_score", 0.0))
            delta = round(a_comp - b_comp, 3)
            lang_deltas[lang] = {
                "composite_score": {
                    "before": b_comp,
                    "after": a_comp,
                    "delta": delta,
                    "improved": delta >= 0
                }
            }

        return {
            "metrics": metric_deltas,
            "language_deltas": lang_deltas
        }
