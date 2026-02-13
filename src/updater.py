"""更新模块 - 支持自动和手动检查 GitHub Releases 新版本，显示更新日志。"""

import threading
import urllib.request
import json
import tkinter as tk
from tkinter import messagebox

from src.version import __version__

GITHUB_OWNER = "Kevin0068"
GITHUB_REPO = "drama-data-manager"
RELEASES_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

FONT = ("Microsoft YaHei", 11)
FONT_SMALL = ("Microsoft YaHei", 10)


def _parse_version(v: str) -> tuple[int, ...]:
    v = v.lstrip("vV")
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _fetch_latest_release() -> dict | None:
    """获取最新 Release 信息，失败返回 None。"""
    try:
        req = urllib.request.Request(
            RELEASES_API, headers={"Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _find_download_url(data: dict) -> str:
    """从 Release 数据中找 exe 下载链接。"""
    for asset in data.get("assets", []):
        name = asset.get("name", "")
        if name.endswith("_Setup.exe") or name.endswith(".exe"):
            return asset["browser_download_url"]
    return data.get("html_url", "")


def check_update(root: tk.Tk):
    """启动时后台自动检查更新，有新版本静默弹窗。"""
    def _check():
        data = _fetch_latest_release()
        if not data:
            return
        tag = data.get("tag_name", "")
        if tag and _parse_version(tag) > _parse_version(__version__):
            changelog = data.get("body", "") or "暂无更新说明"
            url = _find_download_url(data)
            root.after(0, lambda: _show_update_dialog(root, tag, changelog, url))

    threading.Thread(target=_check, daemon=True).start()


def manual_check_update(root: tk.Tk):
    """用户手动点击检查更新，显示加载状态和结果。"""
    def _check():
        data = _fetch_latest_release()
        if data is None:
            root.after(0, lambda: messagebox.showerror(
                "检查失败", "无法连接到更新服务器，请检查网络", parent=root))
            return

        tag = data.get("tag_name", "")
        if not tag or _parse_version(tag) <= _parse_version(__version__):
            root.after(0, lambda: messagebox.showinfo(
                "检查更新", f"当前已是最新版本 v{__version__}", parent=root))
            return

        changelog = data.get("body", "") or "暂无更新说明"
        url = _find_download_url(data)
        root.after(0, lambda: _show_update_dialog(root, tag, changelog, url))

    threading.Thread(target=_check, daemon=True).start()


def _show_update_dialog(root: tk.Tk, new_version: str, changelog: str, download_url: str):
    """弹窗显示新版本信息和更新日志。"""
    dialog = tk.Toplevel(root)
    dialog.title("发现新版本")
    dialog.geometry("500x400")
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text=f"新版本 {new_version} 可用", font=("Microsoft YaHei", 14, "bold")).pack(pady=(16, 4))
    tk.Label(dialog, text=f"当前版本: v{__version__}", font=FONT_SMALL).pack()

    tk.Label(dialog, text="更新日志:", font=FONT, anchor=tk.W).pack(fill=tk.X, padx=16, pady=(12, 4))

    text_frame = tk.Frame(dialog)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(text_frame, font=FONT_SMALL, wrap=tk.WORD,
                          yscrollcommand=scrollbar.set, state=tk.NORMAL)
    text_widget.insert("1.0", changelog)
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=(0, 16))

    def _download():
        import webbrowser
        webbrowser.open(download_url)
        dialog.destroy()

    tk.Button(btn_frame, text="下载更新", font=FONT, command=_download).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="稍后再说", font=FONT, command=dialog.destroy).pack(side=tk.LEFT, padx=8)
