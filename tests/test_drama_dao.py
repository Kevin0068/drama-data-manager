"""DramaDAO 单元测试 - 验证剧名库 CRUD 操作。"""

import pytest
from src.database import Database
from src.dao.backend_dao import BackendDAO
from src.dao.drama_dao import DramaDAO


@pytest.fixture
def db(tmp_path):
    """创建临时数据库实例。"""
    db_path = str(tmp_path / "test.db")
    database = Database(db_path)
    yield database
    database.close()


@pytest.fixture
def backend_id(db):
    """创建一个后台并返回其 ID。"""
    dao = BackendDAO(db)
    return dao.create("测试后台")


@pytest.fixture
def dao(db):
    """创建 DramaDAO 实例。"""
    return DramaDAO(db)


class TestAdd:
    """验证单个剧名添加功能。"""

    def test_add_returns_true_on_success(self, dao, backend_id):
        assert dao.add(backend_id, "琅琊榜") is True

    def test_add_duplicate_returns_false(self, dao, backend_id):
        dao.add(backend_id, "琅琊榜")
        assert dao.add(backend_id, "琅琊榜") is False

    def test_added_drama_appears_in_list(self, dao, backend_id):
        dao.add(backend_id, "甄嬛传")
        assert "甄嬛传" in dao.list_all(backend_id)

    def test_same_name_different_backends(self, db, dao):
        """不同后台可以有相同剧名。"""
        b_dao = BackendDAO(db)
        bid1 = b_dao.create("后台A")
        bid2 = b_dao.create("后台B")
        assert dao.add(bid1, "琅琊榜") is True
        assert dao.add(bid2, "琅琊榜") is True


class TestAddBatch:
    """验证批量添加功能。"""

    def test_batch_add_returns_count(self, dao, backend_id):
        count = dao.add_batch(backend_id, ["剧名A", "剧名B", "剧名C"])
        assert count == 3

    def test_batch_add_with_duplicates_in_input(self, dao, backend_id):
        count = dao.add_batch(backend_id, ["剧名A", "剧名A", "剧名B"])
        assert count == 2

    def test_batch_add_with_existing_names(self, dao, backend_id):
        dao.add(backend_id, "已存在")
        count = dao.add_batch(backend_id, ["已存在", "新剧名"])
        assert count == 1

    def test_batch_add_empty_list(self, dao, backend_id):
        count = dao.add_batch(backend_id, [])
        assert count == 0

    def test_batch_add_all_existing(self, dao, backend_id):
        dao.add_batch(backend_id, ["A", "B"])
        count = dao.add_batch(backend_id, ["A", "B"])
        assert count == 0


class TestDelete:
    """验证剧名删除功能。"""

    def test_delete_removes_drama(self, dao, backend_id):
        dao.add(backend_id, "待删除")
        dao.delete(backend_id, "待删除")
        assert "待删除" not in dao.list_all(backend_id)

    def test_delete_nonexistent_does_not_raise(self, dao, backend_id):
        dao.delete(backend_id, "不存在的剧名")  # 不应抛出异常

    def test_delete_only_affects_target_backend(self, db, dao):
        """删除只影响指定后台的剧名。"""
        b_dao = BackendDAO(db)
        bid1 = b_dao.create("后台X")
        bid2 = b_dao.create("后台Y")
        dao.add(bid1, "共同剧名")
        dao.add(bid2, "共同剧名")
        dao.delete(bid1, "共同剧名")
        assert "共同剧名" not in dao.list_all(bid1)
        assert "共同剧名" in dao.list_all(bid2)


class TestListAll:
    """验证剧名列表查询功能。"""

    def test_empty_list(self, dao, backend_id):
        assert dao.list_all(backend_id) == []

    def test_list_returns_sorted_names(self, dao, backend_id):
        dao.add_batch(backend_id, ["C剧", "A剧", "B剧"])
        assert dao.list_all(backend_id) == ["A剧", "B剧", "C剧"]

    def test_list_only_returns_target_backend(self, db, dao):
        """只返回指定后台的剧名。"""
        b_dao = BackendDAO(db)
        bid1 = b_dao.create("后台1")
        bid2 = b_dao.create("后台2")
        dao.add(bid1, "后台1的剧")
        dao.add(bid2, "后台2的剧")
        assert dao.list_all(bid1) == ["后台1的剧"]
        assert dao.list_all(bid2) == ["后台2的剧"]


class TestGetSet:
    """验证剧名集合查询功能。"""

    def test_empty_set(self, dao, backend_id):
        assert dao.get_set(backend_id) == set()

    def test_get_set_returns_all_names(self, dao, backend_id):
        dao.add_batch(backend_id, ["剧A", "剧B", "剧C"])
        assert dao.get_set(backend_id) == {"剧A", "剧B", "剧C"}

    def test_get_set_only_returns_target_backend(self, db, dao):
        """只返回指定后台的剧名集合。"""
        b_dao = BackendDAO(db)
        bid1 = b_dao.create("集合后台1")
        bid2 = b_dao.create("集合后台2")
        dao.add(bid1, "独有剧名")
        dao.add(bid2, "另一个剧名")
        assert dao.get_set(bid1) == {"独有剧名"}
