from tools.file_scanner import scan_files, read_file
from cloud.drive_scanner import scan_drive
import os


def discovery_agent(state):
    print("  [1/6] Discovery: Scanning files...", flush=True)
    files = scan_files(state["folder_path"])
    raw_text = {}

    for file in files:
        raw_text[file] = read_file(file)

    print(f"  > Found {len(files)} local files", flush=True)
    
    # Only scan Google Drive if credentials exist AND no specific local path was given
    folder_path = state.get("folder_path", "")
    is_specific_file = os.path.isfile(folder_path)
    
    if not is_specific_file and os.path.exists("cloud/credentials.json"):
        print("  > Scanning Google Drive...", flush=True)
        drive_files = scan_drive()
        raw_text.update(drive_files)
        files.extend(list(drive_files.keys()))
        print(f"  > Found {len(drive_files)} cloud files", flush=True)
    else:
        if is_specific_file:
            print("  > Skipping Google Drive (specific file scan)", flush=True)
        else:
            print("  > Skipping Google Drive (no credentials)", flush=True)

    state["files"] = files
    state["raw_text"] = raw_text
    print(f"  > Total: {len(files)} files", flush=True)
    return state
