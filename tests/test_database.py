"""Database 类的单元测试 - 验证表创建和外键级联删除。"""

import sqlite3
import pytest
from src.database import Database


@pytest.fixture
def db(tmp_path):
    """创建临时数据库实例。"""
    db_path = str(tmp_path / "test.db")
    database = Database(db_path)
    yield database
    database.close()


class TestTableCreation:
    """验证所有 6 张表被正确创建。"""

    EXPECTED_TABLES = {
        "backends",
        "drama_names",
        "months",
        "imported_headers",
        "imported_rows",
        "match_results",
    }

    def test_all_tables_exist(self, db):
        conn = db.get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = {row[0] for row in cursor.fetchall()}
        assert tables == self.EXPECTED_TABLES

    def test_foreign_keys_enabled(self, db):
        conn = db.get_connection()
        result = conn.execute("PRAGMA foreign_keys").fetchone()
        assert result[0] == 1


class TestCascadeDelete:
    """验证外键级联删除行为。"""

    def _insert_backend(self, conn, name="测试后台"):
        conn.execute("INSERT INTO backends (name) VALUES (?)", (name,))
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    def _insert_month(self, conn, backend_id, label="2024年01月"):
        conn.execute(
            "INSERT INTO months (backend_id, label) VALUES (?, ?)",
            (backend_id, label),
        )
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    def test_delete_backend_cascades_drama_names(self, db):
        conn = db.get_connection()
        bid = self._insert_backend(conn)
        conn.execute(
            "INSERT INTO drama_names (backend_id, name) VALUES (?, ?)", (bid, "剧名A")
        )
        conn.commit()

        conn.execute("DELETE FROM backends WHERE id = ?", (bid,))
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM drama_names").fetchone()[0]
        assert count == 0

    def test_delete_backend_cascades_months(self, db):
        conn = db.get_connection()
        bid = self._insert_backend(conn)
        self._insert_month(conn, bid)

        conn.execute("DELETE FROM backends WHERE id = ?", (bid,))
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM months").fetchone()[0]
        assert count == 0

    def test_delete_month_cascades_imported_headers(self, db):
        conn = db.get_connection()
        bid = self._insert_backend(conn)
        mid = self._insert_month(conn, bid)
        conn.execute(
            "INSERT INTO imported_headers (month_id, headers_json) VALUES (?, ?)",
            (mid, '["col1","col2"]'),
        )
        conn.commit()

        conn.execute("DELETE FROM months WHERE id = ?", (mid,))
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM imported_headers").fetchone()[0]
        assert count == 0

    def test_delete_month_cascades_imported_rows(self, db):
        conn = db.get_connection()
        bid = self._insert_backend(conn)
        mid = self._insert_month(conn, bid)
        conn.execute(
            "INSERT INTO imported_rows (month_id, row_index, row_json) VALUES (?, ?, ?)",
            (mid, 0, '["val1","val2"]'),
        )
        conn.commit()

        conn.execute("DELETE FROM months WHERE id = ?", (mid,))
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM imported_rows").fetchone()[0]
        assert count == 0

    def test_delete_month_cascades_match_results(self, db):
        conn = db.get_connection()
        bid = self._insert_backend(conn)
        mid = self._insert_month(conn, bid)
        conn.execute(
            "INSERT INTO match_results (month_id, matched_indices_json) VALUES (?, ?)",
            (mid, "[0,1]"),
        )
        conn.commit()

        conn.execute("DELETE FROM months WHERE id = ?", (mid,))
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM match_results").fetchone()[0]
        assert count == 0

    def test_deep_cascade_backend_to_imported_data(self, db):
        """删除后台应级联删除月份，进而级联删除导入数据。"""
        conn = db.get_connection()
        bid = self._insert_backend(conn)
        mid = self._insert_month(conn, bid)
        conn.execute(
            "INSERT INTO imported_headers (month_id, headers_json) VALUES (?, ?)",
            (mid, '["h1"]'),
        )
        conn.execute(
            "INSERT INTO imported_rows (month_id, row_index, row_json) VALUES (?, ?, ?)",
            (mid, 0, '["v1"]'),
        )
        conn.execute(
            "INSERT INTO match_results (month_id, matched_indices_json) VALUES (?, ?)",
            (mid, "[0]"),
        )
        conn.commit()

        conn.execute("DELETE FROM backends WHERE id = ?", (bid,))
        conn.commit()

        for table in ("months", "imported_headers", "imported_rows", "match_results"):
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            assert count == 0, f"{table} should be empty after backend deletion"


class TestGetConnectionAndClose:
    """验证连接获取和关闭。"""

    def test_get_connection_returns_sqlite_connection(self, db):
        conn = db.get_connection()
        assert isinstance(conn, sqlite3.Connection)

    def test_close_closes_connection(self, tmp_path):
        db_path = str(tmp_path / "close_test.db")
        database = Database(db_path)
        database.close()
        with pytest.raises(Exception):
            database.get_connection().execute("SELECT 1")
