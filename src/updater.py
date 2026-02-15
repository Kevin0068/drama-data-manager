"""更新模块 - 支持自动检查、手动检查、下载安装包并自动安装重启。"""

import os
import sys
import subprocess
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
    try:
        req = urllib.request.Request(
            RELEASES_API, headers={"Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _find_setup_download_url(data: dict) -> str:
    """优先找 Setup.exe 安装包，其次找独立 exe。"""
    setup_url = ""
    exe_url = ""
    for asset in data.get("assets", []):
        name = asset.get("name", "")
        if name.endswith(".exe"):
            if "Setup" in name:
                setup_url = asset["browser_download_url"]
            else:
                exe_url = asset["browser_download_url"]
    return setup_url or exe_url or data.get("html_url", "")


def check_update(root: tk.Tk):
    """启动时后台自动检查更新，有新版本静默弹窗。"""
    def _check():
        data = _fetch_latest_release()
        if not data:
            return
        tag = data.get("tag_name", "")
        if tag and _parse_version(tag) > _parse_version(__version__):
            changelog = data.get("body", "") or "暂无更新说明"
            url = _find_setup_download_url(data)
            root.after(0, lambda: _show_update_dialog(root, tag, changelog, url))

    threading.Thread(target=_check, daemon=True).start()


def manual_check_update(root: tk.Tk):
    """用户手动点击检查更新。"""
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
        url = _find_setup_download_url(data)
        root.after(0, lambda: _show_update_dialog(root, tag, changelog, url))

    threading.Thread(target=_check, daemon=True).start()


def _show_update_dialog(root: tk.Tk, new_version: str, changelog: str, download_url: str):
    """弹窗显示新版本信息、更新日志，支持一键下载安装。"""
    dialog = tk.Toplevel(root)
    dialog.title("发现新版本")
    dialog.geometry("500x480")
    dialog.minsize(400, 300)
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text=f"新版本 {new_version} 可用",
             font=("Microsoft YaHei", 14, "bold")).pack(pady=(16, 4))
    tk.Label(dialog, text=f"当前版本: v{__version__}", font=FONT_SMALL).pack()
    tk.Label(dialog, text="更新日志:", font=FONT, anchor=tk.W).pack(
        fill=tk.X, padx=16, pady=(12, 4))

    # 先 pack 底部按钮
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(side=tk.BOTTOM, pady=(0, 16))

    # 进度条 - 一开始就 pack，默认显示 0%
    progress_frame = tk.Frame(dialog)
    progress_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 8))
    progress_var = tk.DoubleVar(value=0)
    ttk.Progressbar(progress_frame, variable=progress_var,
                     maximum=100, length=400).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
    progress_label = tk.Label(progress_frame, text="等待下载", font=FONT_SMALL)
    progress_label.pack(side=tk.RIGHT)

    update_btn = tk.Button(btn_frame, text="立即更新", font=FONT)
    update_btn.pack(side=tk.LEFT, padx=8)
    cancel_btn = tk.Button(btn_frame, text="稍后再说", font=FONT, command=dialog.destroy)
    cancel_btn.pack(side=tk.LEFT, padx=8)

    # 更新日志
    text_frame = tk.Frame(dialog)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget = tk.Text(text_frame, font=FONT_SMALL, wrap=tk.WORD,
                          yscrollcommand=scrollbar.set)
    text_widget.insert("1.0", changelog)
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)

    def _do_update():
        update_btn.config(state=tk.DISABLED, text="下载中...")
        cancel_btn.config(state=tk.DISABLED)
        progress_label.config(text="0%")
        _download_and_install(dialog, root, download_url,
                              progress_var, progress_label, update_btn)

    update_btn.config(command=_do_update)


def _download_and_install(dialog, root, url, progress_var, progress_label, update_btn):
    """下载安装包并运行安装。"""

    def _progress_hook(block_num, block_size, total_size):
        if total_size > 0:
            pct = min(block_num * block_size / total_size * 100, 100)
            root.after(0, lambda: _update_progress(pct))

    def _update_progress(pct):
        progress_var.set(pct)
        progress_label.config(text=f"{pct:.0f}%")

    def _download():
        try:
            # 下载到临时目录，保留 .exe 后缀
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, "DramaDataManager_Setup.exe")
            urllib.request.urlretrieve(url, tmp_path, reporthook=_progress_hook)
            root.after(0, lambda: _on_download_complete(tmp_path))
        except Exception as e:
            root.after(0, lambda: _on_download_error(str(e)))

    def _on_download_complete(setup_path):
        progress_var.set(100)
        progress_label.config(text="100%")
        update_btn.config(text="正在安装...")

        if not getattr(sys, 'frozen', False):
            messagebox.showinfo("提示", f"开发模式：安装包已下载到\n{setup_path}",
                                parent=dialog)
            dialog.destroy()
            return

        # 获取当前进程信息
        current_pid = os.getpid()
        tmp_dir = tempfile.gettempdir()

        # 用 VBS 脚本启动 bat，确保完全独立于当前进程
        bat_path = os.path.join(tmp_dir, "drama_update.bat")
        vbs_path = os.path.join(tmp_dir, "drama_update.vbs")

        # 不手动 start exe，让 Inno Setup 的 [Run] 段自动启动新版本
        bat_content = (
            f'@echo off\r\n'
            f':wait_loop\r\n'
            f'tasklist /FI "PID eq {current_pid}" 2>NUL | find /I "{current_pid}" >NUL\r\n'
            f'if not errorlevel 1 (\r\n'
            f'    timeout /t 1 /nobreak >NUL\r\n'
            f'    goto wait_loop\r\n'
            f')\r\n'
            f'timeout /t 2 /nobreak >NUL\r\n'
            f'"{setup_path}" /SILENT /CLOSEAPPLICATIONS\r\n'
            f'del "{bat_path}"\r\n'
            f'del "{vbs_path}"\r\n'
        )

        vbs_content = (
            f'Set WshShell = CreateObject("WScript.Shell")\r\n'
            f'WshShell.Run """cmd"" /c ""{bat_path}""""", 0, False\r\n'
        )

        try:
            with open(bat_path, "w", encoding="gbk") as f:
                f.write(bat_content)
            with open(vbs_path, "w", encoding="gbk") as f:
                f.write(vbs_content)
            # wscript 启动 VBS，VBS 启动隐藏的 cmd，完全独立
            os.startfile(vbs_path)
        except Exception:
            # fallback: 直接运行安装包
            try:
                subprocess.Popen([setup_path, "/SILENT", "/CLOSEAPPLICATIONS",
                                  "/RESTARTAPPLICATIONS"], shell=False)
            except Exception:
                os.startfile(setup_path)

        sys.exit(0)

    def _on_download_error(err):
        update_btn.config(state=tk.NORMAL, text="重试")
        messagebox.showerror("下载失败", f"下载出错：{err}", parent=dialog)

    threading.Thread(target=_download, daemon=True).start()
