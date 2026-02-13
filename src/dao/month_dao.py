"""月份数据访问对象 - 管理 months 表的 CRUD 操作。"""

import sqlite3
from src.database import Database


class MonthDAO:
    """月份数据访问对象，提供月份空间的创建、删除和查询功能。"""

    def __init__(self, db: Database):
        self._db = db

    def create(self, backend_id: int, label: str) -> int:
        """创建月份空间，返回新月份的 ID。

        Args:
            backend_id: 所属后台 ID。
            label: 月份标签（如 "2024年01月"），同一后台内必须唯一。

        Returns:
            新创建月份的 ID。

        Raises:
            ValueError: 该后台下已存在相同标签的月份。
        """
        conn = self._db.get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO months (backend_id, label) VALUES (?, ?)",
                (backend_id, label),
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"月份 '{label}' 已存在")

    def delete(self, month_id: int) -> None:
        """删除月份及其所有关联数据（通过 ON DELETE CASCADE 级联删除）。

        Args:
            month_id: 要删除的月份 ID。
        """
        conn = self._db.get_connection()
        conn.execute("DELETE FROM months WHERE id = ?", (month_id,))
        conn.commit()

    def list_all(self, backend_id: int) -> list[tuple[int, str]]:
        """返回指定后台的所有月份列表。

        Args:
            backend_id: 后台 ID。

        Returns:
            该后台所有月份的 (id, label) 元组列表，按 ID 升序排列。
        """
        conn = self._db.get_connection()
        cursor = conn.execute(
            "SELECT id, label FROM months WHERE backend_id = ? ORDER BY id",
            (backend_id,),
        )
        return cursor.fetchall()
