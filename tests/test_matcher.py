"""Unit tests for the drama matcher."""

from src.matcher import match_dramas
from src.models import MatchResult


class TestMatchDramasBasic:
    """Basic matching scenarios."""

    def test_basic_matching(self):
        master = [(2, "琅琊榜"), (3, "甄嬛传"), (4, "庆余年")]
        lookup = {"琅琊榜", "庆余年"}

        result = match_dramas(master, lookup)

        assert result.matched_rows == [2, 4]
        assert result.matched_names == ["琅琊榜", "庆余年"]
        assert result.match_count == 2
        assert result.total_master == 3
        assert result.total_lookup == 2

    def test_single_match(self):
        master = [(2, "琅琊榜"), (3, "甄嬛传")]
        lookup = {"甄嬛传"}

        result = match_dramas(master, lookup)

        assert result.matched_rows == [3]
        assert result.matched_names == ["甄嬛传"]
        assert result.match_count == 1


class TestMatchDramasNoMatch:
    """No matches found scenarios."""

    def test_no_matches(self):
        master = [(2, "琅琊榜"), (3, "甄嬛传")]
        lookup = {"庆余年", "长安十二时辰"}

        result = match_dramas(master, lookup)

        assert result.matched_rows == []
        assert result.matched_names == []
        assert result.match_count == 0
        assert result.total_master == 2
        assert result.total_lookup == 2

    def test_empty_master(self):
        result = match_dramas([], {"琅琊榜"})

        assert result.matched_rows == []
        assert result.match_count == 0
        assert result.total_master == 0

    def test_empty_lookup(self):
        master = [(2, "琅琊榜")]
        result = match_dramas(master, set())

        assert result.matched_rows == []
        assert result.match_count == 0
        assert result.total_lookup == 0

    def test_both_empty(self):
        result = match_dramas([], set())

        assert result.matched_rows == []
        assert result.match_count == 0
        assert result.total_master == 0
        assert result.total_lookup == 0


class TestMatchDramasAllMatch:
    """All items match scenarios."""

    def test_all_match(self):
        master = [(2, "琅琊榜"), (3, "甄嬛传"), (4, "庆余年")]
        lookup = {"琅琊榜", "甄嬛传", "庆余年"}

        result = match_dramas(master, lookup)

        assert result.matched_rows == [2, 3, 4]
        assert set(result.matched_names) == {"琅琊榜", "甄嬛传", "庆余年"}
        assert result.match_count == 3

    def test_lookup_superset(self):
        master = [(2, "琅琊榜"), (3, "甄嬛传")]
        lookup = {"琅琊榜", "甄嬛传", "庆余年", "长安十二时辰"}

        result = match_dramas(master, lookup)

        assert result.match_count == 2
        assert result.total_lookup == 4


class TestMatchDramasWhitespace:
    """Whitespace handling in matching."""

    def test_master_has_leading_trailing_spaces(self):
        master = [(2, "  琅琊榜  "), (3, " 甄嬛传")]
        lookup = {"琅琊榜", "甄嬛传"}

        result = match_dramas(master, lookup)

        assert result.matched_rows == [2, 3]
        assert result.matched_names == ["琅琊榜", "甄嬛传"]

    def test_lookup_has_leading_trailing_spaces(self):
        master = [(2, "琅琊榜"), (3, "甄嬛传")]
        lookup = {"  琅琊榜  ", " 甄嬛传 "}

        result = match_dramas(master, lookup)

        assert result.matched_rows == [2, 3]
        assert result.matched_names == ["琅琊榜", "甄嬛传"]

    def test_both_have_spaces(self):
        master = [(2, " 琅琊榜 "), (3, "  甄嬛传  ")]
        lookup = {"  琅琊榜  ", " 甄嬛传 "}

        result = match_dramas(master, lookup)

        assert result.matched_rows == [2, 3]

    def test_internal_spaces_preserved(self):
        """Internal spaces should not be stripped - only leading/trailing."""
        master = [(2, "长安 十二时辰")]
        lookup = {"长安十二时辰"}

        result = match_dramas(master, lookup)

        assert result.matched_rows == []
        assert result.match_count == 0
