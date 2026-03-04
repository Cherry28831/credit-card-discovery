from typing import TypedDict, List, Dict


class ScanState(TypedDict):
    folder_path: str
    files: List[str]
    raw_text: Dict[str, str]
    potential_cards: Dict[str, List[str]]
    valid_cards: List[Dict]
    enriched_findings: List[Dict]
    report: str
