#!/usr/bin/env python3
"""
Command-line interface for CodeSentinel.
"""
import argparse
import sys
import os
import json
from app.services.analysis_service import AnalysisService
from app.database.db_manager import DatabaseManager
from app.reports.report_generator import ReportGenerator
from app.core.analyzer.scoring import ScoringEngine
from app.ui.theme import APP_NAME, APP_TAGLINE, APP_DATA_DIR


def main():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} CLI - {APP_TAGLINE}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a project")
    analyze_parser.add_argument("path", help="Project path")
    analyze_parser.add_argument("--output", "-o", help="Output report file")

    report_parser = subparsers.add_parser("report", help="Generate report")
    report_parser.add_argument("path", help="Project path")
    report_parser.add_argument("--format", choices=["html", "json", "csv"], default="html")
    report_parser.add_argument("--output", "-o", required=True)

    gate_parser = subparsers.add_parser("gate", help="Run quality gate")
    gate_parser.add_argument("path", help="Project path")
    gate_parser.add_argument("--threshold", type=int, default=70, help="Minimum quality score")

    args = parser.parse_args()

    db_path = os.path.join(os.path.expanduser("~"), APP_DATA_DIR, "codesentinel.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = DatabaseManager(db_path)
    db.initialize()
    service = AnalysisService(db)

    if args.command == "analyze":
        run = service.analyze_project(args.path)
        print("Scan complete.")
        print(f"Quality Score: {run.quality_score}")
        print(f"Grade: {ScoringEngine().grade(run.quality_score)}")
        print(f"Security: {run.security_score}")
        print(f"Complexity: {run.complexity_score}")
        print(f"Maintainability: {run.maintainability_score}")
        print(f"Technical Debt: {run.technical_debt}h")
        if args.output:
            data = {
                "project_name": os.path.basename(args.path),
                "project_path": args.path,
                "quality_score": run.quality_score,
                "grade": ScoringEngine().grade(run.quality_score),
                "security": run.security_score,
                "complexity": run.complexity_score,
                "maintainability": run.maintainability_score,
                "duplication": run.duplication_score,
                "technical_debt": run.technical_debt,
                "issues": [],
            }
            gen = ReportGenerator(data)
            if args.output.endswith(".json"):
                gen.generate_json(args.output)
            elif args.output.endswith(".csv"):
                gen.generate_csv(args.output)
            else:
                gen.generate_html(args.output)
            print(f"Report saved to {args.output}")

    elif args.command == "report":
        print("Report generation from existing analysis is available through the analyze command.")

    elif args.command == "gate":
        run = service.analyze_project(args.path)
        if run.quality_score >= args.threshold:
            print(f"Release Gate PASSED (Score: {run.quality_score} >= {args.threshold})")
            sys.exit(0)
        else:
            print(f"Release Gate FAILED (Score: {run.quality_score} < {args.threshold})")
            sys.exit(1)


if __name__ == "__main__":
    main()
