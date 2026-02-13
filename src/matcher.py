"""剧名匹配器：比对A文档和B文档中的剧名。"""

from src.models import MatchResult


def match_dramas(
    master_names: list[tuple[int, str]], lookup_names: set[str]
) -> MatchResult:
    """
    在主表剧名中查找所有出现在查找列表中的剧名，返回匹配结果。

    使用set进行O(1)查找，总时间复杂度O(n+m)。
    比对时去除首尾空格后进行精确匹配。

    Args:
        master_names: A文档中的(行号, 剧名)元组列表
        lookup_names: B文档中的剧名集合（已去除首尾空格）

    Returns:
        MatchResult 包含匹配行号、匹配剧名、统计信息
    """
    # Normalize lookup names by stripping whitespace
    normalized_lookup = {name.strip() for name in lookup_names}

    matched_rows = []
    matched_names = []

    for row_num, name in master_names:
        stripped = name.strip()
        if stripped in normalized_lookup:
            matched_rows.append(row_num)
            matched_names.append(stripped)

    return MatchResult(
        matched_rows=matched_rows,
        matched_names=matched_names,
        total_master=len(master_names),
        total_lookup=len(lookup_names),
        match_count=len(matched_rows),
    )
