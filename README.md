# Credit Card Data Discovery System

An AI-powered multi-agent system for detecting, validating, and classifying credit card data exposure risks in file systems.

## Features

- **Automated Discovery**: Scans directories for potential credit card data
- **Smart Detection**: Uses regex patterns to identify card numbers
- **Luhn Validation**: Validates card numbers using the Luhn algorithm
- **AI Context Analysis**: LLM-powered analysis of file context and security posture
- **Risk Classification**: Automatic risk scoring (Critical/High/Medium/Low/False Positive)
- **Compliance Reporting**: Generates PCI DSS compliance reports

## Architecture

Multi-agent workflow powered by LangGraph:

```
Discovery → Detection → Validation → Context Analysis → Risk Classification → Reporting
```

### Agents

1. **Discovery Agent**: Scans folders and identifies files
2. **Detection Agent**: Extracts potential card numbers using regex
3. **Validation Agent**: Validates cards with Luhn algorithm
4. **Context Agent**: AI analyzes file type, environment, and security status
5. **Risk Agent**: Classifies findings by risk level
6. **Reporting Agent**: Generates comprehensive security reports

## Installation

### Prerequisites

- Python 3.8+
- Ollama with Llama3 model

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/credit-card-discovery.git
cd credit-card-discovery
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Ollama and pull Llama3:
```bash
# Install Ollama from https://ollama.com/download
ollama pull llama3
```

## Usage

Run the scanner on a directory:

```bash
python main.py
```

By default, it scans the `test_data/` folder. To scan a different directory, modify `main.py`:

```python
initial_state = {
    "folder_path": "your/target/directory",
    ...
}
```

## Output

The system generates two files in the `outputs/` directory:

- `findings.json`: Detailed findings with risk classification
- `report.txt`: Human-readable security report

## Example Output

```json
[
  {
    "file": "test_data/logs.log",
    "card_number": "4111111111111111",
    "context_analysis": "...",
    "risk_level": "Critical"
  }
]
```

## Risk Levels

- **Critical**: Unencrypted cards in logs or publicly accessible files
- **High**: Card data accessible to broad user groups
- **Medium**: Test data in production environments
- **Low**: Masked or tokenized card numbers
- **False Positive**: Known test cards in test environments

## Project Structure

```
.
├── agents/
│   ├── discovery_agent.py
│   ├── detection_agent.py
│   ├── validation_agent.py
│   ├── context_agent.py
│   ├── risk_agent.py
│   └── reporting_agent.py
├── tools/
│   ├── luhn_tool.py
│   └── false_positive_checker.py
├── workflow/
│   └── graph.py
├── test_data/
├── outputs/
├── config.py
├── main.py
└── requirements.txt
```

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Ollama](https://ollama.com/) and Llama3
- Luhn algorithm for card validation


---

## 🚀 PHASE 3 UPGRADES - AUTONOMOUS COMPLIANCE SYSTEM

### New Features

#### 1️⃣ Presidio Detection (Enterprise-Grade PII)
- Replaced regex with Microsoft Presidio
- Built-in credit card detection with confidence scoring
- Better false positive reduction

#### 2️⃣ Auto-Remediation Agent
- Automatically masks critical findings
- Replaces card numbers with `****1234` format
- Logs remediation status in findings

#### 3️⃣ CSV Export + Dashboard Integration
- Export findings to CSV
- Import to Google Sheets
- Create dashboards in Looker Studio (free)
- Or use Excel/Power BI

### Updated Architecture

```
discovery → detection (Presidio) → validation → context → risk → remediation → reporting
```

### Quick Start

See [SETUP.md](SETUP.md) for full installation guide.

```bash
py -m pip install -r requirements.txt
py -m spacy download en_core_web_sm
py main.py
py export_csv.py
```

Then upload CSV to Google Sheets and create dashboards in Looker Studio.

### What Changed

| Component | Before | After |
|-----------|--------|-------|
| Detection | Regex patterns | Presidio AI |
| Remediation | Manual | Automatic masking |

This is now an **Autonomous PCI DSS Compliance Discovery Agent**.
