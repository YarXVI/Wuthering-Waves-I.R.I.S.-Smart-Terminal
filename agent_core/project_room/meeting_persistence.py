"""
Meeting Persistence - Save/load meeting data
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class MeetingPersistence:
    """Persist meeting data to disk"""

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path.home() / ".iris" / "meetings"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_meeting(self, meeting_id: str, data: Dict[str, Any]) -> bool:
        """Save meeting to disk"""
        try:
            filepath = self.data_dir / f"{meeting_id}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Load meeting from disk"""
        try:
            filepath = self.data_dir / f"{meeting_id}.json"
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception:
            return None

    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete meeting from disk"""
        try:
            filepath = self.data_dir / f"{meeting_id}.json"
            if filepath.exists():
                filepath.unlink()
            return True
        except Exception:
            return False


persistence = MeetingPersistence()
