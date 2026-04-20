import os
import re
import shutil
from datetime import datetime


def mask_card_number(card_number):
    """Mask card number showing only last 4 digits"""
    card_str = str(card_number)
    if len(card_str) >= 4:
        return f"{'*' * (len(card_str) - 4)}{card_str[-4:]}"
    return "*" * len(card_str)


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
    Creates a new masked file in remediated_files folder.
    Original file remains untouched.
    
    Returns: (success, message, remediated_file_path)
    """
    return remediate_file(file_path, card_number)
