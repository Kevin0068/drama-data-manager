"""命令行入口：解析参数，协调各组件完成匹配和标记流程。"""

import argparse
import sys

from openpyxl import load_workbook

from src.reader import read_drama_names
from src.matcher import match_dramas
from src.highlighter import highlight_rows
from src.writer import save_workbook


def parse_args(argv=None):
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="Excel剧名匹配工具：在A文档中查找B文档中出现的剧名并高亮标记"
    )
    parser.add_argument(
        "--master", required=True, help="A文档（主表）Excel文件路径"
    )
    parser.add_argument(
        "--lookup", required=True, help="B文档（查找列表）Excel文件路径"
    )
    parser.add_argument(
        "--master-col",
        required=True,
        help="A文档剧名列标识（列名或列号）",
    )
    parser.add_argument(
        "--lookup-col",
        required=True,
        help="B文档剧名列标识（列名或列号）",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """解析命令行参数，协调各组件完成匹配和标记流程。"""
    args = parse_args(argv)

    try:
        # 1. 读取A文档剧名（带行号）
        master_names = read_drama_names(args.master, args.master_col)

        # 2. 读取B文档剧名，提取为集合
        lookup_tuples = read_drama_names(args.lookup, args.lookup_col)
        lookup_set = {name for _, name in lookup_tuples}

        # 3. 匹配
        result = match_dramas(master_names, lookup_set)

        # 4. 高亮并保存（仅在有匹配时）
        if result.match_count > 0:
            wb = load_workbook(args.master)
            ws = wb.active
            highlight_rows(ws, result.matched_rows)
            save_workbook(wb, args.master)

        # 5. 输出统计信息
        print(f"A文档总数: {result.total_master}")
        print(f"B文档总数: {result.total_lookup}")
        print(f"匹配数量: {result.match_count}")

        if result.match_count == 0:
            print("未找到匹配项")

    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
