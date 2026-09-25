import json
import csv
import io
from typing import Dict, Any, List
from jinja2 import Template

HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AgentTrust Reliability Report - Run {{ run.id[:8] }}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 32px; }
        .container { max-width: 1100px; margin: 0 auto; }
        .header { border-bottom: 1px solid #334155; padding-bottom: 24px; margin-bottom: 32px; }
        .title { font-size: 28px; font-weight: 700; color: #38bdf8; margin: 0 0 8px 0; }
        .subtitle { font-size: 14px; color: #94a3b8; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; }
        .card-label { font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; }
        .card-value { font-size: 32px; font-weight: 700; margin-top: 8px; color: #f8fafc; }
        .badge { display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }
        .badge-pass { background: #065f46; color: #34d399; }
        .badge-fail { background: #7f1d1d; color: #f87171; }
        .badge-warning { background: #78350f; color: #fbbf24; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; background: #1e293b; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }
        th { background: #0f172a; color: #94a3b8; font-weight: 600; }
        .section-title { font-size: 20px; font-weight: 600; margin-top: 40px; margin-bottom: 16px; color: #e2e8f0; }
        .drilldown { background: #1e293b; border-left: 4px solid #f87171; padding: 16px; margin-bottom: 16px; border-radius: 4px; }
        .tag { font-family: monospace; background: #0f172a; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">AgentTrust Reliability Evaluation Report</h1>
            <div class="subtitle">
                Run ID: <span class="tag">{{ run.id }}</span> |
                Agent: <strong>{{ run.agent_name }} (v{{ run.agent_version }})</strong> |
                Dataset: <strong>{{ run.dataset_name }}</strong> |
                Evaluated: {{ run.completed_at or "In Progress" }}
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-label">Composite Reliability</div>
                <div class="card-value" style="color: #38bdf8;">{{ "%.1f"|format(metrics.composite_score * 100) }}%</div>
            </div>
            <div class="card">
                <div class="card-label">Correctness Rate</div>
                <div class="card-value">{{ "%.1f"|format(metrics.correctness.score * 100) }}%</div>
            </div>
            <div class="card">
                <div class="card-label">Grounding Score</div>
                <div class="card-value">{{ "%.1f"|format(metrics.grounding.score * 100) }}%</div>
            </div>
            <div class="card">
                <div class="card-label">Citation Accuracy</div>
                <div class="card-value">{{ "%.1f"|format(metrics.citation.score * 100) }}%</div>
            </div>
            <div class="card">
                <div class="card-label">Translation Fidelity</div>
                <div class="card-value">{{ "%.1f"|format(metrics.translation.score * 100) }}%</div>
            </div>
        </div>

        <div class="section-title">Language-Level Breakdown</div>
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
                    <td>{{ "%.1f"|format(data.composite_score * 100) }}%</td>
                    <td>{{ "%.1f"|format(data.correctness_score * 100) }}%</td>
                    <td>{{ "%.1f"|format(data.grounding_score * 100) }}%</td>
                    <td>{{ "%.1f"|format(data.citation_score * 100) }}%</td>
                    <td>{{ "%.1f"|format(data.translation_score * 100) if data.translation_score is not none else "N/A" }}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="section-title">Failure Drill-Downs (Diagnostics)</div>
        {% for item in failures %}
        <div class="drilldown">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong>Test {{ item.test_case.external_id }} ({{ item.test_case.language|upper }})</strong>
                <span class="badge badge-fail">{{ item.evaluation.severity }} SEVERITY</span>
            </div>
            <p><strong>Question:</strong> {{ item.test_case.question }}</p>
            <p><strong>Agent Answer:</strong> <em>{{ item.final_answer }}</em></p>
            <p><strong>Diagnostic Reason:</strong> {{ item.evaluation.correctness_reason or item.evaluation.grounding_reason or item.evaluation.citation_reason }}</p>
        </div>
        {% else %}
        <p style="color: #94a3b8;">No failures detected in this evaluation run.</p>
        {% endfor %}
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
            "results": results
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
        template = Template(HTML_REPORT_TEMPLATE)
        return template.render(
            run=run_data,
            metrics=metrics,
            failures=[
                {
                    "test_case": r.get("test_case", {}),
                    "final_answer": r.get("final_answer", ""),
                    "evaluation": r.get("evaluation_result", {})
                }
                for r in failures
            ]
        )
