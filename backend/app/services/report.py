import json
import csv
import io
from typing import Dict, Any, List
from jinja2 import Template

HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentTrust Reliability Report - Run {{ run.id[:8] }}</title>
    <style>
        :root {
            --bg-base: #0b0f19;
            --bg-surface: #111827;
            --bg-surface-elevated: #1f2937;
            --border-subtle: #1e293b;
            --border-strong: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-primary: #38bdf8;
            --accent-success: #34d399;
            --accent-warning: #fbbf24;
            --accent-danger: #f87171;
            --accent-purple: #c084fc;
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
            background: var(--bg-base);
            color: var(--text-primary);
            margin: 0;
            padding: 40px 24px;
            line-height: 1.5;
        }
        .container { max-width: 1140px; margin: 0 auto; }
        .header {
            border-bottom: 1px solid var(--border-subtle);
            padding-bottom: 24px;
            margin-bottom: 32px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 16px;
        }
        .title { font-size: 26px; font-weight: 800; color: var(--accent-primary); margin: 0 0 6px 0; letter-spacing: -0.02em; }
        .subtitle { font-size: 13px; color: var(--text-secondary); }
        .tag { font-family: monospace; background: var(--bg-surface-elevated); padding: 3px 8px; border-radius: 4px; font-size: 12px; border: 1px solid var(--border-strong); }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
        .badge-pass { background: #064e3b; color: var(--accent-success); border: 1px solid #059669; }
        .badge-fail { background: #7f1d1d; color: var(--accent-danger); border: 1px solid #dc2626; }
        .badge-warning { background: #78350f; color: var(--accent-warning); border: 1px solid #d97706; }
        .badge-demo { background: #3b0764; color: #d8b4fe; border: 1px solid #9333ea; }
        
        .section {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }
        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border-subtle);
            padding-bottom: 12px;
            margin-bottom: 20px;
        }
        .section-title { font-size: 16px; font-weight: 700; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.04em; margin: 0; display: flex; align-items: center; gap: 8px; }
        .section-num { color: var(--accent-primary); font-size: 13px; }
        
        .grid-kpi { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; }
        .card { background: var(--bg-surface-elevated); border: 1px solid var(--border-strong); border-radius: 8px; padding: 18px; }
        .card-label { font-size: 11px; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
        .card-value { font-size: 28px; font-weight: 800; margin-top: 8px; color: var(--text-primary); }
        .card-desc { font-size: 11px; color: var(--text-secondary); margin-top: 6px; }

        table { width: 100%; border-collapse: collapse; background: var(--bg-surface-elevated); border-radius: 8px; overflow: hidden; font-size: 13px; }
        th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--border-subtle); }
        th { background: #0f172a; color: var(--text-secondary); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
        tr:hover { background: rgba(255,255,255,0.02); }

        .callout {
            background: #0f172a;
            border-left: 4px solid var(--accent-primary);
            padding: 16px 20px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 20px;
            font-size: 13px;
            color: #cbd5e1;
        }
        .callout-warning { border-left-color: var(--accent-warning); }
        .callout-danger { border-left-color: var(--accent-danger); }

        .failure-item {
            background: #181c2a;
            border: 1px solid #374151;
            border-left: 4px solid var(--accent-danger);
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .failure-item h4 { margin: 0 0 10px 0; font-size: 14px; display: flex; justify-content: space-between; }
        .code-box {
            background: #0b0f19;
            padding: 10px 14px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
            color: #94a3b8;
            margin: 6px 0;
            border: 1px solid var(--border-subtle);
            white-space: pre-wrap;
        }
        .highlight { color: #f87171; font-weight: bold; }
        .evidence-quote { background: #132338; border-left: 3px solid #38bdf8; padding: 8px 12px; margin: 6px 0; border-radius: 0 4px 4px 0; font-size: 12px; color: #bae6fd; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div>
                <h1 class="title">AgentTrust Reliability Evaluation Report</h1>
                <div class="subtitle">Multilingual AI Reliability Evaluator &bull; Evidence-backed reliability diagnostics and reproducibility report</div>
            </div>
            <div style="text-align: right;">
                {% if run.is_demo %}
                <span class="badge badge-demo">DEMO / SIMULATION RUN</span>
                {% else %}
                <span class="badge badge-pass">PRODUCTION EVALUATION</span>
                {% endif %}
                <div style="margin-top: 6px; font-size: 12px; color: var(--text-secondary);">
                    Run ID: <span class="tag">{{ run.id }}</span>
                </div>
            </div>
        </div>

        <!-- 1. Executive Summary -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">01.</span> Executive Summary</h2>
            </div>
            <div class="callout">
                <strong>Evaluation Assessment:</strong> 
                This evaluation tested AI Agent <strong>{{ run.agent_name }} (v{{ run.agent_version }})</strong> against benchmark dataset <strong>{{ run.dataset_name }} (v{{ run.dataset_version or '1.0.0' }})</strong>.
                Across <strong>{{ metrics.total_tests }}</strong> test cases, the agent attained a <strong>Composite Reliability Score of {{ "%.1f"|format(metrics.composite_score * 100) }}%</strong> with an overall pass rate of <strong>{{ "%.1f"|format(metrics.overall_pass_rate * 100) }}%</strong>.
                <br><br>
                <em>Methodological Note:</em> This score is an empirical, reproducible diagnostic measurement calculated specifically for this configured evaluation profile and dataset. It does not certify absolute or universal system trustworthiness.
            </div>
        </div>

        <!-- 2. Run Information -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">02.</span> Run Information</h2>
            </div>
            <table>
                <tbody>
                    <tr><td><strong>Run Identifier</strong></td><td><span class="tag">{{ run.id }}</span></td><td><strong>Execution Status</strong></td><td><span class="badge {% if run.status == 'COMPLETED' %}badge-pass{% else %}badge-warning{% endif %}">{{ run.status }}</span></td></tr>
                    <tr><td><strong>Agent Under Test</strong></td><td>{{ run.agent_name }}</td><td><strong>Agent Version</strong></td><td><code>{{ run.agent_version }}</code></td></tr>
                    <tr><td><strong>Benchmark Dataset</strong></td><td>{{ run.dataset_name }}</td><td><strong>Dataset Version</strong></td><td><code>{{ run.dataset_version or '1.0.0' }}</code></td></tr>
                    <tr><td><strong>Evaluated At</strong></td><td>{{ run.completed_at or 'In Progress' }}</td><td><strong>Total Duration</strong></td><td>{{ run.duration_seconds or '-' }} seconds</td></tr>
                </tbody>
            </table>
        </div>

        <!-- 3. Overall Metrics -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">03.</span> Overall Metrics</h2>
            </div>
            <div class="grid-kpi">
                <div class="card" style="border-color: #0284c7;">
                    <div class="card-label">Composite Reliability</div>
                    <div class="card-value" style="color: var(--accent-primary);">{{ "%.1f"|format(metrics.composite_score * 100) }}%</div>
                    <div class="card-desc">Weighted: 30/30/15/15/10</div>
                </div>
                <div class="card">
                    <div class="card-label">Correctness Rate</div>
                    <div class="card-value">{{ "%.1f"|format(metrics.correctness.score * 100) }}%</div>
                    <div class="card-desc">Pass rate: {{ "%.1f"|format(metrics.correctness.pass_rate * 100) }}%</div>
                </div>
                <div class="card">
                    <div class="card-label">Grounding Score</div>
                    <div class="card-value">{{ "%.1f"|format(metrics.grounding.score * 100) }}%</div>
                    <div class="card-desc">{{ metrics.grounding.supported }} supported / {{ metrics.grounding.contradicted }} contradicted</div>
                </div>
                <div class="card">
                    <div class="card-label">Citation Accuracy</div>
                    <div class="card-value">{{ "%.1f"|format(metrics.citation.score * 100) }}%</div>
                    <div class="card-desc">{{ metrics.citation.valid }} valid citations</div>
                </div>
                <div class="card">
                    <div class="card-label">Translation Fidelity</div>
                    <div class="card-value">{{ "%.1f"|format(metrics.translation.score * 100) }}%</div>
                    <div class="card-desc">{{ "%.1f"|format(metrics.translation.major_drift_rate * 100) }}% major drift</div>
                </div>
                <div class="card">
                    <div class="card-label">Trajectory Integrity</div>
                    <div class="card-value">{{ "%.1f"|format((metrics.trajectory.score if metrics.trajectory else 1.0) * 100) }}%</div>
                    <div class="card-desc">{{ metrics.trajectory.loop_warnings if metrics.trajectory else 0 }} loop warnings</div>
                </div>
            </div>
        </div>

        <!-- 4. Language Breakdown -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">04.</span> Multilingual Breakdown</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Language</th>
                        <th>Tests</th>
                        <th>Pass Rate</th>
                        <th>Composite</th>
                        <th>Correctness</th>
                        <th>Grounding</th>
                        <th>Citations</th>
                        <th>Translation</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lang, data in metrics.language_breakdown.items() %}
                    <tr>
                        <td><strong>{{ lang|upper }}</strong></td>
                        <td>{{ data.total_tests }}</td>
                        <td>{{ "%.1f"|format(data.pass_rate * 100) }}%</td>
                        <td><strong>{{ "%.1f"|format(data.composite_score * 100) }}%</strong></td>
                        <td>{{ "%.1f"|format(data.correctness_score * 100) }}%</td>
                        <td>{{ "%.1f"|format(data.grounding_score * 100) }}%</td>
                        <td>{{ "%.1f"|format(data.citation_score * 100) }}%</td>
                        <td>{{ "%.1f"|format(data.translation_score * 100) if data.translation_score is not none else "N/A" }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 5. Failure Summary -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">05.</span> Failure Summary & Severity Breakdown</h2>
            </div>
            <div class="grid-kpi">
                <div class="card">
                    <div class="card-label" style="color: var(--accent-danger);">Critical Severity</div>
                    <div class="card-value" style="color: var(--accent-danger);">{{ metrics.severity_breakdown.CRITICAL or 0 }}</div>
                    <div class="card-desc">Direct contradictions & fatal fact errors</div>
                </div>
                <div class="card">
                    <div class="card-label" style="color: #fb923c;">High Severity</div>
                    <div class="card-value" style="color: #fb923c;">{{ metrics.severity_breakdown.HIGH or 0 }}</div>
                    <div class="card-desc">Major unsupported claims & drifts</div>
                </div>
                <div class="card">
                    <div class="card-label" style="color: var(--accent-warning);">Medium Severity</div>
                    <div class="card-value" style="color: var(--accent-warning);">{{ metrics.severity_breakdown.MEDIUM or 0 }}</div>
                    <div class="card-desc">Citation mismatches & minor drifts</div>
                </div>
                <div class="card">
                    <div class="card-label">Low Severity</div>
                    <div class="card-value">{{ metrics.severity_breakdown.LOW or 0 }}</div>
                    <div class="card-desc">Minor formatting & trajectory warnings</div>
                </div>
            </div>
        </div>

        <!-- 6. Critical Failures -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">06.</span> Critical & High Priority Failures</h2>
            </div>
            {% for item in critical_failures %}
            <div class="failure-item">
                <h4>
                    <span>Test <code>{{ item.test_case.external_id }}</code> ({{ item.test_case.language|upper }})</span>
                    <span class="badge badge-fail">{{ item.evaluation.severity }}</span>
                </h4>
                <div><strong>Question:</strong> {{ item.test_case.question }}</div>
                <div style="margin-top: 6px;"><strong>Agent Answer:</strong></div>
                <div class="code-box">{{ item.final_answer }}</div>
                <div style="margin-top: 6px;"><strong>Expected Statutory Fact:</strong></div>
                <div class="code-box">{{ item.test_case.expected_answer }}</div>
                <div style="margin-top: 6px;"><strong>Root Cause Diagnostic:</strong></div>
                <div class="evidence-quote">
                    {{ item.evaluation.correctness_reason or item.evaluation.grounding_reason or item.evaluation.citation_reason or item.evaluation.translation_reason }}
                </div>
            </div>
            {% else %}
            <p style="color: var(--accent-success); font-size: 13px;">✓ Zero Critical or High-severity failures detected in this run.</p>
            {% endfor %}
        </div>

        <!-- 7. Evidence Diagnostics -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">07.</span> Evidence Grounding Diagnostics</h2>
            </div>
            <div class="callout">
                Claims are extracted and validated against verified corpus documents. Statements are classified strictly as 
                <strong>SUPPORTED</strong>, <strong>UNSUPPORTED</strong>, or <strong>CONTRADICTED</strong>. Unsupported claims are not blindly assumed to be hallucinations.
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Extracted Claim</th>
                        <th>Classification</th>
                        <th>Evidence Grounding Diagnostic</th>
                    </tr>
                </thead>
                <tbody>
                    {% for r in results %}
                    {% if r.evaluation_result.grounding_status != 'SUPPORTED' %}
                    <tr>
                        <td><code>{{ r.test_case.external_id }}</code></td>
                        <td>{{ r.final_answer[:120] }}...</td>
                        <td>
                            <span class="badge {% if r.evaluation_result.grounding_status == 'CONTRADICTED' %}badge-fail{% else %}badge-warning{% endif %}">
                                {{ r.evaluation_result.grounding_status }}
                            </span>
                        </td>
                        <td style="font-size: 12px; color: #cbd5e1;">{{ r.evaluation_result.grounding_reason or 'No grounding explanation available.' }}</td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 8. Translation Analysis -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">08.</span> Multilingual Translation Fidelity</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Language</th>
                        <th>Status</th>
                        <th>Fidelity Score</th>
                        <th>Drift Assessment</th>
                    </tr>
                </thead>
                <tbody>
                    {% for r in results %}
                    {% if r.language != 'en' %}
                    <tr>
                        <td><code>{{ r.test_case.external_id }}</code></td>
                        <td><strong>{{ r.language|upper }}</strong></td>
                        <td>
                            <span class="badge {% if r.evaluation_result.translation_status == 'PASS' %}badge-pass{% elif r.evaluation_result.translation_status == 'MINOR_DRIFT' %}badge-warning{% else %}badge-fail{% endif %}">
                                {{ r.evaluation_result.translation_status }}
                            </span>
                        </td>
                        <td>{{ "%.1f"|format((r.evaluation_result.translation_score or 0) * 100) }}%</td>
                        <td style="font-size: 12px; color: #cbd5e1;">{{ r.evaluation_result.translation_reason or 'Faithful back-translation to English.' }}</td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 9. Trajectory Analysis -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">09.</span> Observable Trajectory & Tool Execution</h2>
            </div>
            <div class="callout">
                Trajectory analysis evaluates observable behavioral steps, tool calls, and retrieval protocols. Hidden model chain-of-thought is never evaluated or stored.
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Trajectory Status</th>
                        <th>Score</th>
                        <th>Latency</th>
                        <th>Diagnostic Details</th>
                    </tr>
                </thead>
                <tbody>
                    {% for r in results[:10] %}
                    <tr>
                        <td><code>{{ r.test_case.external_id }}</code></td>
                        <td>
                            <span class="badge {% if r.evaluation_result.trajectory_status == 'PASS' %}badge-pass{% else %}badge-warning{% endif %}">
                                {{ r.evaluation_result.trajectory_status or 'PASS' }}
                            </span>
                        </td>
                        <td>{{ "%.1f"|format((r.evaluation_result.trajectory_score or 1.0) * 100) }}%</td>
                        <td>{{ r.latency_ms or 0 }} ms</td>
                        <td style="font-size: 12px; color: #cbd5e1;">
                            {% if r.evaluation_result.trajectory_status == 'LOOP_WARNING' %}
                            Warning: Repeated tool invocation pattern detected.
                            {% else %}
                            Observable tool sequence and completion executed normally.
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 10. Regression Analysis -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">10.</span> Regression Analysis</h2>
            </div>
            <div class="callout">
                To identify regressions or improvements, compare this evaluation against any prior baseline run using the 
                <strong>Before / After Comparisons</strong> module (<code>/compare?before=BASELINE&after={{ run.id }}</code>).
            </div>
        </div>

        <!-- 11. Test-level Details -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">11.</span> Test-Level Execution Catalog</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Lang</th>
                        <th>Overall</th>
                        <th>Correctness</th>
                        <th>Grounding</th>
                        <th>Citations</th>
                        <th>Translation</th>
                        <th>Latency</th>
                    </tr>
                </thead>
                <tbody>
                    {% for r in results %}
                    <tr>
                        <td><code>{{ r.test_case.external_id }}</code></td>
                        <td>{{ r.language|upper }}</td>
                        <td>
                            <span class="badge {% if r.evaluation_result.overall_status == 'PASS' %}badge-pass{% else %}badge-fail{% endif %}">
                                {{ r.evaluation_result.overall_status }}
                            </span>
                        </td>
                        <td>{{ "%.1f"|format((r.evaluation_result.correctness_score or 0) * 100) }}%</td>
                        <td>{{ "%.1f"|format((r.evaluation_result.grounding_score or 0) * 100) }}%</td>
                        <td>{{ "%.1f"|format((r.evaluation_result.citation_score or 0) * 100) }}%</td>
                        <td>{{ "%.1f"|format((r.evaluation_result.translation_score or 0) * 100) if r.evaluation_result.translation_score is not none else "N/A" }}</td>
                        <td>{{ r.latency_ms or 0 }}ms</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 12. Methodology -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">12.</span> Evaluation Methodology</h2>
            </div>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.6;">
                AgentTrust utilizes a hybrid evaluation methodology combining deterministic fact extraction with semantic LLM evaluation:
            </p>
            <ul style="font-size: 13px; color: var(--text-secondary); line-height: 1.8;">
                <li><strong>Deterministic Fact Verification:</strong> Strict normalization and exact checking for statutory dates, numeric thresholds, sections, and authorities.</li>
                <li><strong>Semantic Verification:</strong> Structured JSON validation for semantic meaning and nuance without subjective scoring drift.</li>
                <li><strong>Evidence-Backed Grounding:</strong> Claims are mapped against retrieved evidence and classified as SUPPORTED, UNSUPPORTED, or CONTRADICTED.</li>
                <li><strong>Multilingual Back-Translation:</strong> Non-English agent responses are translated back to verify essential numeric and factual fidelity.</li>
                <li><strong>Observable Trajectory Inspection:</strong> Validates tool invocation sequences, loops, and missing retrieval calls without analyzing private chain-of-thought.</li>
                <li><strong>Composite Reliability Formula:</strong> 30% Correctness + 30% Grounding + 15% Citation + 15% Translation + 10% Trajectory (normalized when translation is N/A).</li>
            </ul>
        </div>

        <!-- 13. Limitations -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="section-num">13.</span> Scientific & Technical Limitations</h2>
            </div>
            <div class="callout callout-warning">
                <strong>Important Methodological Limitations:</strong>
                <ul style="margin: 8px 0 0 0; padding-left: 20px; line-height: 1.6;">
                    <li><strong>Non-Exhaustive Test Coverage:</strong> This evaluation tests only the specific prompts, facts, and scenarios included in the benchmark dataset. High performance does not guarantee reliability on unobserved edge cases.</li>
                    <li><strong>LLM Judge Stochasticity:</strong> Semantic evaluation uses LLM-as-a-judge with zero-temperature prompting; minor variance may exist across model updates.</li>
                    <li><strong>External Observability Dependency:</strong> Trace and citation metrics depend on the external agent providing structured tool and citation payloads. "Not provided by agent" indicates missing telemetry, not necessarily faulty reasoning.</li>
                    <li><strong>No Hidden Reasoning Inspection:</strong> Internal chain-of-thought is not audited; only observable external outputs and tool invocations are evaluated.</li>
                </ul>
            </div>
        </div>

        <!-- Footer -->
        <div style="text-align: center; font-size: 12px; color: var(--text-secondary); margin-top: 40px; border-top: 1px solid var(--border-subtle); padding-top: 20px;">
            Generated by <strong>AgentTrust: Multilingual AI Reliability Evaluator</strong> &bull; Evidence-backed reliability diagnostics for AI agents.
        </div>
    </div>
</body>
</html>
"""


class ReportGenerator:
    @staticmethod
    def generate_json_export(run_data: Dict[str, Any], results: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        payload = {
            "evaluation_platform": "AgentTrust",
            "version": "1.0.0",
            "run": run_data,
            "metrics": metrics,
            "results": results,
            "methodology": {
                "formula": "30% Correctness, 30% Grounding, 15% Citation, 15% Translation, 10% Trajectory",
                "disclaimer": "Diagnostic measurement on defined dataset and configuration; not an absolute measure of trust."
            }
        }
        return json.dumps(payload, indent=2, default=str)

    @staticmethod
    def generate_csv_export(results: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Test ID",
            "Language",
            "Overall Status",
            "Composite Score",
            "Severity",
            "Correctness Status",
            "Correctness Score",
            "Grounding Status",
            "Grounding Score",
            "Citation Status",
            "Citation Score",
            "Translation Status",
            "Translation Score",
            "Trajectory Status",
            "Latency (ms)"
        ])

        for r in results:
            ev = r.get("evaluation_result", {})
            tc = r.get("test_case", {})
            writer.writerow([
                tc.get("external_id", r.get("test_case_id")),
                r.get("language"),
                ev.get("overall_status"),
                ev.get("composite_score"),
                ev.get("severity"),
                ev.get("correctness_status"),
                ev.get("correctness_score"),
                ev.get("grounding_status"),
                ev.get("grounding_score"),
                ev.get("citation_status"),
                ev.get("citation_score"),
                ev.get("translation_status"),
                ev.get("translation_score"),
                ev.get("trajectory_status"),
                r.get("latency_ms", 0)
            ])

        return output.getvalue()

    @staticmethod
    def generate_html_report(run_data: Dict[str, Any], results: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        failures = [
            r for r in results
            if r.get("evaluation_result", {}).get("overall_status") != "PASS"
        ]
        critical_failures = [
            r for r in failures
            if r.get("evaluation_result", {}).get("severity") in ("CRITICAL", "HIGH")
        ]
        template = Template(HTML_REPORT_TEMPLATE)
        return template.render(
            run=run_data,
            metrics=metrics,
            results=results,
            failures=[
                {
                    "test_case": r.get("test_case", {}),
                    "final_answer": r.get("final_answer", ""),
                    "evaluation": r.get("evaluation_result", {})
                }
                for r in failures
            ],
            critical_failures=[
                {
                    "test_case": r.get("test_case", {}),
                    "final_answer": r.get("final_answer", ""),
                    "evaluation": r.get("evaluation_result", {})
                }
                for r in critical_failures
            ]
        )

