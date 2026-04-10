from tools.file_scanner import scan_files, read_file
from cloud.drive_scanner import scan_drive


def discovery_agent(state):
    print("  [1/6] Discovery: Scanning files...")
    files = scan_files(state["folder_path"])
    raw_text = {}

    for file in files:
        raw_text[file] = read_file(file)

    print(f"  ✓ Found {len(files)} local files")
    
    print("  [1/6] Discovery: Scanning Google Drive...")
    drive_files = scan_drive()
    raw_text.update(drive_files)
    files.extend(list(drive_files.keys()))
    
    print(f"  ✓ Found {len(drive_files)} cloud files")

    state["files"] = files
    state["raw_text"] = raw_text
    print(f"  ✓ Total: {len(files)} files")
    return state
