"""月份数据界面 - 数据表格、导入/匹配/导出、视图切换、统计。"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from src.database import Database
from src.dao.imported_data_dao import ImportedDataDAO
from src.dao.drama_dao import DramaDAO
from src.excel_importer import ExcelImporter
from src.exporter import Exporter
from src.match_engine import MatchEngine
from src.view_helpers import filter_rows, compute_column_sums

FONT = ("Microsoft YaHei", 11)
FONT_TITLE = ("Microsoft YaHei", 14, "bold")
FONT_SMALL = ("Microsoft YaHei", 10)


class MonthView:
    """月份数据界面，显示数据表格，提供导入/匹配/导出功能。"""

    def __init__(self, parent, db: Database, backend_id: int,
                 month_id: int, month_label: str, on_back=None):
        self.parent = parent
        self.db = db
        self.backend_id = backend_id
        self.month_id = month_id
        self.month_label = month_label
        self.on_back = on_back

        self.data_dao = ImportedDataDAO(db)
        self.drama_dao = DramaDAO(db)

        self.headers: list[str] = []
        self.all_rows: list[list] = []
        self.matched_indices: list[int] = []
        self.view_mode = tk.StringVar(value="all")
        self.search_var = tk.StringVar()
        self._sort_col: int | None = None
        self._sort_reverse: bool = False

        self._build()
        self._load_data()

    def _build(self):
        """构建月份数据界面。"""
        # 顶部：返回 + 标题
        top = tk.Frame(self.parent)
        top.pack(fill=tk.X, padx=16, pady=(12, 4))

        tk.Button(top, text="← 返回", font=FONT, command=self._go_back).pack(side=tk.LEFT)
        tk.Label(top, text=self.month_label, font=FONT_TITLE).pack(side=tk.LEFT, padx=16)

        # 工具栏
        toolbar = tk.Frame(self.parent)
        toolbar.pack(fill=tk.X, padx=16, pady=4)

        tk.Button(toolbar, text="导入", font=FONT, command=self._import_data).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="匹配", font=FONT, command=self._run_match).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="重新匹配", font=FONT, command=self._run_match).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="导出", font=FONT, command=self._export_data).pack(side=tk.LEFT, padx=4)

        # 视图切换
        view_frame = tk.Frame(toolbar)
        view_frame.pack(side=tk.RIGHT)

        for text, val in [("全部", "all"), ("仅匹配", "matched"), ("仅未匹配", "unmatched")]:
            tk.Radiobutton(
                view_frame, text=text, variable=self.view_mode, value=val,
                font=FONT_SMALL, command=self._refresh_table,
            ).pack(side=tk.LEFT, padx=2)

        # 搜索栏
        search_frame = tk.Frame(self.parent)
        search_frame.pack(fill=tk.X, padx=16, pady=2)

        tk.Label(search_frame, text="查找:", font=FONT_SMALL).pack(side=tk.LEFT)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=FONT)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        self.search_var.trace_add("write", lambda *_: self._refresh_table())
        tk.Button(search_frame, text="清除", font=FONT_SMALL,
                  command=lambda: self.search_var.set("")).pack(side=tk.LEFT)

        # 数据表格
        table_frame = tk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self.tree = ttk.Treeview(table_frame, show="headings")

        vsb = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # 底部统计栏（基本统计 + 可滚动合计区域）
        stats_frame = tk.Frame(self.parent)
        stats_frame.pack(fill=tk.X, padx=16, pady=(0, 8))

        self.stats_label = tk.Label(stats_frame, text="", font=FONT_SMALL, anchor=tk.W)
        self.stats_label.pack(fill=tk.X)

        self.sums_text = tk.Text(stats_frame, font=FONT_SMALL, height=3, wrap=tk.WORD,
                                 state=tk.DISABLED, relief=tk.FLAT, bg=self.parent.cget("bg"))
        self.sums_text.pack(fill=tk.X)

    def _load_data(self):
        """从数据库加载已有数据和匹配结果。"""
        self.headers = self.data_dao.get_headers(self.month_id)
        self.all_rows = self.data_dao.get_all_rows(self.month_id)
        self.matched_indices = self.data_dao.get_match_results(self.month_id)
        self._refresh_table()

    def _refresh_table(self):
        """根据当前视图模式、搜索关键词刷新表格数据。"""
        self.tree.delete(*self.tree.get_children())

        if not self.headers:
            self.tree["columns"] = ()
            self._update_stats([])
            return

        # 设置列（带排序点击）
        cols = [f"c{i}" for i in range(len(self.headers))]
        self.tree["columns"] = cols

        # 筛选行（视图模式）
        filtered = filter_rows(self.all_rows, self.matched_indices, self.view_mode.get())

        # 搜索过滤
        keyword = self.search_var.get().strip()
        if keyword:
            keyword_lower = keyword.lower()
            filtered = [
                row for row in filtered
                if any(keyword_lower in str(v).lower() for v in row if v is not None)
            ]

        # 排序
        if self._sort_col is not None and self._sort_col < len(self.headers):
            col_idx = self._sort_col

            def sort_key(row):
                if col_idx >= len(row) or row[col_idx] is None:
                    return (1, "")
                val = row[col_idx]
                if isinstance(val, (int, float)):
                    return (0, val)
                return (1, str(val).lower())

            filtered = sorted(filtered, key=sort_key, reverse=self._sort_reverse)

        # 计算列宽
        col_widths = []
        for i, header in enumerate(self.headers):
            max_len = len(str(header))
            for row in filtered[:50]:
                if i < len(row) and row[i] is not None:
                    max_len = max(max_len, len(str(row[i])))
            width = min(max(max_len * 12 + 20, 60), 300)
            col_widths.append(width)

        for i, header in enumerate(self.headers):
            arrow = ""
            if self._sort_col == i:
                arrow = " ▼" if self._sort_reverse else " ▲"
            self.tree.heading(cols[i], text=header + arrow,
                              command=lambda c=i: self._on_sort(c))
            self.tree.column(cols[i], width=col_widths[i], minwidth=50, stretch=False)

        # 插入数据行
        for row in filtered:
            values = [str(v) if v is not None else "" for v in row]
            while len(values) < len(self.headers):
                values.append("")
            self.tree.insert("", tk.END, values=values)

        self._update_stats(filtered)

    def _on_sort(self, col_index: int):
        """点击表头排序：再次点击同一列切换升降序。"""
        if self._sort_col == col_index:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_col = col_index
            self._sort_reverse = False
        self._refresh_table()

    @staticmethod
    def _format_number(val) -> str:
        """格式化数值：>=10000 转为万元单位。"""
        if not isinstance(val, (int, float)):
            return str(val)
        abs_val = abs(val)
        if abs_val >= 10000:
            return f"{val / 10000:.2f}万"
        elif isinstance(val, float):
            return f"{val:g}"
        return str(val)

    def _update_stats(self, displayed_rows: list[list]):
        """更新底部统计栏。"""
        total = len(self.all_rows)
        matched = len(self.matched_indices)
        displayed = len(displayed_rows)

        self.stats_label.config(
            text=f"总行数: {total}  |  匹配: {matched}  |  当前显示: {displayed}"
        )

        # 合计行
        sums_text = ""
        if displayed_rows and self.headers:
            sums = compute_column_sums(displayed_rows, len(self.headers))
            parts = []
            for i, s in enumerate(sums):
                if s != "":
                    parts.append(f"{self.headers[i]}: {self._format_number(s)}")
            if parts:
                sums_text = "合计: " + ", ".join(parts)

        self.sums_text.config(state=tk.NORMAL)
        self.sums_text.delete("1.0", tk.END)
        self.sums_text.insert("1.0", sums_text)
        self.sums_text.config(state=tk.DISABLED)

    def _import_data(self):
        """导入 Excel 文件数据。"""
        file_path = filedialog.askopenfilename(
            title="选择 Excel 文件",
            filetypes=[
                ("Excel 文件", "*.xlsx *.xls"),
                ("所有文件", "*.*"),
            ],
            parent=self.parent,
        )
        if not file_path:
            return
        try:
            headers, rows = ExcelImporter.import_file(file_path)
            self.data_dao.save_data(self.month_id, headers, rows)
            self.headers = headers
            self.all_rows = rows
            self.matched_indices = []
            self.view_mode.set("all")
            self._refresh_table()
            messagebox.showinfo("导入成功", f"已导入 {len(rows)} 行数据", parent=self.parent)
        except Exception as e:
            messagebox.showerror("导入失败", str(e), parent=self.parent)

    def _run_match(self):
        """执行匹配操作。"""
        if not self.all_rows:
            messagebox.showinfo("提示", "请先导入数据", parent=self.parent)
            return

        drama_set = self.drama_dao.get_set(self.backend_id)
        if not drama_set:
            messagebox.showinfo("提示", "剧名库为空，请先添加剧名", parent=self.parent)
            return

        try:
            col_index = MatchEngine.find_column_index(self.headers)
        except ValueError:
            # 让用户选择列
            col_index = self._ask_column_index()
            if col_index is None:
                return

        matched = MatchEngine.match(self.all_rows, col_index, drama_set)
        self.matched_indices = matched
        self.data_dao.save_match_results(self.month_id, matched)

        self.view_mode.set("matched")
        self._refresh_table()
        messagebox.showinfo(
            "匹配完成",
            f"共匹配 {len(matched)} 行（总 {len(self.all_rows)} 行）",
            parent=self.parent,
        )

    def _ask_column_index(self) -> int | None:
        """弹出对话框让用户选择匹配列。"""
        if not self.headers:
            return None

        dialog = tk.Toplevel(self.parent)
        dialog.title("选择匹配列")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.geometry("320x400")

        tk.Label(dialog, text='未找到"合集名称"列\n请选择用于匹配的列：', font=FONT).pack(pady=8)

        listbox = tk.Listbox(dialog, font=FONT)
        listbox.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)
        for i, h in enumerate(self.headers):
            listbox.insert(tk.END, f"{i+1}. {h}")

        result = [None]

        def on_confirm():
            sel = listbox.curselection()
            if sel:
                result[0] = sel[0]
                dialog.destroy()

        tk.Button(dialog, text="确定", font=FONT, command=on_confirm).pack(pady=8)
        dialog.wait_window()
        return result[0]

    def _export_data(self):
        """导出完整表格，匹配行高亮黄色。"""
        if not self.headers:
            messagebox.showinfo("提示", "没有数据可导出", parent=self.parent)
            return

        file_path = filedialog.asksaveasfilename(
            title="导出 Excel 文件",
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx")],
            parent=self.parent,
        )
        if not file_path:
            return
        try:
            Exporter.export_with_highlight(
                file_path, self.headers, self.all_rows, self.matched_indices
            )
            messagebox.showinfo(
                "导出成功",
                f"已导出 {len(self.all_rows)} 行（其中 {len(self.matched_indices)} 行高亮）到:\n{file_path}",
                parent=self.parent,
            )
        except Exception as e:
            messagebox.showerror("导出失败", str(e), parent=self.parent)

    def _go_back(self):
        """返回后台界面。"""
        if self.on_back:
            self.on_back()
