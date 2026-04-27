# AWS S3 Quick Start Guide

## Step-by-Step Setup

### Step 1: Install AWS CLI (Optional but Recommended)

**Windows:**
```cmd
# Download and install from: https://aws.amazon.com/cli/
# Or use chocolatey:
choco install awscli
```

**Verify installation:**
```cmd
aws --version
```

### Step 2: Configure AWS Credentials

#### Method A: Using AWS CLI (Easiest)

```cmd
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: `AKIAIOSFODNN7EXAMPLE`
- **AWS Secret Access Key**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
- **Default region**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

This creates files at:
- Windows: `C:\Users\YourUsername\.aws\credentials`
- Linux/Mac: `~/.aws/credentials`

#### Method B: Manual Setup (Windows)

1. Create directory:
```cmd
mkdir %USERPROFILE%\.aws
```

2. Create `credentials` file (no extension):
```cmd
notepad %USERPROFILE%\.aws\credentials
```

Add this content:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
```

3. Create `config` file:
```cmd
notepad %USERPROFILE%\.aws\config
```

Add this content:
```ini
[default]
region = us-east-1
```

#### Method C: Environment Variables (Temporary)

**Windows Command Prompt:**
```cmd
set AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
set AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
set AWS_REGION=us-east-1
```

**Windows PowerShell:**
```powershell
$env:AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
$env:AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"
$env:AWS_REGION="us-east-1"
```

### Step 3: Get AWS Access Keys

If you don't have AWS access keys:

1. **Login to AWS Console**: https://console.aws.amazon.com/
2. **Go to IAM**: Search for "IAM" in the search bar
3. **Click "Users"** in the left sidebar
4. **Select your user** (or create a new one)
5. **Click "Security credentials" tab**
6. **Click "Create access key"**
7. **Select "Application running outside AWS"**
8. **Click "Next"** → **"Create access key"**
9. **Download the CSV file** or copy the keys immediately (you won't see them again!)

### Step 4: Set IAM Permissions

Your AWS user needs S3 read permissions. Attach this policy:

1. In IAM → Users → Your User
2. Click "Add permissions" → "Attach policies directly"
3. Search for and select: **`AmazonS3ReadOnlyAccess`**
4. Click "Next" → "Add permissions"

Or create a custom policy for specific buckets:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

### Step 5: Test Your S3 Connection

```cmd
cd "c:\Users\Cherry\Downloads\Axis\Credit Card Data Discovery"
python cloud/s3_scanner.py
```

**Expected output:**
```
Testing AWS S3 connection...
✓ Successfully connected to AWS S3
✓ Found 3 accessible buckets:
  - my-logs-bucket
  - my-data-bucket
  - my-backup-bucket
```

**If you see errors:**
- "AWS credentials not found" → Check Step 2
- "Access Denied" → Check Step 4 (IAM permissions)
- "No accessible buckets found" → You may not have any S3 buckets yet

### Step 6: Use S3 Scanning

#### Option A: Via Dashboard (Recommended)

1. **Start the dashboard:**
```cmd
cd "c:\Users\Cherry\Downloads\Axis\Credit Card Data Discovery"
streamlit run dashboard.py
```

2. **Navigate to "Run Scan" tab**

3. **Check the "AWS S3" checkbox**

4. **Configure S3 options:**
   - **Bucket Name**: Leave empty to scan ALL buckets, or enter specific bucket name
   - **Prefix/Folder**: Optional (e.g., `logs/2024/` to scan only that folder)

5. **Click "Launch Scan"**

6. **View results:**
   - S3 files will appear with `s3://bucket-name/file-path` format
   - Purple color in "Source Breakdown" chart
   - Filter by "S3" in AI Analysis tab

#### Option B: Via Command Line

```cmd
cd "c:\Users\Cherry\Downloads\Axis\Credit Card Data Discovery"
python main.py
```

This will automatically:
- Scan local files
- Scan Google Drive (if configured)
- Scan ALL accessible S3 buckets

### Step 7: Understanding S3 Results

**In the Dashboard:**

1. **Overview Tab:**
   - "Source Breakdown" chart shows S3 files in purple
   - Total findings include S3 discoveries

2. **AI Analysis Tab:**
   - Filter by "S3" source
   - S3 files show as: `s3://bucket-name/path/to/file.log`
   - Source label shows "S3"

3. **Remediated Tab:**
   - Remediated S3 files create local masked copies
   - Original S3 files remain unchanged

## Common Use Cases

### Use Case 1: Scan Specific Bucket

**Dashboard:**
- Check "AWS S3"
- Enter bucket name: `my-logs-bucket`
- Leave prefix empty
- Click "Launch Scan"

**Code:**
```python
from cloud.s3_scanner import scan_s3
files = scan_s3(bucket_names=['my-logs-bucket'])
```

### Use Case 2: Scan Specific Folder in Bucket

**Dashboard:**
- Check "AWS S3"
- Enter bucket name: `my-logs-bucket`
- Enter prefix: `production/logs/`
- Click "Launch Scan"

**Code:**
```python
from cloud.s3_scanner import scan_s3
files = scan_s3(bucket_names=['my-logs-bucket'], prefix='production/logs/')
```

### Use Case 3: Scan All Buckets

**Dashboard:**
- Check "AWS S3"
- Leave bucket name empty
- Leave prefix empty
- Click "Launch Scan"

**Code:**
```python
from cloud.s3_scanner import scan_s3
files = scan_s3()  # Scans all accessible buckets
```

### Use Case 4: Scan Multiple Specific Buckets

**Code only:**
```python
from cloud.s3_scanner import scan_s3
files = scan_s3(bucket_names=['bucket1', 'bucket2', 'bucket3'])
```

## What Files Are Scanned?

The S3 scanner looks for these file types:
- `.txt` - Text files
- `.log` - Log files
- `.csv` - CSV data files
- `.json` - JSON files
- `.xml` - XML files
- `.sql` - SQL dump files
- `.conf`, `.config`, `.ini` - Configuration files
- `.env` - Environment variable files
- `.properties` - Java properties files

**Limits:**
- Maximum file size: 10 MB
- Maximum files per bucket: 100

## Troubleshooting

### Problem: "AWS credentials not found"

**Solution:**
```cmd
# Check if credentials file exists
dir %USERPROFILE%\.aws\credentials

# If not, run:
aws configure

# Or set environment variables:
set AWS_ACCESS_KEY_ID=your_key
set AWS_SECRET_ACCESS_KEY=your_secret
set AWS_REGION=us-east-1
```

### Problem: "Access Denied"

**Solution:**
1. Check IAM permissions (need `s3:ListBucket` and `s3:GetObject`)
2. Verify bucket policy doesn't block your access
3. Check if bucket exists and you have access

### Problem: "No accessible buckets found"

**Solution:**
1. Create a test S3 bucket in AWS Console
2. Verify your AWS credentials have `s3:ListAllMyBuckets` permission
3. Check you're in the correct AWS region

### Problem: Scan is slow

**Solution:**
- Specify a bucket name instead of scanning all buckets
- Use a prefix to limit the scan to specific folders
- Reduce `max_files_per_bucket` in code (default: 100)

## Security Best Practices

1. **Never commit AWS credentials to Git**
   - Add `.aws/` to `.gitignore`
   - Use environment variables for CI/CD

2. **Use least privilege IAM permissions**
   - Only grant S3 read access
   - Limit to specific buckets if possible

3. **Rotate access keys regularly**
   - Every 90 days recommended
   - Delete unused keys

4. **Enable MFA on AWS account**
   - Adds extra security layer

5. **Monitor access with CloudTrail**
   - Track who accessed what

## Cost Considerations

**S3 Pricing (approximate):**
- GET requests: $0.0004 per 1,000 requests
- Data transfer out: $0.09 per GB (first 10 TB)

**Example:**
- Scanning 1,000 files = ~$0.0004
- Downloading 1 GB of files = ~$0.09

**Tips to reduce costs:**
- Scan specific buckets/folders instead of all
- Use prefix filtering
- Limit max files per bucket

## Next Steps

1. ✅ Configure AWS credentials
2. ✅ Test connection with `python cloud/s3_scanner.py`
3. ✅ Run your first scan via dashboard
4. ✅ Review findings in Overview tab
5. ✅ Analyze S3 findings in AI Analysis tab
6. ✅ Remediate any exposed credit card data

## Need Help?

- **AWS Documentation**: https://docs.aws.amazon.com/s3/
- **Boto3 Docs**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
- **IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

## Example: Complete Workflow

```cmd
# 1. Configure AWS
aws configure

# 2. Test connection
cd "c:\Users\Cherry\Downloads\Axis\Credit Card Data Discovery"
python cloud/s3_scanner.py

# 3. Run scan
streamlit run dashboard.py

# 4. In dashboard:
#    - Go to "Run Scan" tab
#    - Check "AWS S3"
#    - Click "Launch Scan"

# 5. View results in "Overview" tab
# 6. Analyze findings in "AI Analysis" tab
# 7. Remediate issues in "AI Analysis" tab
# 8. Check "Remediated" tab for completed remediations
```

That's it! You're now ready to scan AWS S3 buckets for credit card data exposure! 🚀
