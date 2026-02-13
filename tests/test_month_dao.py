"""MonthDAO 单元测试 - 验证月份空间的创建、删除和查询功能。"""

import pytest
from src.database import Database
from src.dao.backend_dao import BackendDAO
from src.dao.month_dao import MonthDAO


@pytest.fixture
def db(tmp_path):
    """创建临时数据库实例。"""
    db_path = str(tmp_path / "test.db")
    database = Database(db_path)
    yield database
    database.close()


@pytest.fixture
def backend_id(db):
    """创建一个测试后台并返回其 ID。"""
    dao = BackendDAO(db)
    return dao.create("测试后台")


@pytest.fixture
def month_dao(db):
    """创建 MonthDAO 实例。"""
    return MonthDAO(db)


class TestCreate:
    """验证月份创建功能。"""

    def test_create_returns_id(self, month_dao, backend_id):
        mid = month_dao.create(backend_id, "2024年01月")
        assert isinstance(mid, int)
        assert mid > 0

    def test_create_multiple_months(self, month_dao, backend_id):
        id1 = month_dao.create(backend_id, "2024年01月")
        id2 = month_dao.create(backend_id, "2024年02月")
        assert id1 != id2

    def test_create_duplicate_raises_value_error(self, month_dao, backend_id):
        month_dao.create(backend_id, "2024年01月")
        with pytest.raises(ValueError, match="已存在"):
            month_dao.create(backend_id, "2024年01月")

    def test_same_label_different_backends(self, db, month_dao):
        """不同后台可以有相同标签的月份。"""
        dao = BackendDAO(db)
        bid1 = dao.create("后台A")
        bid2 = dao.create("后台B")
        id1 = month_dao.create(bid1, "2024年01月")
        id2 = month_dao.create(bid2, "2024年01月")
        assert id1 != id2


class TestDelete:
    """验证月份删除功能。"""

    def test_delete_removes_month(self, month_dao, backend_id):
        mid = month_dao.create(backend_id, "2024年01月")
        month_dao.delete(mid)
        assert month_dao.list_all(backend_id) == []

    def test_delete_nonexistent_is_noop(self, month_dao):
        month_dao.delete(9999)  # 不应抛出异常

    def test_delete_cascades_imported_data(self, db, month_dao, backend_id):
        """删除月份应级联删除其导入数据。"""
        mid = month_dao.create(backend_id, "2024年01月")
        conn = db.get_connection()
        conn.execute(
            "INSERT INTO imported_headers (month_id, headers_json) VALUES (?, ?)",
            (mid, '["col1","col2"]'),
        )
        conn.execute(
            "INSERT INTO imported_rows (month_id, row_index, row_json) VALUES (?, ?, ?)",
            (mid, 0, '["v1","v2"]'),
        )
        conn.execute(
            "INSERT INTO match_results (month_id, matched_indices_json) VALUES (?, ?)",
            (mid, "[0]"),
        )
        conn.commit()

        month_dao.delete(mid)

        for table in ("imported_headers", "imported_rows", "match_results"):
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            assert count == 0, f"{table} should be empty after month deletion"


class TestListAll:
    """验证月份列表查询功能。"""

    def test_list_empty(self, month_dao, backend_id):
        assert month_dao.list_all(backend_id) == []

    def test_list_returns_tuples_ordered_by_id(self, month_dao, backend_id):
        id1 = month_dao.create(backend_id, "2024年01月")
        id2 = month_dao.create(backend_id, "2024年02月")
        result = month_dao.list_all(backend_id)
        assert result == [(id1, "2024年01月"), (id2, "2024年02月")]

    def test_list_only_returns_months_for_given_backend(self, db, month_dao):
        """list_all 只返回指定后台的月份。"""
        dao = BackendDAO(db)
        bid1 = dao.create("后台A")
        bid2 = dao.create("后台B")
        month_dao.create(bid1, "2024年01月")
        month_dao.create(bid2, "2024年02月")
        result = month_dao.list_all(bid1)
        assert len(result) == 1
        assert result[0][1] == "2024年01月"
