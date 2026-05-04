"""文件操作工具"""
import os
import fnmatch
from server.config import config


def search_local_files(query: str, path: str = "", file_pattern: str = "*.md") -> str:
    search_root = path or config.notes_dir
    if not os.path.isdir(search_root):
        return f"路径不存在: {search_root}"

    results = []
    for root, dirs, files in os.walk(search_root):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules', '.git')]
        for fname in files:
            if not fnmatch.fnmatch(fname, file_pattern):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if query.lower() in content.lower():
                    idx = content.lower().find(query.lower())
                    start = max(0, idx - 50)
                    end = min(len(content), idx + len(query) + 100)
                    results.append({"file": fpath, "snippet": content[start:end]})
            except Exception:
                continue

    results = results[:10]
    if not results:
        return f"未找到包含 '{query}' 的文件"
    output = [f"找到 {len(results)} 个匹配文件：\n"]
    for r in results:
        output.append(f"[文件] {r['file']}")
        output.append(f"  片段: ...{r['snippet']}...\n")
    return "\n".join(output)


def read_file_content(file_path: str) -> str:
    if not os.path.isfile(file_path):
        return f"文件不存在: {file_path}"
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"读取失败: {e}"


SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_local_files",
        "description": "在本地笔记/文档中搜索关键词，返回匹配的文件路径和上下文片段",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "path": {"type": "string", "description": "搜索路径（可选）"},
                "file_pattern": {"type": "string", "description": "文件匹配模式，如 *.md（可选，默认 *.md）"}
            },
            "required": ["query"]
        }
    }
}

READER_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file_content",
        "description": "读取指定文件的完整内容",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "文件路径"}
            },
            "required": ["file_path"]
        }
    }
}
