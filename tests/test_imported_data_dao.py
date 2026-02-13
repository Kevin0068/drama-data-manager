"""ImportedDataDAO 单元测试 - 验证导入数据和匹配结果的保存与查询功能。"""

import pytest
from src.database import Database
from src.dao.backend_dao import BackendDAO
from src.dao.month_dao import MonthDAO
from src.dao.imported_data_dao import ImportedDataDAO


@pytest.fixture
def db(tmp_path):
    """创建临时数据库实例。"""
    db_path = str(tmp_path / "test.db")
    database = Database(db_path)
    yield database
    database.close()


@pytest.fixture
def month_id(db):
    """创建测试后台和月份，返回月份 ID。"""
    bid = BackendDAO(db).create("测试后台")
    return MonthDAO(db).create(bid, "2024年01月")


@pytest.fixture
def dao(db):
    """创建 ImportedDataDAO 实例。"""
    return ImportedDataDAO(db)


class TestSaveDataAndGetHeaders:
    """验证 save_data 和 get_headers。"""

    def test_save_and_get_headers(self, dao, month_id):
        headers = ["姓名", "金额", "合集名称"]
        dao.save_data(month_id, headers, [])
        assert dao.get_headers(month_id) == headers

    def test_get_headers_no_data(self, dao, month_id):
        assert dao.get_headers(month_id) == []

    def test_save_data_replaces_old_data(self, dao, month_id):
        dao.save_data(month_id, ["旧列"], [["旧值"]])
        dao.save_data(month_id, ["新列A", "新列B"], [["a", "b"]])
        assert dao.get_headers(month_id) == ["新列A", "新列B"]
        rows = dao.get_all_rows(month_id)
        assert rows == [["a", "b"]]


class TestGetAllRows:
    """验证 get_all_rows。"""

    def test_get_rows_preserves_order(self, dao, month_id):
        rows = [["r0c0", "r0c1"], ["r1c0", "r1c1"], ["r2c0", "r2c1"]]
        dao.save_data(month_id, ["c0", "c1"], rows)
        assert dao.get_all_rows(month_id) == rows

    def test_get_rows_empty(self, dao, month_id):
        assert dao.get_all_rows(month_id) == []

    def test_rows_with_mixed_types(self, dao, month_id):
        rows = [["文本", 123, 45.6, None, True]]
        dao.save_data(month_id, ["col"], rows)
        assert dao.get_all_rows(month_id) == rows


class TestMatchResults:
    """验证 save_match_results 和 get_match_results。"""

    def test_save_and_get_match_results(self, dao, month_id):
        dao.save_match_results(month_id, [0, 2, 5])
        assert dao.get_match_results(month_id) == [0, 2, 5]

    def test_get_match_results_no_data(self, dao, month_id):
        assert dao.get_match_results(month_id) == []

    def test_save_match_results_replaces(self, dao, month_id):
        dao.save_match_results(month_id, [0, 1])
        dao.save_match_results(month_id, [3, 4, 5])
        assert dao.get_match_results(month_id) == [3, 4, 5]

    def test_empty_match_results(self, dao, month_id):
        dao.save_match_results(month_id, [])
        assert dao.get_match_results(month_id) == []


class TestHasData:
    """验证 has_data。"""

    def test_has_data_false_initially(self, dao, month_id):
        assert dao.has_data(month_id) is False

    def test_has_data_true_after_save(self, dao, month_id):
        dao.save_data(month_id, ["col"], [])
        assert dao.has_data(month_id) is True

    def test_has_data_true_after_reimport(self, dao, month_id):
        dao.save_data(month_id, ["old"], [["v"]])
        dao.save_data(month_id, ["new"], [["w"]])
        assert dao.has_data(month_id) is True
