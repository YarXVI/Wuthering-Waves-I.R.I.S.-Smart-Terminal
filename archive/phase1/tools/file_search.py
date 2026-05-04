"""
文件搜索工具 — 按关键词搜索本地文件内容
"""

import os
import fnmatch
from config import config


def search_local_files(query: str, path: str = "", file_pattern: str = "*.md") -> str:
    """
    在本地目录中搜索包含 query 的文件。

    参数:
        query: 搜索关键词
        path: 搜索路径，默认使用配置中的 notes_dir
        file_pattern: 文件匹配模式，如 "*.md", "*.txt", "*.*"
    返回:
        匹配文件路径列表的文本描述
    """
    search_root = path or config.notes_dir

    if not os.path.isdir(search_root):
        return f"错误：路径 '{search_root}' 不存在或不可访问"

    results = []
    for root, dirs, files in os.walk(search_root):
        # 忽略隐藏目录和 .git、__pycache__ 等
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__'
                   and d != 'node_modules' and d != '.git']

        for fname in files:
            if not fnmatch.fnmatch(fname, file_pattern):
                continue

            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if query.lower() in content.lower():
                    # 截取匹配上下文
                    idx = content.lower().find(query.lower())
                    start = max(0, idx - 50)
                    end = min(len(content), idx + len(query) + 100)
                    context = content[start:end]
                    results.append({
                        "file": fpath,
                        "snippet": context,
                    })
            except Exception:
                continue

    # 限制结果数量
    results = results[:10]

    if not results:
        return f"未在 '{search_root}' 下找到包含 '{query}' 的文件"

    output = [f"找到 {len(results)} 个匹配文件：\n"]
    for r in results:
        output.append(f"📄 {r['file']}")
        output.append(f"   片段: ...{r['snippet']}...\n")

    return "\n".join(output)


def read_file_content(file_path: str) -> str:
    """
    读取指定文件的完整内容。

    参数:
        file_path: 文件路径
    返回:
        文件内容文本
    """
    if not os.path.isfile(file_path):
        return f"错误：文件 '{file_path}' 不存在"
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"读取文件出错: {e}"


# OpenAI function calling 工具定义
FILE_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_local_files",
        "description": "在本地笔记/文档中搜索关键词，返回匹配的文件路径和上下文片段",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "path": {
                    "type": "string",
                    "description": "搜索路径（可选，默认笔记目录）"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "文件匹配模式，如 *.md, *.txt, *.*（可选，默认 *.md）",
                    "default": "*.md"
                }
            },
            "required": ["query"]
        }
    }
}

FILE_READER_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file_content",
        "description": "读取指定文件的完整内容",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要读取的文件路径"
                }
            },
            "required": ["file_path"]
        }
    }
}
