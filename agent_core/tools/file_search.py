"""
File search tools for agent
"""

import os
import re
from pathlib import Path
from typing import Optional


FILE_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_local_files",
        "description": "Search for files matching a pattern in a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to search in",
                },
                "pattern": {
                    "type": "string",
                    "description": "File name pattern to match (supports * wildcard)",
                },
            },
            "required": ["path", "pattern"],
        },
    },
}


FILE_READER_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file_content",
        "description": "Read content of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Full path to the file to read",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum number of characters to read",
                    "default": 10000,
                },
            },
            "required": ["file_path"],
        },
    },
}


def search_local_files(path: str, pattern: str) -> dict:
    """
    Search for files matching pattern in directory
    """
    try:
        search_path = Path(path)
        if not search_path.exists():
            return {"success": False, "error": f"Path does not exist: {path}"}
        if not search_path.is_dir():
            return {"success": False, "error": f"Path is not a directory: {path}"}

        # Convert pattern to regex
        regex_pattern = pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
        regex = re.compile(regex_pattern, re.IGNORECASE)

        matches = []
        for item in search_path.rglob("*"):
            if item.is_file() and regex.search(item.name):
                matches.append({
                    "name": item.name,
                    "path": str(item),
                    "size": item.stat().st_size,
                })

        return {
            "success": True,
            "matches": matches[:100],  # Limit to 100 results
            "count": len(matches),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_file_content(file_path: str, max_chars: int = 10000) -> dict:
    """
    Read content of a file
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File does not exist: {file_path}"}
        if not path.is_file():
            return {"success": False, "error": f"Path is not a file: {file_path}"}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(max_chars)

        return {
            "success": True,
            "content": content,
            "file_path": str(path),
            "truncated": len(content) >= max_chars,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
