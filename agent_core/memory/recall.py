"""

跨会话召回模块 - 支持 FTS5 全文搜索

"""



import json

import re

import sqlite3

from dataclasses import dataclass

from datetime import datetime

from pathlib import Path

from typing import Any



from agent_core.memory.session_store import BASE_DIR as SESSIONS_DIR





SEARCH_INDEX_DIR = Path(__file__).resolve().parent.parent.parent / "memory" / "search_index"

SEARCH_INDEX_DB = SEARCH_INDEX_DIR / "fts_index.db"





@dataclass

class SearchResult:

    """搜索结果"""

    agent_id: str

    session_file: str

    snippet: str

    score: float

    matched_at: str





class SessionSearchEngine:

    """会话搜索引擎 - 基于 SQLite FTS5"""



    def __init__(self, index_db: Path | None = None):

        self.index_db = index_db or SEARCH_INDEX_DB

        self._ensure_index()



    def _ensure_index(self):

        """确保搜索索引存在"""

        self.index_db.parent.mkdir(parents=True, exist_ok=True)



        conn = sqlite3.connect(str(self.index_db))

        cursor = conn.cursor()



        cursor.execute("""

            CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(

                agent_id,

                content,

                tokenize='unicode61 remove_diacritics 1'

            )

        """)



        cursor.execute("""

            CREATE TABLE IF NOT EXISTS indexed_sessions (

                agent_id TEXT,

                session_file TEXT,

                indexed_at TEXT,

                PRIMARY KEY (agent_id, session_file)

            )

        """)



        conn.commit()

        conn.close()



    def rebuild_index(self, agent_id: str | None = None) -> int:

        """重建搜索索引"""

        if agent_id:

            agent_ids = [agent_id]

        else:

            if not SESSIONS_DIR.exists():

                return 0

            agent_ids = [

                f.stem for f in SESSIONS_DIR.glob("*.json")

                if not f.name.startswith(".")

            ]



        count = 0

        conn = sqlite3.connect(str(self.index_db))

        cursor = conn.cursor()



        for aid in agent_ids:

            for session_file in SESSIONS_DIR.glob(f"{aid}*.json"):

                if session_file.name.startswith("."):

                    continue



                try:

                    data = json.loads(session_file.read_text(encoding="utf-8"))

                    content = self._extract_searchable_content(data)



                    cursor.execute("""

                        INSERT OR REPLACE INTO sessions_fts (agent_id, content)

                        VALUES (?, ?)

                    """, (aid, content))



                    cursor.execute("""

                        INSERT OR REPLACE INTO indexed_sessions (agent_id, session_file, indexed_at)

                        VALUES (?, ?, ?)

                    """, (aid, session_file.name, datetime.now().isoformat()))



                    count += 1

                except (json.JSONDecodeError, Exception) as e:

                    print(f"[SearchIndex] Failed to index {session_file}: {e}")



        conn.commit()

        conn.close()



        return count



    def _extract_searchable_content(self, data: dict) -> str:

        """提取可搜索内容"""

        parts = []



        if data.get("system_prompt"):

            parts.append(data["system_prompt"])



        for msg in data.get("messages", []):

            role = msg.get("role", "")

            content = msg.get("content", "")



            if content:

                parts.append(f"{role}: {content}")



        return " | ".join(parts)



    def search(

        self,

        query: str,

        agent_id: str | None = None,

        limit: int = 10,

    ) -> list[SearchResult]:

        """搜索会话"""

        if not query.strip():

            return []



        conn = sqlite3.connect(str(self.index_db))

        conn.create_function("rank", 1, self._bm25_rank)

        cursor = conn.cursor()



        fts_query = self._prepare_fts_query(query)



        if agent_id:

            cursor.execute("""

                SELECT agent_id, session_file, content,

                       bm25(sessions_fts) as rank

                FROM sessions_fts

                WHERE sessions_fts MATCH ?

                  AND agent_id = ?

                ORDER BY rank

                LIMIT ?

            """, (fts_query, agent_id, limit))

        else:

            cursor.execute("""

                SELECT agent_id, session_file, content,

                       bm25(sessions_fts) as rank

                FROM sessions_fts

                WHERE sessions_fts MATCH ?

                ORDER BY rank

                LIMIT ?

            """, (fts_query, limit))



        results = []

        for row in cursor.fetchall():

            result = SearchResult(

                agent_id=row[0],

                session_file=row[1],

                snippet=self._create_snippet(row[2], query),

                score=abs(row[3]) if row[3] else 0.0,

                matched_at=datetime.now().isoformat(),

            )

            results.append(result)



        conn.close()

        return results



    def _prepare_fts_query(self, query: str) -> str:

        """准备 FTS5 查询"""

        terms = []

        for term in query.split():

            term = term.strip()

            if term:

                if len(term) > 2:

                    term = f"{term}*"

                terms.append(term)



        return " ".join(f'"{t}"' for t in terms if t)



    def _bm25_rank(self, score: float) -> float:

        """BM25 排序"""

        return -score



    def _create_snippet(self, content: str, query: str, context_chars: int = 100) -> str:

        """创建搜索结果片段"""

        query_lower = query.lower()

        content_lower = content.lower()



        pos = content_lower.find(query_lower)

        if pos == -1:

            for term in query.split():

                term = term.strip()

                if len(term) > 2:

                    pos = content_lower.find(term.lower())

                    if pos != -1:

                        break



        if pos == -1:

            return content[:context_chars * 2] + "..."



        start = max(0, pos - context_chars)

        end = min(len(content), pos + len(query) + context_chars)



        snippet = content[start:end]

        if start > 0:

            snippet = "..." + snippet

        if end < len(content):

            snippet = snippet + "..."



        return snippet



    def delete_from_index(self, agent_id: str, session_file: str) -> bool:

        """从索引中删除"""

        try:

            conn = sqlite3.connect(str(self.index_db))

            cursor = conn.cursor()



            cursor.execute("""

                DELETE FROM sessions_fts

                WHERE agent_id = ? AND rowid IN (

                    SELECT rowid FROM sessions_fts WHERE agent_id = ?

                )

            """, (agent_id, agent_id))



            cursor.execute("""

                DELETE FROM indexed_sessions

                WHERE agent_id = ? AND session_file = ?

            """, (agent_id, session_file))



            conn.commit()

            conn.close()

            return True

        except Exception as e:

            print(f"[SearchIndex] Failed to delete from index: {e}")

            return False





class SessionRecall:

    """跨会话召回引擎"""



    def __init__(self):

        self.search_engine = SessionSearchEngine()



    def recall(

        self,

        query: str,

        agent_id: str | None = None,

        limit: int = 5,

    ) -> list[dict]:

        """召回相关历史会话"""

        results = self.search_engine.search(query, agent_id, limit)



        recalled = []

        for result in results:

            session_path = SESSIONS_DIR / result.session_file

            if session_path.exists():

                try:

                    data = json.loads(session_path.read_text(encoding="utf-8"))

                    recalled.append({

                        "agent_id": result.agent_id,

                        "session_file": result.session_file,

                        "message_count": data.get("message_count", 0),

                        "updated_at": data.get("updated_at", ""),

                        "snippet": result.snippet,

                        "score": result.score,

                    })

                except (json.JSONDecodeError, Exception):

                    continue



        return recalled



    def rebuild(self, agent_id: str | None = None) -> int:

        """重建索引"""

        return self.search_engine.rebuild_index(agent_id)





_search_engine: SessionSearchEngine | None = None

_recall: SessionRecall | None = None





def get_search_engine() -> SessionSearchEngine:

    """获取全局搜索引擎单例"""

    global _search_engine

    if _search_engine is None:

        _search_engine = SessionSearchEngine()

    return _search_engine





def get_recall() -> SessionRecall:

    """获取全局召回引擎单例"""

    global _recall

    if _recall is None:

        _recall = SessionRecall()

    return _recall

