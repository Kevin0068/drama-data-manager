"""自动更新模块 - 启动时检查 GitHub Releases 是否有新版本。"""

import os
import sys
import threading
import urllib.request
import json
import tkinter as tk
from tkinter import messagebox

from src.version import __version__

GITHUB_OWNER = "Kevin0068"
GITHUB_REPO = "drama-data-manager"
RELEASES_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


def _parse_version(v: str) -> tuple[int, ...]:
    """将版本字符串转为可比较的元组，如 'v1.2.3' -> (1, 2, 3)。"""
    v = v.lstrip("vV")
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def check_update(root: tk.Tk):
    """在后台线程检查更新，有新版本时在主线程弹窗提示。"""
    def _check():
        try:
            req = urllib.request.Request(RELEASES_API, headers={"Accept": "application/vnd.github.v3+json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            latest_tag = data.get("tag_name", "")
            if not latest_tag:
                return

            if _parse_version(latest_tag) > _parse_version(__version__):
                # 查找 .exe 下载链接
                download_url = data.get("html_url", "")
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        break

                root.after(0, lambda: _show_update_dialog(root, latest_tag, download_url))
        except Exception:
            pass  # 网络不通或其他错误，静默忽略

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()


def _show_update_dialog(root: tk.Tk, new_version: str, download_url: str):
    """弹窗提示有新版本可用。"""
    msg = f"发现新版本 {new_version}（当前版本 v{__version__}）\n\n是否打开下载页面？"
    if messagebox.askyesno("版本更新", msg, parent=root):
        import webbrowser
        webbrowser.open(download_url)
