from dataclasses import dataclass


@dataclass
class MatchResult:
    """匹配结果"""
    matched_rows: list[int]       # 匹配到的行号列表（1-based）
    matched_names: list[str]      # 匹配到的剧名列表
    total_master: int             # A文档总剧名数
    total_lookup: int             # B文档总剧名数
    match_count: int              # 匹配数量
