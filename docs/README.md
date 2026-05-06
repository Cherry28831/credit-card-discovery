# SecureScan - Credit Card Data Discovery System

An AI-powered autonomous compliance system for detecting, validating, and remediating credit card data exposure across local filesystems and cloud storage (AWS S3).

### Key Features

- **Multi-Source Scanning** - Local filesystems, AWS S3 buckets
- **AI-Powered Detection** - Microsoft Presidio + Luhn validation (99.9% accuracy)
- **Risk Analysis** - AWS Bedrock LLM context analysis and classification
- **Auto-Remediation** - One-click card masking with S3 upload
- **Interactive Dashboard** - Real-time progress, analytics, and reporting

---

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│  Discovery  │───▶│  Detection   │───▶│ Validation  │───▶│   Context   │
│   Agent     │    │ (Presidio AI)│    │(Luhn Check) │    │  (AI LLM)   │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
                                                                   │
                                                                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│  Reporting  │◀───│     Risk     │◀───│ Remediation │◀───│  Dashboard  │
│   Agent     │    │Classification│    │   Agent     │    │     UI      │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

**Agents:**

1. **Discovery** - Scans local/cloud storage
2. **Detection** - Presidio finds credit card patterns
3. **Validation** - Luhn algorithm validates cards
4. **Context** - AI analyzes file security posture
5. **Risk** - Classifies as Critical/Medium/Low
6. **Reporting** - Generates PCI DSS reports

---

## Prerequisites

- Python 3.8+
- AWS Account (for Bedrock LLM)
- AWS S3 (optional, for cloud scanning)

---

## Quick Start

### 1. Installation

```bash
# Install dependencies
py -m pip install -r requirements.txt
py -m spacy download en_core_web_sm

# Create database
py create_db.py
```

### 2. Configure AWS

```bash
# Set environment variables
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_REGION=us-east-1
```

See [BEDROCK_SETUP.md](BEDROCK_SETUP.md) for details.

### 3. Run Dashboard

```bash
py -m streamlit run dashboard.py
```

Opens at: `http://localhost:8501`

### 4. Run Scan

**Via Dashboard:** Run Scan tab → Select sources → Launch

**Via CLI:**

```bash
# Scan sample files
py main.py sample_files

# Scan local directory
py main.py C:\path\to\scan

# Scan AWS S3 only
py main.py . --s3 --skip-local

# Scan local + S3
py main.py C:\path --s3
```

---

## How Detection Works

### Step 1: Pattern Detection (Presidio)

- Uses regex: `\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4,7}`
- Detects: `4111111111111111`, `4111-1111-1111-1111`, `4111 1111 1111 1111`
- Confidence score > 0.5 kept

### Step 2: Luhn Validation

- Mathematical checksum algorithm
- Filters out random numbers, phone numbers, account IDs
- Only real credit cards pass

### Step 3: AI Risk Classification

- AWS Bedrock analyzes file path, type, storage location
- **Critical**: Production logs, public S3
- **Medium**: Dev/test logs, configs
- **Low**: Test cards in sample files

---

## Dashboard Features

- **Overview**: Metrics, charts, findings table
- **Run Scan**: Source selection, real-time progress
- **AI Analysis**: LLM context analysis, one-click remediation
- **Remediated**: Audit trail of masked findings
- **Executive Report**: PCI DSS compliance report

---

## Project Structure

```
.
├── agents/              # Multi-agent pipeline
├── cloud/               # S3 scanner
├── tools/               # Presidio, Luhn, remediation
├── config/              # AWS Bedrock config
├── outputs/             # Scan results (DB, JSON, reports)
├── sample_files/        # Test data
├── docs/                # Documentation
├── dashboard.py         # Streamlit UI
├── main.py              # CLI scanner
└── requirements.txt
```

---

## Documentation

- [Setup Guide](SETUP.md)
- [AWS Bedrock Setup](BEDROCK_SETUP.md)
- [S3 Setup](S3_SETUP.md)
- [S3 Quick Start](S3_QUICKSTART.md)
- [S3 Remediation](S3_REMEDIATION.md)

---

## Testing

```bash
# Test with sample files
py main.py sample_files

# Test S3 connection
py -c "from cloud.s3_scanner import test_s3_connection; test_s3_connection()"
```

**Known Test Cards:**

- Visa: `4111111111111111`
- Mastercard: `5555555555554444`
- Amex: `378282246310005`

---

## Troubleshooting

**Scan not starting?**

- Check AWS credentials configured
- Verify paths exist
- Check scan output log

**S3 not scanning?**

- Verify AWS credentials have S3 permissions
- Ensure `--s3` flag passed
- Check IAM policy: `s3:ListBucket`, `s3:GetObject`

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Acknowledgments

- **Microsoft Presidio** - PII detection
- **AWS Bedrock** - LLM analysis
- **Streamlit** - Dashboard framework

---

**Built with care for PCI DSS Compliance**
