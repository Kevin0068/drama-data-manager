"""BackendDAO 单元测试 - 验证后台 CRUD 操作。"""

import sqlite3
import pytest
from src.database import Database
from src.dao.backend_dao import BackendDAO


@pytest.fixture
def db(tmp_path):
    """创建临时数据库实例。"""
    db_path = str(tmp_path / "test.db")
    database = Database(db_path)
    yield database
    database.close()


@pytest.fixture
def dao(db):
    """创建 BackendDAO 实例。"""
    return BackendDAO(db)


class TestCreate:
    """验证后台创建功能。"""

    def test_create_returns_id(self, dao):
        backend_id = dao.create("测试后台")
        assert isinstance(backend_id, int)
        assert backend_id > 0

    def test_create_multiple_returns_unique_ids(self, dao):
        id1 = dao.create("后台A")
        id2 = dao.create("后台B")
        assert id1 != id2

    def test_create_duplicate_name_raises(self, dao):
        dao.create("重复后台")
        with pytest.raises(sqlite3.IntegrityError):
            dao.create("重复后台")

    def test_created_backend_appears_in_list(self, dao):
        dao.create("新后台")
        backends = dao.list_all()
        names = [name for _, name in backends]
        assert "新后台" in names


class TestDelete:
    """验证后台删除功能（含级联删除）。"""

    def test_delete_removes_backend(self, dao):
        bid = dao.create("待删除")
        dao.delete(bid)
        backends = dao.list_all()
        ids = [id_ for id_, _ in backends]
        assert bid not in ids

    def test_delete_nonexistent_does_not_raise(self, dao):
        dao.delete(9999)  # 不存在的 ID，不应抛出异常

    def test_delete_cascades_drama_names(self, dao, db):
        """删除后台应级联删除关联的剧名。"""
        bid = dao.create("级联测试")
        conn = db.get_connection()
        conn.execute(
            "INSERT INTO drama_names (backend_id, name) VALUES (?, ?)",
            (bid, "剧名1"),
        )
        conn.commit()

        dao.delete(bid)

        count = conn.execute("SELECT COUNT(*) FROM drama_names WHERE backend_id = ?", (bid,)).fetchone()[0]
        assert count == 0

    def test_delete_cascades_months_and_deep_data(self, dao, db):
        """删除后台应级联删除月份及其下的导入数据和匹配结果。"""
        bid = dao.create("深度级联")
        conn = db.get_connection()
        conn.execute(
            "INSERT INTO months (backend_id, label) VALUES (?, ?)",
            (bid, "2024年01月"),
        )
        conn.commit()
        mid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            "INSERT INTO imported_headers (month_id, headers_json) VALUES (?, ?)",
            (mid, '["col1"]'),
        )
        conn.execute(
            "INSERT INTO imported_rows (month_id, row_index, row_json) VALUES (?, ?, ?)",
            (mid, 0, '["val1"]'),
        )
        conn.execute(
            "INSERT INTO match_results (month_id, matched_indices_json) VALUES (?, ?)",
            (mid, "[0]"),
        )
        conn.commit()

        dao.delete(bid)

        for table in ("months", "imported_headers", "imported_rows", "match_results"):
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            assert count == 0, f"{table} should be empty after backend deletion"


class TestListAll:
    """验证后台列表查询功能。"""

    def test_empty_list(self, dao):
        assert dao.list_all() == []

    def test_list_returns_all_backends(self, dao):
        dao.create("后台A")
        dao.create("后台B")
        dao.create("后台C")
        backends = dao.list_all()
        assert len(backends) == 3
        names = [name for _, name in backends]
        assert names == ["后台A", "后台B", "后台C"]

    def test_list_returns_tuples_of_id_and_name(self, dao):
        bid = dao.create("验证格式")
        backends = dao.list_all()
        assert len(backends) == 1
        assert backends[0] == (bid, "验证格式")

    def test_list_ordered_by_id(self, dao):
        id1 = dao.create("第一个")
        id2 = dao.create("第二个")
        backends = dao.list_all()
        assert backends[0][0] < backends[1][0]
