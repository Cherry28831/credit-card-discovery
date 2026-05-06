from tools.file_scanner import scan_files, read_file
from cloud.drive_scanner import scan_drive
from cloud.s3_scanner import scan_s3
import os


def discovery_agent(state):
    print("  [1/6] Discovery: Scanning files...", flush=True)
    folder_path = state.get("folder_path", "")
    scan_cloud = state.get("scan_cloud", False)
    enable_s3 = state.get("scan_s3", False)
    scan_local = state.get("scan_local", True)
    
    print(f"    > Debug - enable_s3={enable_s3}, scan_local={scan_local}, scan_cloud={scan_cloud}", flush=True)
    
    files = []
    raw_text = {}
    
    # Scan local files if enabled
    if scan_local:
        print(f"    > Scanning local path: {folder_path}", flush=True)
        files = scan_files(folder_path)
        for file in files:
            raw_text[file] = read_file(file)
        print(f"    > Found {len(files)} local files", flush=True)
    else:
        print("    > Local scanning disabled", flush=True)
    
    # Scan Google Drive if enabled
    if scan_cloud:
        if os.path.exists("cloud/credentials.json"):
            print("    > Scanning Google Drive...", flush=True)
            drive_files = scan_drive()
            raw_text.update(drive_files)
            files.extend(list(drive_files.keys()))
            print(f"    > Found {len(drive_files)} cloud files", flush=True)
        else:
            print("    > Skipping Google Drive (no credentials)", flush=True)
    
    # Scan AWS S3 if enabled
    if enable_s3:
        print("    > S3 scanning enabled, calling scan_s3()...", flush=True)
        try:
            s3_files = scan_s3()
            if s3_files:
                raw_text.update(s3_files)
                files.extend(list(s3_files.keys()))
                print(f"    > Found {len(s3_files)} S3 files", flush=True)
            else:
                print("    > No S3 files found or credentials not configured", flush=True)
        except Exception as e:
            print(f"    > Skipping S3 (error: {e})", flush=True)
    else:
        print("    > S3 scanning disabled", flush=True)

    state["files"] = files
    state["raw_text"] = raw_text
    print(f"    > Total: {len(files)} files", flush=True)
    return state
