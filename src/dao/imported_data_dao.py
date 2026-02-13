"""导入数据访问对象 - 管理 imported_headers、imported_rows、match_results 表。"""

import json
from src.database import Database


class ImportedDataDAO:
    """导入数据访问对象，提供导入数据和匹配结果的保存与查询功能。"""

    def __init__(self, db: Database):
        self._db = db

    def save_data(self, month_id: int, headers: list[str], rows: list[list]) -> None:
        """保存导入数据（先清除旧数据再写入）。

        Args:
            month_id: 月份 ID。
            headers: 表头列名列表。
            rows: 每行数据列表的列表。
        """
        conn = self._db.get_connection()
        conn.execute("DELETE FROM imported_rows WHERE month_id = ?", (month_id,))
        conn.execute("DELETE FROM imported_headers WHERE month_id = ?", (month_id,))

        conn.execute(
            "INSERT INTO imported_headers (month_id, headers_json) VALUES (?, ?)",
            (month_id, json.dumps(headers, ensure_ascii=False)),
        )
        for idx, row in enumerate(rows):
            conn.execute(
                "INSERT INTO imported_rows (month_id, row_index, row_json) VALUES (?, ?, ?)",
                (month_id, idx, json.dumps(row, ensure_ascii=False)),
            )
        conn.commit()

    def get_headers(self, month_id: int) -> list[str]:
        """获取表头。

        Args:
            month_id: 月份 ID。

        Returns:
            表头列名列表，无数据时返回空列表。
        """
        conn = self._db.get_connection()
        row = conn.execute(
            "SELECT headers_json FROM imported_headers WHERE month_id = ?",
            (month_id,),
        ).fetchone()
        if row is None:
            return []
        return json.loads(row[0])

    def get_all_rows(self, month_id: int) -> list[list]:
        """获取所有行数据，按 row_index 排序。

        Args:
            month_id: 月份 ID。

        Returns:
            行数据列表，每行为一个列表。
        """
        conn = self._db.get_connection()
        cursor = conn.execute(
            "SELECT row_json FROM imported_rows WHERE month_id = ? ORDER BY row_index",
            (month_id,),
        )
        return [json.loads(r[0]) for r in cursor.fetchall()]

    def save_match_results(self, month_id: int, matched_indices: list[int]) -> None:
        """保存匹配结果（行索引列表）。

        Args:
            month_id: 月份 ID。
            matched_indices: 匹配行的索引列表。
        """
        conn = self._db.get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO match_results (month_id, matched_indices_json) VALUES (?, ?)",
            (month_id, json.dumps(matched_indices)),
        )
        conn.commit()

    def get_match_results(self, month_id: int) -> list[int]:
        """获取匹配结果行索引列表。

        Args:
            month_id: 月份 ID。

        Returns:
            匹配行索引列表，无结果时返回空列表。
        """
        conn = self._db.get_connection()
        row = conn.execute(
            "SELECT matched_indices_json FROM match_results WHERE month_id = ?",
            (month_id,),
        ).fetchone()
        if row is None:
            return []
        return json.loads(row[0])

    def has_data(self, month_id: int) -> bool:
        """检查月份是否有导入数据。

        Args:
            month_id: 月份 ID。

        Returns:
            True 如果该月份有导入数据。
        """
        conn = self._db.get_connection()
        row = conn.execute(
            "SELECT 1 FROM imported_headers WHERE month_id = ?",
            (month_id,),
        ).fetchone()
        return row is not None
