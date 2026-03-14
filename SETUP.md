# 🚀 AUTONOMOUS COMPLIANCE SYSTEM - SETUP GUIDE

## Phase 1: Install Dependencies

```bash
py -m pip install -r requirements.txt
py -m spacy download en_core_web_sm
```

## Phase 2: Install Ollama

Download from: https://ollama.com/download

```bash
ollama pull llama3
```

## Phase 3: Run the System

```bash
py main.py
```

This will:
- ✅ Scan test_data/ with Presidio
- ✅ Validate cards with Luhn
- ✅ Analyze context with LLM
- ✅ Classify risk levels
- ✅ Auto-remediate critical findings
- ✅ Generate reports

## What You Built

✅ **Presidio Detection** - Enterprise PII detection
✅ **Auto-Remediation** - Masks critical card numbers
✅ **LLM Risk Analysis** - AI-powered classification

## Architecture

```
discovery → detection (Presidio) → validation → context → risk → remediation → reporting
```
