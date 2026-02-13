"""匹配引擎：对导入数据执行剧名匹配。"""


class MatchEngine:
    @staticmethod
    def match(rows: list[list], col_index: int, drama_set: set[str]) -> list[int]:
        """
        对导入数据执行匹配，返回匹配行的索引列表（0-based）。
        比对时去除首尾空格后精确匹配。
        """
        matched = []
        for i, row in enumerate(rows):
            if col_index < len(row):
                value = str(row[col_index]).strip()
                if value in drama_set:
                    matched.append(i)
        return matched

    @staticmethod
    def find_column_index(headers: list[str], target: str = "合集名称") -> int:
        """在表头中查找目标列，返回索引。未找到抛出 ValueError。"""
        for i, header in enumerate(headers):
            if str(header).strip() == target:
                return i
        raise ValueError(f"未找到目标列: {target}")
