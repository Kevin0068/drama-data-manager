"""pytest配置和共享fixtures。"""

import pytest
import os
import tempfile
from openpyxl import Workbook


@pytest.fixture
def tmp_dir():
    """提供临时目录用于测试文件操作。"""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_workbook():
    """创建一个包含示例数据的工作簿。"""
    wb = Workbook()
    ws = wb.active
    ws.append(["剧名", "类型", "年份"])
    ws.append(["琅琊榜", "古装", 2015])
    ws.append(["甄嬛传", "古装", 2011])
    ws.append(["人民的名义", "现代", 2017])
    return wb
