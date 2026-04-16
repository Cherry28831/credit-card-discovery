import os


def scan_files(path):
    file_paths = []
    
    # Check if path is a file
    if os.path.isfile(path):
        return [path]
    
    # Otherwise treat as directory
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                file_paths.append(os.path.join(root, file))
    
    return file_paths


def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""
