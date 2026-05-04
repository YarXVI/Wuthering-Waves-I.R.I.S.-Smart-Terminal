"""
Meeting Export - Export meeting records
"""

from typing import Dict, Any


def export_meeting_to_markdown(meeting_data: Dict[str, Any]) -> str:
    """Export meeting to markdown format"""
    lines = [
        f"# {meeting_data.get('title', 'Meeting')}",
        "",
        f"Meeting ID: {meeting_data.get('meeting_id', '')}",
        f"Created: {meeting_data.get('created_at', '')}",
        "",
        "## Discussion Rounds",
        ""
    ]

    for round_data in meeting_data.get('rounds', []):
        lines.append(f"### Round {round_data.get('round_number', 0)}")
        lines.append(f"**Author:** {round_data.get('author', '')}")
        lines.append("")
        lines.append(round_data.get('content', ''))
        lines.append("")

    return "\n".join(lines)


def export_meeting_to_json(meeting_data: Dict[str, Any]) -> str:
    """Export meeting to JSON format"""
    import json
    return json.dumps(meeting_data, indent=2, ensure_ascii=False)
