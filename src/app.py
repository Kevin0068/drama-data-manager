"""应用入口 - 初始化数据库、创建主窗口、启动事件循环。"""

import tkinter as tk
from src.database import Database
from src.gui.main_window import MainWindow
from src.version import __version__
from src.updater import check_update


def main():
    db = Database()

    root = tk.Tk()
    root.title(f"剧名数据管理系统 v{__version__}")
    root.geometry("800x600")
    root.minsize(640, 480)

    MainWindow(root, db)

    # 启动后台检查更新
    check_update(root)

    def on_close():
        db.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
