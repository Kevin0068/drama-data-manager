"""更新模块 - 支持自动检查、手动检查、后台下载并自动替换重启。"""

import os
import sys
import threading
import tempfile
import urllib.request
import json
import tkinter as tk
from tkinter import messagebox, ttk

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


def _find_exe_download_url(data: dict) -> str:
    """从 Release 数据中找独立 exe 下载链接（优先非 Setup 的 exe）。"""
    exe_url = ""
    for asset in data.get("assets", []):
        name = asset.get("name", "")
        if name.endswith(".exe"):
            if "Setup" not in name:
                return asset["browser_download_url"]
            exe_url = asset["browser_download_url"]
    return exe_url or data.get("html_url", "")


def check_update(root: tk.Tk):
    """启动时后台自动检查更新，有新版本静默弹窗。"""
    def _check():
        data = _fetch_latest_release()
        if not data:
            return
        tag = data.get("tag_name", "")
        if tag and _parse_version(tag) > _parse_version(__version__):
            changelog = data.get("body", "") or "暂无更新说明"
            url = _find_exe_download_url(data)
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
        url = _find_exe_download_url(data)
        root.after(0, lambda: _show_update_dialog(root, tag, changelog, url))

    threading.Thread(target=_check, daemon=True).start()


def _show_update_dialog(root: tk.Tk, new_version: str, changelog: str, download_url: str):
    """弹窗显示新版本信息、更新日志，支持一键下载替换重启。"""
    dialog = tk.Toplevel(root)
    dialog.title("发现新版本")
    dialog.geometry("500x480")
    dialog.minsize(400, 400)
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text=f"新版本 {new_version} 可用",
             font=("Microsoft YaHei", 14, "bold")).pack(pady=(16, 4))
    tk.Label(dialog, text=f"当前版本: v{__version__}", font=FONT_SMALL).pack()

    tk.Label(dialog, text="更新日志:", font=FONT, anchor=tk.W).pack(
        fill=tk.X, padx=16, pady=(12, 4))

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

    # 按钮区域（先 pack 到底部，确保始终可见）
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(side=tk.BOTTOM, pady=(0, 16))

    # 进度条（初始隐藏）
    progress_frame = tk.Frame(dialog)
    progress_var = tk.DoubleVar(value=0)
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var,
                                   maximum=100, length=400)
    progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
    progress_label = tk.Label(progress_frame, text="0%", font=FONT_SMALL)
    progress_label.pack(side=tk.RIGHT)

    update_btn = tk.Button(btn_frame, text="立即更新", font=FONT)
    update_btn.pack(side=tk.LEFT, padx=8)
    cancel_btn = tk.Button(btn_frame, text="稍后再说", font=FONT,
                           command=dialog.destroy)
    cancel_btn.pack(side=tk.LEFT, padx=8)

    def _do_update():
        update_btn.config(state=tk.DISABLED, text="下载中...")
        cancel_btn.config(state=tk.DISABLED)
        progress_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 8))
        _download_and_replace(dialog, root, download_url,
                              progress_var, progress_label, update_btn)

    update_btn.config(command=_do_update)


def _download_and_replace(dialog, root, url, progress_var, progress_label, update_btn):
    """后台线程下载新版 exe，完成后用 bat 脚本替换并重启。"""

    def _progress_hook(block_num, block_size, total_size):
        if total_size > 0:
            pct = min(block_num * block_size / total_size * 100, 100)
            root.after(0, lambda: _update_progress(pct))

    def _update_progress(pct):
        progress_var.set(pct)
        progress_label.config(text=f"{pct:.0f}%")

    def _download():
        try:
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".exe")
            os.close(tmp_fd)
            urllib.request.urlretrieve(url, tmp_path, reporthook=_progress_hook)
            root.after(0, lambda: _on_download_complete(tmp_path))
        except Exception as e:
            root.after(0, lambda: _on_download_error(str(e)))

    def _on_download_complete(tmp_path):
        progress_var.set(100)
        progress_label.config(text="100%")
        update_btn.config(text="准备重启...")

        current_exe = sys.executable
        # 如果是 PyInstaller 打包的 exe
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable
        else:
            # 开发模式下不执行替换
            messagebox.showinfo("提示", f"开发模式：新版本已下载到\n{tmp_path}",
                                parent=dialog)
            dialog.destroy()
            return

        _replace_and_restart(current_exe, tmp_path)

    def _on_download_error(err):
        update_btn.config(state=tk.NORMAL, text="重试")
        messagebox.showerror("下载失败", f"下载出错：{err}", parent=dialog)

    threading.Thread(target=_download, daemon=True).start()


def _replace_and_restart(current_exe: str, new_exe: str):
    """创建 bat 脚本：等待当前进程退出 → 替换 exe → 重启 → 删除 bat。"""
    bat_path = os.path.join(tempfile.gettempdir(), "_drama_update.bat")
    bat_content = f'''@echo off
chcp 65001 >nul
echo 正在更新，请稍候...
timeout /t 2 /nobreak >nul
:retry
del "{current_exe}" >nul 2>&1
if exist "{current_exe}" (
    timeout /t 1 /nobreak >nul
    goto retry
)
move /y "{new_exe}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
'''
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)

    os.startfile(bat_path)
    sys.exit(0)
