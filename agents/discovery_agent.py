from tools.file_scanner import scan_files, read_file
from cloud.drive_scanner import scan_drive
from cloud.s3_scanner import scan_s3
import os


def discovery_agent(state):
    print("  [1/6] Discovery: Scanning files...", flush=True)
    folder_path = state.get("folder_path", "")
    
    files = []
    raw_text = {}
    
    # Check for special scan modes
    s3_only = folder_path == "--s3-only"
    cloud_only = folder_path == "--cloud-only"
    
    # Scan local files (unless S3-only or cloud-only mode)
    if not s3_only and not cloud_only:
        files = scan_files(folder_path)
        for file in files:
            raw_text[file] = read_file(file)
        print(f"    > Found {len(files)} local files", flush=True)
    
    is_specific_file = os.path.isfile(folder_path) if folder_path and not folder_path.startswith("--") else False
    
    # Scan Google Drive
    if (cloud_only or not is_specific_file) and not s3_only:
        if os.path.exists("cloud/credentials.json"):
            print("    > Scanning Google Drive...", flush=True)
            drive_files = scan_drive()
            raw_text.update(drive_files)
            files.extend(list(drive_files.keys()))
            print(f"    > Found {len(drive_files)} cloud files", flush=True)
        else:
            print("    > Skipping Google Drive (no credentials)", flush=True)
    
    # Scan AWS S3
    if (s3_only or not is_specific_file) and not cloud_only:
        try:
            print("    > Scanning AWS S3...", flush=True)
            s3_files = scan_s3()
            if s3_files:
                raw_text.update(s3_files)
                files.extend(list(s3_files.keys()))
                print(f"    > Found {len(s3_files)} S3 files", flush=True)
            else:
                print("    > No S3 files found or credentials not configured", flush=True)
        except Exception as e:
            print(f"    > Skipping S3 (error: {e})", flush=True)

    state["files"] = files
    state["raw_text"] = raw_text
    print(f"    > Total: {len(files)} files", flush=True)
    return state
