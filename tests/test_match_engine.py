"""MatchEngine 单元测试。"""

import pytest
from src.match_engine import MatchEngine


class TestMatch:
    """测试 match 静态方法。"""

    def test_basic_match(self):
        rows = [["琅琊榜", "古装"], ["甄嬛传", "古装"], ["未知剧", "现代"]]
        drama_set = {"琅琊榜", "甄嬛传"}
        result = MatchEngine.match(rows, 0, drama_set)
        assert result == [0, 1]

    def test_no_match(self):
        rows = [["未知剧A", "古装"], ["未知剧B", "现代"]]
        drama_set = {"琅琊榜"}
        result = MatchEngine.match(rows, 0, drama_set)
        assert result == []

    def test_all_match(self):
        rows = [["琅琊榜", "古装"], ["甄嬛传", "古装"]]
        drama_set = {"琅琊榜", "甄嬛传"}
        result = MatchEngine.match(rows, 0, drama_set)
        assert result == [0, 1]

    def test_empty_rows(self):
        result = MatchEngine.match([], 0, {"琅琊榜"})
        assert result == []

    def test_empty_drama_set(self):
        rows = [["琅琊榜", "古装"]]
        result = MatchEngine.match(rows, 0, set())
        assert result == []

    def test_strip_whitespace(self):
        """验证去除首尾空格后精确匹配（Requirements 5.5）。"""
        rows = [["  琅琊榜  ", "古装"], ["甄嬛传 ", "古装"], [" 未知剧", "现代"]]
        drama_set = {"琅琊榜", "甄嬛传"}
        result = MatchEngine.match(rows, 0, drama_set)
        assert result == [0, 1]

    def test_non_first_column(self):
        rows = [["古装", "琅琊榜"], ["现代", "未知剧"]]
        drama_set = {"琅琊榜"}
        result = MatchEngine.match(rows, 1, drama_set)
        assert result == [0]

    def test_col_index_out_of_range(self):
        """列索引超出行长度时，该行不匹配。"""
        rows = [["琅琊榜"]]
        drama_set = {"琅琊榜"}
        result = MatchEngine.match(rows, 5, drama_set)
        assert result == []

    def test_non_string_values_converted(self):
        """非字符串值应被转换为字符串后匹配。"""
        rows = [[123, "数据"], [456, "数据"]]
        drama_set = {"123"}
        result = MatchEngine.match(rows, 0, drama_set)
        assert result == [0]


class TestFindColumnIndex:
    """测试 find_column_index 静态方法。"""

    def test_find_default_target(self):
        headers = ["序号", "合集名称", "播放量"]
        result = MatchEngine.find_column_index(headers)
        assert result == 1

    def test_find_custom_target(self):
        headers = ["序号", "剧名", "播放量"]
        result = MatchEngine.find_column_index(headers, target="剧名")
        assert result == 1

    def test_target_not_found(self):
        headers = ["序号", "播放量"]
        with pytest.raises(ValueError, match="未找到目标列"):
            MatchEngine.find_column_index(headers)

    def test_strip_header_whitespace(self):
        """表头有空格时也能找到。"""
        headers = ["序号", "  合集名称  ", "播放量"]
        result = MatchEngine.find_column_index(headers)
        assert result == 1

    def test_empty_headers(self):
        with pytest.raises(ValueError):
            MatchEngine.find_column_index([])

    def test_first_column(self):
        headers = ["合集名称", "播放量"]
        result = MatchEngine.find_column_index(headers)
        assert result == 0
