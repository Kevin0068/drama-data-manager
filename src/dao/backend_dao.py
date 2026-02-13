"""后台数据访问对象 - 管理 backends 表的 CRUD 操作。"""

import sqlite3
from src.database import Database


class BackendDAO:
    """后台数据访问对象，提供后台的创建、删除和查询功能。"""

    def __init__(self, db: Database):
        self._db = db

    def create(self, name: str) -> int:
        """创建后台，返回新后台的 ID。

        Args:
            name: 后台名称，必须唯一。

        Returns:
            新创建后台的 ID。

        Raises:
            sqlite3.IntegrityError: 后台名称已存在。
        """
        conn = self._db.get_connection()
        cursor = conn.execute(
            "INSERT INTO backends (name) VALUES (?)", (name,)
        )
        conn.commit()
        return cursor.lastrowid

    def delete(self, backend_id: int) -> None:
        """删除后台及其所有关联数据（通过 ON DELETE CASCADE 级联删除）。

        Args:
            backend_id: 要删除的后台 ID。
        """
        conn = self._db.get_connection()
        conn.execute("DELETE FROM backends WHERE id = ?", (backend_id,))
        conn.commit()

    def list_all(self) -> list[tuple[int, str]]:
        """返回所有后台列表。

        Returns:
            所有后台的 (id, name) 元组列表。
        """
        conn = self._db.get_connection()
        cursor = conn.execute("SELECT id, name FROM backends ORDER BY id")
        return cursor.fetchall()
