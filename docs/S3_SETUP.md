# AWS S3 Integration Setup Guide

## Overview
The SecureScan system can now scan files stored in AWS S3 buckets for credit card data exposure. This guide will help you configure AWS credentials and use the S3 scanning feature.

## Prerequisites
- AWS Account with S3 access
- Python package `boto3` (already included in requirements.txt)

## AWS Credentials Configuration

### Option 1: Environment Variables (Recommended for Development)

Set the following environment variables:

**Windows (Command Prompt):**
```cmd
set AWS_ACCESS_KEY_ID=your_access_key_id
set AWS_SECRET_ACCESS_KEY=your_secret_access_key
set AWS_REGION=us-east-1
```

**Windows (PowerShell):**
```powershell
$env:AWS_ACCESS_KEY_ID="your_access_key_id"
$env:AWS_SECRET_ACCESS_KEY="your_secret_access_key"
$env:AWS_REGION="us-east-1"
```

**Linux/Mac:**
```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_REGION=us-east-1
```

### Option 2: AWS Credentials File (Recommended for Production)

1. Create the AWS credentials directory:
   - Windows: `C:\Users\YourUsername\.aws\`
   - Linux/Mac: `~/.aws/`

2. Create a file named `credentials` (no extension):

```ini
[default]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
```

3. Create a file named `config`:

```ini
[default]
region = us-east-1
```

### Option 3: IAM Role (For EC2 Instances)

If running on an EC2 instance, attach an IAM role with S3 read permissions. No credentials file needed.

## Creating AWS Access Keys

1. Log in to AWS Console
2. Go to IAM → Users → Your User
3. Click "Security credentials" tab
4. Click "Create access key"
5. Choose "Application running outside AWS"
6. Download and save the credentials securely

## Required IAM Permissions

Your AWS user/role needs the following S3 permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::*",
                "arn:aws:s3:::*/*"
            ]
        }
    ]
}
```

For specific buckets only:
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

## Testing S3 Connection

Run the S3 scanner test:

```bash
python cloud/s3_scanner.py
```

This will:
- Test your AWS credentials
- List all accessible S3 buckets
- Verify connection

## Using S3 Scanning

### Via Dashboard

1. Start the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

2. Go to "Run Scan" tab

3. Check "AWS S3" checkbox

4. Configure S3 options:
   - **Bucket Name**: Leave empty to scan all accessible buckets, or specify one bucket
   - **Prefix/Folder**: Optional folder path within bucket (e.g., `logs/`)

5. Click "Launch Scan"

### Via Command Line

The S3 scanner will automatically run when you execute:

```bash
python main.py
```

It will scan all accessible S3 buckets if AWS credentials are configured.

## Supported File Types

The S3 scanner will scan files with these extensions:
- `.txt` - Text files
- `.log` - Log files
- `.csv` - CSV files
- `.json` - JSON files
- `.xml` - XML files
- `.sql` - SQL files
- `.conf`, `.config`, `.ini` - Configuration files
- `.env` - Environment files
- `.properties` - Properties files

## File Size Limits

- Maximum file size: 10 MB
- Maximum files per bucket: 100 (configurable in code)

## Security Best Practices

1. **Use IAM Roles**: When running on AWS infrastructure, use IAM roles instead of access keys
2. **Least Privilege**: Grant only necessary S3 permissions
3. **Rotate Keys**: Regularly rotate access keys
4. **Never Commit Keys**: Never commit AWS credentials to version control
5. **Use AWS Secrets Manager**: For production, consider using AWS Secrets Manager
6. **Enable MFA**: Enable multi-factor authentication on your AWS account
7. **Monitor Access**: Use AWS CloudTrail to monitor S3 access

## Troubleshooting

### "AWS credentials not found"
- Verify credentials are set in environment variables or ~/.aws/credentials
- Check that the credentials file has correct format
- Ensure no extra spaces in credentials

### "Access Denied" errors
- Verify IAM permissions include s3:ListBucket and s3:GetObject
- Check bucket policies don't block access
- Verify the bucket exists and you have access

### "No accessible buckets found"
- Verify your AWS credentials have ListAllMyBuckets permission
- Check that buckets exist in your account
- Verify the AWS region is correct

### Connection timeout
- Check your internet connection
- Verify AWS region is accessible
- Check firewall/proxy settings

## Example Usage

### Scan specific bucket:
```python
from cloud.s3_scanner import scan_s3

# Scan specific bucket
files = scan_s3(bucket_names=['my-logs-bucket'])

# Scan with prefix
files = scan_s3(bucket_names=['my-bucket'], prefix='logs/2024/')

# Scan all accessible buckets
files = scan_s3()
```

## Cost Considerations

- **S3 GET Requests**: Each file download is a GET request (~$0.0004 per 1,000 requests)
- **Data Transfer**: Downloading files incurs data transfer costs
- **Recommendation**: Use S3 bucket policies to limit scanning to specific folders

## Integration with Remediation

When credit card data is found in S3 files:
1. The finding is logged with `s3://bucket-name/path` format
2. Remediation creates a local masked copy
3. Original S3 file remains unchanged
4. Consider implementing S3 upload for remediated files (future feature)

## Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
