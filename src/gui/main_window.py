"""主窗口 - 显示后台列表，提供新建/删除后台功能，双击进入后台管理界面。"""

import sqlite3
import tkinter as tk
from tkinter import simpledialog, messagebox

from src.database import Database
from src.dao.backend_dao import BackendDAO

FONT = ("Microsoft YaHei", 11)
FONT_TITLE = ("Microsoft YaHei", 16, "bold")


class MainWindow:
    """应用主窗口，显示后台列表，提供新建/删除后台功能。"""

    def __init__(self, root: tk.Tk, db: Database):
        self.root = root
        self.db = db
        self.backend_dao = BackendDAO(db)
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self._build()

    def _build(self):
        """构建主窗口界面。"""
        # 标题
        tk.Label(
            self.content_frame, text="剧名数据管理系统", font=FONT_TITLE
        ).pack(pady=(16, 8))

        # 后台列表区域
        list_frame = tk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(
            list_frame, font=FONT, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.bind("<Double-1>", lambda e: self._enter_backend())

        # 按钮区域
        btn_frame = tk.Frame(self.content_frame)
        btn_frame.pack(pady=(4, 16))

        tk.Button(
            btn_frame, text="新建后台", font=FONT, command=self._create_backend
        ).pack(side=tk.LEFT, padx=8)
        tk.Button(
            btn_frame, text="删除后台", font=FONT, command=self._delete_backend
        ).pack(side=tk.LEFT, padx=8)

        self._refresh_list()

    def _refresh_list(self):
        """从数据库加载后台列表并刷新 Listbox。"""
        self.listbox.delete(0, tk.END)
        self._backends = self.backend_dao.list_all()
        for _, name in self._backends:
            self.listbox.insert(tk.END, name)

    def _create_backend(self):
        """弹出输入对话框创建新后台。"""
        name = simpledialog.askstring(
            "新建后台", "请输入后台名称：", parent=self.root
        )
        if not name or not name.strip():
            return
        name = name.strip()
        try:
            self.backend_dao.create(name)
        except sqlite3.IntegrityError:
            messagebox.showwarning("提示", f"后台 \"{name}\" 已存在", parent=self.root)
            return
        self._refresh_list()

    def _delete_backend(self):
        """确认后删除选中的后台。"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个后台", parent=self.root)
            return
        idx = sel[0]
        backend_id, backend_name = self._backends[idx]
        if not messagebox.askyesno(
            "确认删除",
            f"确定要删除后台 \"{backend_name}\" 及其所有数据吗？",
            parent=self.root,
        ):
            return
        self.backend_dao.delete(backend_id)
        self._refresh_list()

    def _enter_backend(self):
        """双击后台进入后台管理界面。"""
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        backend_id, backend_name = self._backends[idx]

        # 清除当前内容，显示 BackendView
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        from src.gui.backend_view import BackendView

        BackendView(
            self.content_frame, self.db, backend_id, backend_name,
            on_back=self._rebuild,
        )

    def _rebuild(self):
        """从 BackendView 返回时重建主窗口内容。"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self._build()
