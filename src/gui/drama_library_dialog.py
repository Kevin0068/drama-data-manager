"""剧名库管理对话框 - 支持添加、删除、批量导入、搜索、导出剧名。"""

import tkinter as tk
from tkinter import messagebox, filedialog

from src.database import Database
from src.dao.drama_dao import DramaDAO
from src.excel_importer import ExcelImporter

FONT = ("Microsoft YaHei", 11)
FONT_TITLE = ("Microsoft YaHei", 13, "bold")
FONT_SMALL = ("Microsoft YaHei", 10)


class DramaLibraryDialog(tk.Toplevel):
    """剧名库管理弹窗，支持添加/删除/批量导入/搜索/导出。"""

    def __init__(self, parent, db: Database, backend_id: int):
        super().__init__(parent)
        self.db = db
        self.backend_id = backend_id
        self.drama_dao = DramaDAO(db)
        self._names: list[str] = []
        self.search_var = tk.StringVar()

        self.title("剧名库管理")
        self.geometry("480x560")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self._build()
        self._refresh_list()

    def _build(self):
        """构建对话框界面。"""
        tk.Label(self, text="剧名库", font=FONT_TITLE).pack(pady=(12, 4))

        # 搜索栏
        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(search_frame, text="搜索:", font=FONT_SMALL).pack(side=tk.LEFT)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=FONT)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        self.search_var.trace_add("write", lambda *_: self._refresh_display())
        tk.Button(search_frame, text="清除", font=FONT_SMALL,
                  command=lambda: self.search_var.set("")).pack(side=tk.LEFT)

        # 剧名列表
        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(list_frame, font=FONT, yscrollcommand=scrollbar.set,
                                  selectmode=tk.EXTENDED)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 输入框 + 添加按钮
        input_frame = tk.Frame(self)
        input_frame.pack(fill=tk.X, padx=16, pady=4)

        self.entry = tk.Entry(input_frame, font=FONT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self._add_drama())

        tk.Button(input_frame, text="添加", font=FONT, command=self._add_drama).pack(side=tk.LEFT)

        # 操作按钮
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=(4, 12))

        tk.Button(btn_frame, text="删除选中", font=FONT, command=self._delete_drama).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="批量导入", font=FONT, command=self._batch_import).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="导出", font=FONT, command=self._export).pack(side=tk.LEFT, padx=4)

        # 计数标签
        self.count_label = tk.Label(self, text="", font=FONT)
        self.count_label.pack(pady=(0, 8))

    def _refresh_list(self):
        """从数据库加载剧名列表。"""
        self._names = self.drama_dao.list_all(self.backend_id)
        self._refresh_display()

    def _refresh_display(self):
        """根据搜索关键词刷新显示。"""
        self.listbox.delete(0, tk.END)
        keyword = self.search_var.get().strip().lower()
        displayed = 0
        for name in self._names:
            if not keyword or keyword in name.lower():
                self.listbox.insert(tk.END, name)
                displayed += 1
        if keyword:
            self.count_label.config(text=f"共 {len(self._names)} 个剧名，显示 {displayed} 个")
        else:
            self.count_label.config(text=f"共 {len(self._names)} 个剧名")

    def _add_drama(self):
        """添加单个剧名。"""
        name = self.entry.get().strip()
        if not name:
            return
        added = self.drama_dao.add(self.backend_id, name)
        if not added:
            messagebox.showinfo("提示", f'剧名 "{name}" 已存在', parent=self)
        self.entry.delete(0, tk.END)
        self._refresh_list()

    def _delete_drama(self):
        """删除选中的剧名（支持多选）。"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择要删除的剧名", parent=self)
            return
        names_to_delete = [self.listbox.get(i) for i in sel]
        if len(names_to_delete) > 1:
            if not messagebox.askyesno("确认", f"确定要删除选中的 {len(names_to_delete)} 个剧名吗？", parent=self):
                return
        for name in names_to_delete:
            self.drama_dao.delete(self.backend_id, name)
        self._refresh_list()

    def _batch_import(self):
        """从文件批量导入剧名。"""
        file_path = filedialog.askopenfilename(
            title="选择剧名文件",
            filetypes=[
                ("Excel 文件", "*.xlsx *.xls"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*"),
            ],
            parent=self,
        )
        if not file_path:
            return
        try:
            names = ExcelImporter.import_drama_names(file_path)
            count = self.drama_dao.add_batch(self.backend_id, names)
            messagebox.showinfo(
                "导入完成",
                f"读取 {len(names)} 个剧名，新增 {count} 个（{len(names) - count} 个重复已忽略）",
                parent=self,
            )
        except Exception as e:
            messagebox.showerror("导入失败", str(e), parent=self)
        self._refresh_list()

    def _export(self):
        """导出剧名库到 Excel 文件。"""
        if not self._names:
            messagebox.showinfo("提示", "剧名库为空", parent=self)
            return
        file_path = filedialog.asksaveasfilename(
            title="导出剧名库",
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx")],
            parent=self,
        )
        if not file_path:
            return
        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "剧名库"
            ws.append(["剧名"])
            for name in self._names:
                ws.append([name])
            wb.save(file_path)
            messagebox.showinfo("导出成功", f"已导出 {len(self._names)} 个剧名到:\n{file_path}", parent=self)
        except Exception as e:
            messagebox.showerror("导出失败", str(e), parent=self)
