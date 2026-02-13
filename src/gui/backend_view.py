"""后台管理界面 - 显示月份列表、剧名库入口，双击月份进入数据界面。"""

import tkinter as tk
from tkinter import messagebox, simpledialog

from src.database import Database
from src.dao.month_dao import MonthDAO

FONT = ("Microsoft YaHei", 11)
FONT_TITLE = ("Microsoft YaHei", 14, "bold")


class BackendView:
    """后台管理界面，显示月份列表和剧名库入口。"""

    def __init__(self, parent, db: Database, backend_id: int, backend_name: str, on_back=None):
        self.parent = parent
        self.db = db
        self.backend_id = backend_id
        self.backend_name = backend_name
        self.on_back = on_back
        self.month_dao = MonthDAO(db)
        self._build()

    def _build(self):
        """构建后台管理界面。"""
        # 顶部：标题 + 返回按钮
        top = tk.Frame(self.parent)
        top.pack(fill=tk.X, padx=16, pady=(12, 4))

        tk.Button(top, text="← 返回", font=FONT, command=self._go_back).pack(side=tk.LEFT)
        tk.Label(top, text=f"后台: {self.backend_name}", font=FONT_TITLE).pack(side=tk.LEFT, padx=16)

        # 月份列表
        list_frame = tk.Frame(self.parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(list_frame, font=FONT, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.bind("<Double-1>", lambda e: self._enter_month())

        # 按钮区域
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=(4, 16))

        tk.Button(btn_frame, text="新建月份", font=FONT, command=self._create_month).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="重命名", font=FONT, command=self._rename_month).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="删除月份", font=FONT, command=self._delete_month).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="管理剧名库", font=FONT, command=self._open_drama_library).pack(side=tk.LEFT, padx=8)

        self._refresh_list()

    def _refresh_list(self):
        """从数据库加载月份列表并刷新 Listbox。"""
        self.listbox.delete(0, tk.END)
        self._months = self.month_dao.list_all(self.backend_id)
        for _, label in self._months:
            self.listbox.insert(tk.END, label)

    def _create_month(self):
        """弹出输入对话框创建新月份。"""
        label = simpledialog.askstring(
            "新建月份", "请输入月份标签（如 2026年01月）：", parent=self.parent
        )
        if not label or not label.strip():
            return
        label = label.strip()
        try:
            self.month_dao.create(self.backend_id, label)
        except ValueError:
            messagebox.showwarning("提示", f"月份 \"{label}\" 已存在", parent=self.parent)
            return
        self._refresh_list()

    def _delete_month(self):
        """确认后删除选中的月份。"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个月份", parent=self.parent)
            return
        idx = sel[0]
        month_id, month_label = self._months[idx]
        if not messagebox.askyesno(
            "确认删除",
            f"确定要删除月份 \"{month_label}\" 及其所有数据吗？",
            parent=self.parent,
        ):
            return
        self.month_dao.delete(month_id)
        self._refresh_list()

    def _rename_month(self):
        """重命名选中的月份。"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个月份", parent=self.parent)
            return
        idx = sel[0]
        month_id, month_label = self._months[idx]
        new_label = simpledialog.askstring(
            "重命名月份", f"当前名称: {month_label}\n请输入新名称：",
            parent=self.parent, initialvalue=month_label
        )
        if not new_label or not new_label.strip() or new_label.strip() == month_label:
            return
        try:
            self.month_dao.rename(month_id, new_label.strip())
        except ValueError:
            messagebox.showwarning("提示", f"月份 \"{new_label.strip()}\" 已存在", parent=self.parent)
            return
        self._refresh_list()

    def _open_drama_library(self):
        """打开剧名库管理对话框。"""
        from src.gui.drama_library_dialog import DramaLibraryDialog
        DramaLibraryDialog(self.parent, self.db, self.backend_id)

    def _enter_month(self):
        """双击月份进入月份数据界面。"""
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        month_id, month_label = self._months[idx]

        # 清除当前内容，显示 MonthView
        for widget in self.parent.winfo_children():
            widget.destroy()

        from src.gui.month_view import MonthView
        MonthView(
            self.parent, self.db, self.backend_id, month_id, month_label,
            on_back=self._rebuild,
        )

    def _go_back(self):
        """返回主窗口。"""
        if self.on_back:
            self.on_back()

    def _rebuild(self):
        """从 MonthView 返回时重建后台界面。"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        self._build()
