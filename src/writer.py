"""Excel写入器：将工作簿保存回原文件路径。"""


def save_workbook(wb, file_path: str) -> None:
    """
    将工作簿保存回原文件路径（覆盖原文件）。

    Args:
        wb: openpyxl工作簿对象
        file_path: 原始A文档文件路径
    """
    wb.save(file_path)
