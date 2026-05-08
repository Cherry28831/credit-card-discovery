# SecureScan - Credit Card Data Discovery System

An AI-powered autonomous compliance system for detecting, validating, and remediating credit card data exposure across local filesystems, cloud storage (AWS S3), PDFs, and images.

### Key Features

- **Multi-Source Scanning** - Local filesystems, AWS S3 buckets, PDFs, images
- **OCR Support** - Extract text from PDFs and images (PNG, JPG, TIFF, etc.)
- **AI-Powered Detection** - Microsoft Presidio + Luhn validation (99.9% accuracy)
- **Cardholder Data Detection** - CVV, expiry dates, cardholder names, PINs, track data
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
- Tesseract OCR (optional, for PDF/image scanning)

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

### 2. Install Tesseract OCR (Optional - for PDF/Image scanning)

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH or update `tools/ocr_tool.py` line 8:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**Linux:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Note:** Without Tesseract, text-based PDFs will still work, but scanned PDFs and images will be skipped.

### 2. Configure AWS

```bash
# Set environment variables
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_REGION=us-east-1
```

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

### Supported File Types

- **Text files**: `.txt`, `.log`, `.csv`, `.json`, `.xml`, `.sql`, `.ini`, `.conf`, etc.
- **PDFs**: `.pdf` (text-based and scanned/image PDFs via OCR)
- **Images**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.gif` (via OCR)

### Step 1: Pattern Detection (Presidio)

- Uses regex: `\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4,7}`
- Detects: `4111111111111111`, `4111-1111-1111-1111`, `4111 1111 1111 1111`
- Confidence score > 0.5 kept

### Step 1.5: Cardholder Data Detection

- **CVV/CVC**: 3-4 digit security codes (labeled or near card context)
- **Expiry Dates**: MM/YY, MM/YYYY formats (labeled or near card context)
- **Cardholder Names**: Person names near card-related keywords using NER
- **PIN Codes**: 4-6 digit codes (only when explicitly labeled)
- **Track Data**: Magnetic stripe data (Track 1 & 2 formats)

### Step 2: Luhn Validation

- Mathematical checksum algorithm
- Filters out random numbers, phone numbers, account IDs
- Only real credit cards pass

### Step 3: AI Risk Classification

- AWS Bedrock analyzes file path, type, storage location
- Considers additional cardholder data found (CVV, expiry, names)
- **Critical**: Production logs, public S3, full cardholder data
- **Medium**: Dev/test logs, configs, partial data
- **Low**: Test cards in sample files

---

## Cardholder Data Detected

Beyond credit card numbers, the system detects:

- **CVV/CVC Codes**: 3-4 digit security codes
- **Expiry Dates**: MM/YY or MM/YYYY formats  
- **Cardholder Names**: Using NLP entity recognition
- **PIN Codes**: When explicitly labeled
- **Track Data**: Magnetic stripe data (Track 1 & 2)

All findings are included in the AI analysis and risk assessment.

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
├── tools/               # Presidio, Luhn, OCR, remediation
│   ├── ocr_tool.py      # PDF/image text extraction
│   ├── presidio_tool.py # Credit card detection
│   ├── cardholder_data_tool.py # CVV, expiry, names detection
│   ├── luhn_tool.py     # Card validation
│   └── remediation.py   # Card masking
├── config/              # AWS Bedrock config
├── outputs/             # Scan results (DB, JSON, reports)
├── sample_files/        # Test data (includes PDFs)
├── docs/                # Documentation
├── dashboard.py         # Streamlit UI
├── main.py              # CLI scanner
└── requirements.txt
```

---

## Documentation

- [Setup Guide](SETUP.md)

---

## Testing

```bash
# Test with sample files (includes PDFs)
py main.py sample_files

# Test S3 connection
py -c "from cloud.s3_scanner import test_s3_connection; test_s3_connection()"
```

**Sample Files Include:**
- Text files with test cards
- **invoice_2024_001.pdf** - Invoice with card payment details
- **payment_receipt_batch.pdf** - Batch receipt with 5 test cards

**Known Test Cards:**

- Visa: `4111111111111111`, `4532148803436467`
- Mastercard: `5555555555554444`, `5425233430109903`
- Amex: `378282246310005`, `378282246310005`
- Discover: `6011111111111117`

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

**OCR not working?**

- Install Tesseract OCR (see installation section)
- Verify Tesseract is in PATH or update `tools/ocr_tool.py`
- Text-based PDFs work without Tesseract
- For scanned PDFs/images, Tesseract is required

**Poor OCR accuracy?**

- Ensure source PDFs/images are high quality
- Increase DPI in `tools/ocr_tool.py` line 35: `dpi=300` → `dpi=600`
- OCR works best with clear, high-contrast text

---

## License

MIT License - See [LICENSE](LICENSE)
