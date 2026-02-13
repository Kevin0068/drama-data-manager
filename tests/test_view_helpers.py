"""view_helpers 单元测试。"""

import pytest
from src.view_helpers import filter_rows, compute_column_sums


class TestFilterRows:
    """测试 filter_rows 函数。"""

    def test_all_mode_returns_all_rows(self):
        rows = [["a", 1], ["b", 2], ["c", 3]]
        result = filter_rows(rows, [0, 2], "all")
        assert result == rows

    def test_matched_mode_returns_only_matched(self):
        rows = [["a", 1], ["b", 2], ["c", 3]]
        result = filter_rows(rows, [0, 2], "matched")
        assert result == [["a", 1], ["c", 3]]

    def test_unmatched_mode_returns_only_unmatched(self):
        rows = [["a", 1], ["b", 2], ["c", 3]]
        result = filter_rows(rows, [0, 2], "unmatched")
        assert result == [["b", 2]]

    def test_empty_rows(self):
        assert filter_rows([], [0], "all") == []
        assert filter_rows([], [0], "matched") == []
        assert filter_rows([], [0], "unmatched") == []

    def test_empty_matched_indices(self):
        rows = [["a", 1], ["b", 2]]
        assert filter_rows(rows, [], "matched") == []
        assert filter_rows(rows, [], "unmatched") == rows

    def test_all_matched(self):
        rows = [["a", 1], ["b", 2]]
        result = filter_rows(rows, [0, 1], "matched")
        assert result == rows

    def test_all_unmatched(self):
        rows = [["a", 1], ["b", 2]]
        result = filter_rows(rows, [0, 1], "unmatched")
        assert result == []

    def test_preserves_full_row_data(self):
        """验证视图切换时保留所有列的完整数据（Requirements 6.4）。"""
        rows = [["剧名A", 100, 200, "备注"], ["剧名B", 300, 400, "备注2"]]
        result = filter_rows(rows, [0], "matched")
        assert result == [["剧名A", 100, 200, "备注"]]

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            filter_rows([["a"]], [], "invalid")


class TestComputeColumnSums:
    """测试 compute_column_sums 函数。"""

    def test_numeric_columns(self):
        rows = [[1, 2, 3], [4, 5, 6]]
        result = compute_column_sums(rows, 3)
        assert result == [5.0, 7.0, 9.0]

    def test_non_numeric_columns(self):
        rows = [["a", "b"], ["c", "d"]]
        result = compute_column_sums(rows, 2)
        assert result == ["", ""]

    def test_mixed_columns(self):
        rows = [["剧名A", 100, 200], ["剧名B", 300, 400]]
        result = compute_column_sums(rows, 3)
        assert result == ["", 400.0, 600.0]

    def test_empty_rows(self):
        result = compute_column_sums([], 3)
        assert result == ["", "", ""]

    def test_none_values_skipped(self):
        rows = [[None, 10], [None, 20]]
        result = compute_column_sums(rows, 2)
        assert result == ["", 30.0]

    def test_mixed_numeric_and_none(self):
        rows = [[10, None], [None, 20], [30, 40]]
        result = compute_column_sums(rows, 2)
        assert result == [40.0, 60.0]

    def test_float_values(self):
        rows = [[1.5, 2.5], [3.5, 4.5]]
        result = compute_column_sums(rows, 2)
        assert result == [5.0, 7.0]

    def test_short_rows_handled(self):
        """行长度小于 num_columns 时不报错。"""
        rows = [[1], [2, 3]]
        result = compute_column_sums(rows, 3)
        assert result == [3.0, 3.0, ""]

    def test_zero_columns(self):
        result = compute_column_sums([[1, 2]], 0)
        assert result == []
