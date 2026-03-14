from tools.file_scanner import scan_files, read_file


def discovery_agent(state):
    print("  [1/6] Discovery: Scanning files...")
    files = scan_files(state["folder_path"])
    raw_text = {}

    for file in files:
        raw_text[file] = read_file(file)

    state["files"] = files
    state["raw_text"] = raw_text
    print(f"  ✓ Found {len(files)} files")
    return state
