# CodeSentinel - Code Quality Workbench

CodeSentinel is a desktop application for scanning Python projects, reviewing code quality findings, and exporting evidence-ready reports. It detects code smells, security issues, duplication, complexity hotspots, and maintainability risks.

## Features

- Project selection and scanning
- AST-based parsing for Python
- Cyclomatic complexity and nesting depth analysis
- Code smell detection
- Security pattern detection
- Duplicate code detection
- Maintainability index and technical debt estimation
- Quality score and release grade
- Dashboard with charts and priority findings
- Findings explorer with filtering
- File inventory and scan history
- Release gate settings
- HTML, JSON, CSV, and PDF report generation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI

```bash
python -m app.main
```

### CLI

```bash
python -m cli.cli analyze /path/to/project
python -m cli.cli gate /path/to/project --threshold 70
python -m cli.cli analyze /path/to/project --output report.html
```

## License

MIT
