"""视图筛选和统计辅助函数。"""


def filter_rows(rows: list[list], matched_indices: list[int], mode: str) -> list[list]:
    """
    按匹配状态筛选行。
    mode: "all" = 全部, "matched" = 仅匹配, "unmatched" = 仅未匹配
    Returns filtered rows list.
    """
    if mode == "all":
        return rows

    matched_set = set(matched_indices)

    if mode == "matched":
        return [row for i, row in enumerate(rows) if i in matched_set]
    elif mode == "unmatched":
        return [row for i, row in enumerate(rows) if i not in matched_set]
    else:
        raise ValueError(f"无效的筛选模式: {mode}")


def compute_column_sums(rows: list[list], num_columns: int) -> list:
    """
    计算每列的合计值。数值列求和，非数值列返回空字符串。
    Returns list of sums/empty strings, one per column.
    """
    sums = [0.0] * num_columns
    has_numeric = [False] * num_columns

    for row in rows:
        for col_idx in range(num_columns):
            if col_idx < len(row):
                val = row[col_idx]
                if isinstance(val, (int, float)):
                    sums[col_idx] += val
                    has_numeric[col_idx] = True

    return [sums[i] if has_numeric[i] else "" for i in range(num_columns)]
