"""剧名库数据访问对象 - 管理 drama_names 表的 CRUD 操作。"""

from src.database import Database


class DramaDAO:
    """剧名库数据访问对象，提供剧名的添加、删除和查询功能。"""

    def __init__(self, db: Database):
        self._db = db

    def add(self, backend_id: int, name: str) -> bool:
        """添加剧名到指定后台的剧名库。

        使用 INSERT OR IGNORE 处理重复，通过 rowcount 判断是否实际插入。

        Args:
            backend_id: 后台 ID。
            name: 剧名。

        Returns:
            True 如果成功插入，False 如果剧名已存在。
        """
        conn = self._db.get_connection()
        cursor = conn.execute(
            "INSERT OR IGNORE INTO drama_names (backend_id, name) VALUES (?, ?)",
            (backend_id, name),
        )
        conn.commit()
        return cursor.rowcount > 0

    def add_batch(self, backend_id: int, names: list[str]) -> int:
        """批量添加剧名到指定后台的剧名库。

        Args:
            backend_id: 后台 ID。
            names: 剧名列表。

        Returns:
            实际新增的剧名数量。
        """
        conn = self._db.get_connection()
        inserted = 0
        for name in names:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO drama_names (backend_id, name) VALUES (?, ?)",
                (backend_id, name),
            )
            inserted += cursor.rowcount
        conn.commit()
        return inserted

    def delete(self, backend_id: int, name: str) -> None:
        """从指定后台的剧名库中删除剧名。

        Args:
            backend_id: 后台 ID。
            name: 要删除的剧名。
        """
        conn = self._db.get_connection()
        conn.execute(
            "DELETE FROM drama_names WHERE backend_id = ? AND name = ?",
            (backend_id, name),
        )
        conn.commit()

    def list_all(self, backend_id: int) -> list[str]:
        """返回指定后台的所有剧名，按名称排序。

        Args:
            backend_id: 后台 ID。

        Returns:
            剧名列表，按名称升序排列。
        """
        conn = self._db.get_connection()
        cursor = conn.execute(
            "SELECT name FROM drama_names WHERE backend_id = ? ORDER BY name",
            (backend_id,),
        )
        return [row[0] for row in cursor.fetchall()]

    def get_set(self, backend_id: int) -> set[str]:
        """返回指定后台的剧名集合，用于快速匹配。

        Args:
            backend_id: 后台 ID。

        Returns:
            剧名集合。
        """
        conn = self._db.get_connection()
        cursor = conn.execute(
            "SELECT name FROM drama_names WHERE backend_id = ?",
            (backend_id,),
        )
        return {row[0] for row in cursor.fetchall()}
