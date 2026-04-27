# S3 Remediation Guide

## Overview

The SecureScan tool now supports automatic remediation of sensitive data found in AWS S3 buckets. When you remediate an S3 finding, the tool will:

1. Download the file from S3
2. Mask the sensitive card numbers
3. Upload the remediated file to a designated S3 location
4. Keep the original file untouched

## How It Works

### Remediation Process

When you click "Remediate" on an S3 finding:

```
Original:    s3://my-bucket/logs/app.log
Remediated:  s3://my-bucket/remediated/logs/app.log
```

The remediated file is uploaded to the same bucket under a `remediated/` prefix, preserving the original folder structure.

### Example

**Before Remediation:**
```
s3://my-bucket/
├── logs/
│   ├── app.log          (contains: 4532-1234-5678-9012)
│   └── access.log
└── data/
    └── transactions.csv
```

**After Remediation:**
```
s3://my-bucket/
├── logs/
│   ├── app.log          (unchanged: 4532-1234-5678-9012)
│   └── access.log
├── data/
│   └── transactions.csv
└── remediated/          (NEW)
    └── logs/
        └── app.log      (masked: ************9012)
```

## Features

### Automatic Detection
- The tool automatically detects S3 paths (starting with `s3://`)
- Uses the same masking logic as local files
- Handles multiple card number formats (plain, spaced, dashed)

### Masking Strategy
- Shows only the last 4 digits of card numbers
- Replaces the rest with asterisks (*)
- Example: `4532123456789012` → `************9012`

### Error Handling
- Validates S3 path format
- Checks S3 connectivity
- Provides clear error messages if remediation fails

## IAM Permissions Required

To remediate S3 files, your AWS credentials need these additional permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

### Minimum Permissions
- `s3:GetObject` - Download files for masking
- `s3:PutObject` - Upload remediated files

## Usage in Dashboard

### Step 1: Scan S3 Bucket
1. Go to "Run Scan" tab
2. Check "AWS S3"
3. Enter bucket name (or leave empty for all buckets)
4. Click "Launch Scan"

### Step 2: Review Findings
1. Go to "AI Analysis" tab
2. Filter by Source: "S3"
3. Review the findings with AI-powered context

### Step 3: Remediate
1. Click "Remediate" button on any S3 finding
2. Wait for confirmation: "Remediated and uploaded to S3!"
3. The finding moves to "Remediated" tab

### Step 4: Verify
1. Go to "Remediated" tab
2. View the remediated S3 path
3. Check your S3 bucket for the `remediated/` folder

## Remediated Files Location

All remediated S3 files are stored in the same bucket under the `remediated/` prefix:

| Original Path | Remediated Path |
|--------------|-----------------|
| `s3://bucket/file.txt` | `s3://bucket/remediated/file.txt` |
| `s3://bucket/logs/app.log` | `s3://bucket/remediated/logs/app.log` |
| `s3://bucket/data/users.csv` | `s3://bucket/remediated/data/users.csv` |

## Cost Considerations

### S3 API Costs
- **GET requests**: $0.0004 per 1,000 requests
- **PUT requests**: $0.005 per 1,000 requests
- **Data transfer**: $0.09 per GB (out to internet)

### Example Cost
Remediating 100 files (average 10KB each):
- GET requests: 100 × $0.0004/1000 = $0.00004
- PUT requests: 100 × $0.005/1000 = $0.0005
- Data transfer: 1MB × $0.09/GB = ~$0.00009
- **Total: ~$0.0006 (less than $0.001)**

## Troubleshooting

### Error: "Failed to connect to S3"
**Solution**: Check your AWS credentials configuration
```bash
aws configure list
```

### Error: "Access Denied"
**Solution**: Verify IAM permissions include `s3:GetObject` and `s3:PutObject`

### Error: "Invalid S3 path format"
**Solution**: Ensure path starts with `s3://` and includes bucket name

### Error: "Card number not found in file"
**Solution**: The card number may have been already masked or is in a different format

## Best Practices

1. **Test First**: Use a test bucket before remediating production data
2. **Backup**: Keep original files untouched (tool does this automatically)
3. **Verify**: Check remediated files in S3 console after remediation
4. **Monitor**: Review remediation logs in the dashboard
5. **Permissions**: Use least-privilege IAM policies

## Security Notes

- Original S3 files are **never modified**
- Remediated files are stored separately under `remediated/` prefix
- All operations use encrypted connections (HTTPS)
- AWS credentials are never logged or displayed
- Temporary files are deleted after upload

## Integration with Compliance

The S3 remediation feature helps with:
- **PCI DSS Requirement 3.4**: Render PAN unreadable
- **GDPR Article 32**: Security of processing
- **HIPAA**: Safeguards for PHI
- **SOC 2**: Data protection controls

## Next Steps

After remediation:
1. Review remediated files in S3 console
2. Update application configurations to use remediated files
3. Archive or delete original files (manual step)
4. Document remediation in compliance reports
5. Schedule regular scans to catch new exposures

## Support

For issues or questions:
- Check the main S3_SETUP.md for credential configuration
- Review scan logs in "Run Scan" tab
- Check remediation status in "Remediated" tab
