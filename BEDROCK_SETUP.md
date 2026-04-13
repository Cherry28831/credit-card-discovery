# AWS Bedrock Setup Guide

## Step 1: Install AWS CLI

Download and install from: https://aws.amazon.com/cli/

Or use pip:
```bash
py -m pip install awscli
```

## Step 2: Get AWS Credentials

1. Go to AWS Console: https://console.aws.amazon.com/
2. Click your username (top right) → Security credentials
3. Scroll to "Access keys" → Create access key
4. Choose "Command Line Interface (CLI)"
5. Copy your:
   - Access Key ID
   - Secret Access Key

## Step 3: Configure AWS CLI

Run this command and paste your credentials:

```bash
aws configure
```

Enter:
- AWS Access Key ID: [paste your key]
- AWS Secret Access Key: [paste your secret]
- Default region name: us-east-1
- Default output format: json

## Step 4: Enable Bedrock Model Access

1. Go to: https://console.aws.amazon.com/bedrock/
2. Click "Model access" (left sidebar)
3. Click "Manage model access"
4. Check "Claude 3 Haiku"
5. Click "Request model access"

## Step 5: Test Connection

```bash
py main.py
```

Your credentials are stored in: `C:\Users\Cherry\.aws\credentials`
