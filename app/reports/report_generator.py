"""
Generate reports in various formats.
"""
import json
import csv
import os
import html
from typing import Dict, List
from datetime import datetime
from app.ui.theme import APP_NAME, APP_TAGLINE, APP_VERSION


class ReportGenerator:
    def __init__(self, analysis_data: Dict):
        self.data = analysis_data

    def generate_html(self, output_path: str):
        project_name = html.escape(str(self.data.get("project_name", "Unknown")))
        project_path = html.escape(str(self.data.get("project_path", "Unknown")))
        quality_score = html.escape(str(self.data.get("quality_score", 0)))
        grade = html.escape(str(self.data.get("grade", "N/A")))
        maintainability = html.escape(str(self.data.get("maintainability", 0)))
        complexity = html.escape(str(self.data.get("complexity", 0)))
        security = html.escape(str(self.data.get("security", 0)))
        duplication = html.escape(str(self.data.get("duplication", 0)))
        technical_debt = html.escape(str(self.data.get("technical_debt", 0)))
        template = """<!DOCTYPE html>
<html>
<head>
    <title>""" + APP_NAME + """ Report</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #101112; color: #f4f1e8; margin: 0; padding: 24px; }
        .container { max-width: 1040px; margin: auto; padding: 30px; background: #181a17; border: 1px solid #30342d; border-radius: 8px; }
        h1 { color: #39d98a; margin-bottom: 5px; }
        h2 { color: #f4f1e8; border-bottom: 1px solid #30342d; padding-bottom: 8px; margin-top: 28px; }
        .score { font-size: 48px; font-weight: bold; color: #39d98a; }
        .grade { font-size: 24px; color: #ffb84d; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-label { color: #a8ad9f; font-size: 12px; }
        .metric-value { font-size: 20px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th { background: #151713; color: #f4f1e8; padding: 10px; text-align: left; }
        td { padding: 8px 10px; border-bottom: 1px solid #30342d; }
        tr:hover { background: #20231f; }
        .severity-critical { color: #ff5c7a; font-weight: bold; }
        .severity-high { color: #ff9f5a; }
        .severity-medium { color: #ffd166; }
        .severity-low { color: #39d98a; }
        .footer { margin-top: 30px; color: #747b70; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>""" + APP_NAME + """ Quality Report</h1>
        <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>

        <h2>Project Overview</h2>
        <p><strong>Project:</strong> """ + project_name + """</p>
        <p><strong>Path:</strong> """ + project_path + """</p>

        <h2>Quality Score</h2>
        <div class="score">""" + quality_score + """/100</div>
        <div class="grade">Grade: """ + grade + """</div>

        <h2>Metrics</h2>
        <div class="metric">
            <div class="metric-label">Maintainability</div>
            <div class="metric-value">""" + maintainability + """</div>
        </div>
        <div class="metric">
            <div class="metric-label">Complexity</div>
            <div class="metric-value">""" + complexity + """</div>
        </div>
        <div class="metric">
            <div class="metric-label">Security</div>
            <div class="metric-value">""" + security + """</div>
        </div>
        <div class="metric">
            <div class="metric-label">Duplication</div>
            <div class="metric-value">""" + duplication + """</div>
        </div>
        <div class="metric">
            <div class="metric-label">Technical Debt</div>
            <div class="metric-value">""" + technical_debt + """h</div>
        </div>

        <h2>Findings</h2>
        <table>
            <tr><th>Severity</th><th>Type</th><th>File</th><th>Line</th><th>Message</th></tr>
            """ + self._render_issues_table(self.data.get("issues", [])) + """
        </table>

        <div class="footer">
            <p>""" + APP_NAME + """ v""" + APP_VERSION + """ - """ + APP_TAGLINE + """</p>
        </div>
    </div>
</body>
</html>"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)

    def generate_pdf(self, output_path: str):
        """Generate PDF report using WeasyPrint."""
        try:
            from weasyprint import HTML
            temp_html = output_path + ".temp.html"
            self.generate_html(temp_html)
            HTML(temp_html).write_pdf(output_path)
            os.remove(temp_html)
        except ImportError:
            raise ImportError("WeasyPrint is required for PDF generation. Install with: pip install weasyprint")

    def _render_issues_table(self, issues: List[Dict]) -> str:
        rows = []
        for issue in issues:
            severity_class = f"severity-{issue.get('severity', 'low').lower()}"
            rows.append(
                f'<tr>'
                f'<td class="{severity_class}">{html.escape(str(issue.get("severity", "")))}</td>'
                f'<td>{html.escape(str(issue.get("type", "")))}</td>'
                f'<td>{html.escape(str(issue.get("file_path", "")))}</td>'
                f'<td>{html.escape(str(issue.get("line", "")))}</td>'
                f'<td>{html.escape(str(issue.get("message", "")))}</td>'
                f'</tr>'
            )
        return "\n".join(rows) if rows else '<tr><td colspan="5">No findings found</td></tr>'

    def generate_json(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, default=str)

    def generate_csv(self, output_path: str):
        issues = self.data.get("issues", [])
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Severity", "Type", "Category", "File", "Line", "Message", "Recommendation"])
            for issue in issues:
                writer.writerow([
                    issue.get("severity", ""),
                    issue.get("type", ""),
                    issue.get("category", ""),
                    issue.get("file_path", ""),
                    issue.get("line", ""),
                    issue.get("message", ""),
                    issue.get("recommendation", ""),
                ])
