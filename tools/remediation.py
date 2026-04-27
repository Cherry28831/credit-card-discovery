import os
import re
import shutil
import tempfile
from datetime import datetime
from cloud.s3_scanner import get_s3_client


def mask_card_number(card_number):
    """Mask card number showing only last 4 digits"""
    card_str = str(card_number)
    if len(card_str) >= 4:
        return f"{'*' * (len(card_str) - 4)}{card_str[-4:]}"
    return "*" * len(card_str)


def remediate_s3_file(s3_path, card_number):
    """
    Remediate an S3 file by downloading, masking, and uploading to remediated location.
    Original S3 file remains untouched.
    Remediated file is uploaded to s3://bucket/remediated/original-path
    
    Returns: (success, message, remediated_s3_path)
    """
    try:
        # Parse S3 path: s3://bucket/key
        if not s3_path.startswith('s3://'):
            return False, "Invalid S3 path format", None
        
        path_parts = s3_path[5:].split('/', 1)
        if len(path_parts) < 2:
            return False, "Invalid S3 path format", None
        
        bucket_name = path_parts[0]
        object_key = path_parts[1]
        
        # Get S3 client
        s3_client = get_s3_client()
        if not s3_client:
            return False, "Failed to connect to S3", None
        
        # Create temporary file for download
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Download from S3
            s3_client.download_file(bucket_name, object_key, temp_path)
            
            # Read content
            try:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(temp_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # Mask the card number
            card_str = str(card_number)
            masked = mask_card_number(card_number)
            
            # Replace all occurrences
            patterns = [
                card_str,
                ' '.join([card_str[i:i+4] for i in range(0, len(card_str), 4)]),
                '-'.join([card_str[i:i+4] for i in range(0, len(card_str), 4)]),
            ]
            
            modified = False
            for pattern in patterns:
                if pattern in content:
                    content = content.replace(pattern, masked)
                    modified = True
            
            if not modified:
                return False, "Card number not found in file", None
            
            # Write masked content to temp file
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create remediated S3 path: s3://bucket/remediated/original-key
            remediated_key = f"remediated/{object_key}"
            remediated_s3_path = f"s3://{bucket_name}/{remediated_key}"
            
            # Upload to S3
            s3_client.upload_file(temp_path, bucket_name, remediated_key)
            
            return True, f"Remediated and uploaded to S3: {remediated_s3_path}", remediated_s3_path
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return False, f"Error remediating S3 file: {str(e)}", None


def remediate_file(file_path, card_number):
    """
    Remediate a file by creating/updating a masked version in remediated_files folder.
    If remediated file already exists, mask in the same file.
    Original file remains untouched.
    
    Returns: (success, message, remediated_file_path)
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}", None
        
        # Create remediated files directory
        remediated_dir = "outputs/remediated_files"
        os.makedirs(remediated_dir, exist_ok=True)
        
        # Create remediated file path (without timestamp, same name as original)
        file_name = os.path.basename(file_path)
        remediated_file_path = os.path.join(remediated_dir, file_name)
        
        # Check if remediated file already exists
        if os.path.exists(remediated_file_path):
            # Read from existing remediated file
            try:
                with open(remediated_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(remediated_file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
        else:
            # Read from original file (first time)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
        
        # Mask the card number
        card_str = str(card_number)
        masked = mask_card_number(card_number)
        
        # Replace all occurrences of the card number
        # Handle different formats: with spaces, dashes, or no separators
        patterns = [
            card_str,  # Plain number
            ' '.join([card_str[i:i+4] for i in range(0, len(card_str), 4)]),  # Spaces every 4 digits
            '-'.join([card_str[i:i+4] for i in range(0, len(card_str), 4)]),  # Dashes every 4 digits
        ]
        
        modified = False
        for pattern in patterns:
            if pattern in content:
                content = content.replace(pattern, masked)
                modified = True
        
        if not modified:
            return False, f"Card number not found in file", remediated_file_path
        
        # Write masked content to remediated file
        with open(remediated_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"Remediated file: {remediated_file_path}", remediated_file_path
        
    except Exception as e:
        return False, f"Error remediating file: {str(e)}", None


def remediate_finding(file_path, card_number):
    """
    Main function to remediate a finding.
    Handles both local files and S3 files.
    - Local: Creates masked file in remediated_files folder
    - S3: Downloads, masks, and uploads to s3://bucket/remediated/path
    Original file remains untouched.
    
    Returns: (success, message, remediated_file_path)
    """
    # Check if S3 path
    if file_path.startswith('s3://'):
        return remediate_s3_file(file_path, card_number)
    else:
        return remediate_file(file_path, card_number)
