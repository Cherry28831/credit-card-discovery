import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
import json

def get_s3_client():
    """
    Initialize S3 client using credentials from:
    1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
    2. AWS credentials file (~/.aws/credentials)
    3. IAM role (if running on EC2)
    """
    try:
        # Try to get region from environment or use default
        region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Initialize S3 client
        s3_client = boto3.client('s3', region_name=region)
        
        # Test connection by listing buckets
        try:
            s3_client.list_buckets()
            print(f"[OK] Successfully authenticated with AWS")
            print(f"[OK] Using region: {region}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidAccessKeyId':
                print("[ERROR] Invalid AWS Access Key ID")
            elif error_code == 'SignatureDoesNotMatch':
                print("[ERROR] Invalid AWS Secret Access Key")
            elif error_code == 'AccessDenied':
                print("[ERROR] Access Denied - Check IAM permissions")
                print("  Required permission: s3:ListAllMyBuckets")
            else:
                print(f"[ERROR] AWS Error: {error_code} - {e.response['Error']['Message']}")
            return None
        
        return s3_client
    except NoCredentialsError:
        print("[ERROR] AWS credentials not found")
        print("  Configure credentials using one of these methods:")
        print("  1. AWS CLI: aws configure")
        print("  2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("  3. Credentials file: ~/.aws/credentials")
        return None
    except Exception as e:
        print(f"[ERROR] Error initializing S3 client: {e}")
        return None


def list_buckets(s3_client):
    """List all accessible S3 buckets"""
    try:
        response = s3_client.list_buckets()
        return [bucket['Name'] for bucket in response['Buckets']]
    except Exception as e:
        print(f"Error listing buckets: {e}")
        return []


def scan_bucket(s3_client, bucket_name, prefix='', max_files=100):
    """
    Scan files in an S3 bucket
    
    Args:
        s3_client: Boto3 S3 client
        bucket_name: Name of the S3 bucket
        prefix: Optional prefix to filter objects (folder path)
        max_files: Maximum number of files to scan
    
    Returns:
        Dictionary with file paths as keys and content as values
    """
    s3_files = {}
    file_count = 0
    
    # File extensions to scan
    scannable_extensions = [
        '.txt', '.log', '.csv', '.json', '.xml', '.sql', 
        '.conf', '.config', '.ini', '.env', '.properties'
    ]
    
    try:
        # List objects in bucket
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        for page in pages:
            if 'Contents' not in page:
                continue
                
            for obj in page['Contents']:
                if file_count >= max_files:
                    break
                    
                key = obj['Key']
                size = obj['Size']
                
                # Skip if file is too large (> 10MB)
                if size > 10 * 1024 * 1024:
                    continue
                
                # Check if file has scannable extension
                if not any(key.lower().endswith(ext) for ext in scannable_extensions):
                    continue
                
                try:
                    # Download file content
                    response = s3_client.get_object(Bucket=bucket_name, Key=key)
                    content = response['Body'].read()
                    
                    # Try to decode as text
                    try:
                        text_content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            text_content = content.decode('latin-1')
                        except:
                            continue
                    
                    # Store with s3:// prefix
                    file_path = f"s3://{bucket_name}/{key}"
                    s3_files[file_path] = text_content
                    file_count += 1
                    
                    print(f"  Scanned: {file_path} ({size} bytes)")
                    
                except Exception as e:
                    print(f"  Error reading {key}: {e}")
                    continue
            
            if file_count >= max_files:
                break
        
        return s3_files
        
    except Exception as e:
        print(f"Error scanning bucket {bucket_name}: {e}")
        return {}


def scan_s3(bucket_names=None, prefix='', max_files_per_bucket=100):
    """
    Main function to scan S3 buckets
    
    Args:
        bucket_names: List of bucket names to scan. If None, scans all accessible buckets
        prefix: Optional prefix to filter objects
        max_files_per_bucket: Maximum files to scan per bucket
    
    Returns:
        Dictionary with file paths as keys and content as values
    """
    print("    [S3 Scanner] Initializing AWS S3 connection...", flush=True)
    
    s3_client = get_s3_client()
    if not s3_client:
        return {}
    
    all_files = {}
    
    # If no bucket names provided, list all accessible buckets
    if not bucket_names:
        print("    [S3 Scanner] Listing all accessible buckets...", flush=True)
        bucket_names = list_buckets(s3_client)
        
        if not bucket_names:
            print("    [S3 Scanner] No accessible buckets found.", flush=True)
            return {}
        
        print(f"    [S3 Scanner] Found {len(bucket_names)} accessible bucket(s)", flush=True)
    
    # Scan each bucket
    for bucket_name in bucket_names:
        print(f"    [S3 Scanner] Scanning bucket: {bucket_name}", flush=True)
        bucket_files = scan_bucket(s3_client, bucket_name, prefix, max_files_per_bucket)
        all_files.update(bucket_files)
        print(f"    [S3 Scanner] Found {len(bucket_files)} file(s) in {bucket_name}", flush=True)
    
    print(f"    [S3 Scanner] Total S3 files scanned: {len(all_files)}", flush=True)
    return all_files


def test_s3_connection():
    """Test S3 connection and list buckets"""
    print("Testing AWS S3 connection...")
    print(f"Credentials location: {os.path.expanduser('~/.aws/credentials')}")
    print()
    
    s3_client = get_s3_client()
    if not s3_client:
        print()
        print("Troubleshooting steps:")
        print("1. Verify AWS credentials are configured")
        print("2. Check IAM permissions (need s3:ListAllMyBuckets)")
        print("3. Ensure credentials are not expired")
        print("4. Try creating a test S3 bucket in AWS Console")
        return False
    
    buckets = list_buckets(s3_client)
    if buckets:
        print(f"[OK] Successfully connected to AWS S3")
        print(f"[OK] Found {len(buckets)} accessible buckets:")
        for bucket in buckets:
            print(f"  - {bucket}")
        return True
    else:
        print("[!] No accessible buckets found")
        print()
        print("This could mean:")
        print("1. You don't have any S3 buckets yet (create one in AWS Console)")
        print("2. IAM permissions don't allow listing buckets")
        print("3. Buckets exist in a different AWS region")
        print()
        print("To create a test bucket:")
        print("1. Go to: https://s3.console.aws.amazon.com/s3/")
        print("2. Click 'Create bucket'")
        print("3. Enter a unique name (e.g., 'test-scan-bucket-yourname')")
        print("4. Click 'Create bucket'")
        return False


if __name__ == "__main__":
    # Test the connection
    test_s3_connection()
