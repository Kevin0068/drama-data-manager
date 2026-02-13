# 剧名数据管理系统

Excel 剧名数据匹配与管理工具，支持多后台、剧名库、月份数据空间、自动匹配、统计和导出。

## 下载

前往 [Releases](https://github.com/Kevin0068/drama-data-manager/releases) 页面下载最新版 `.exe` 文件，双击即可运行（无需安装 Python）。

启动时会自动检查更新，有新版本会弹窗提示。

## 功能

- 多后台管理，每个后台独立剧名库
- 月份数据空间，按月组织 Excel 数据
- 导入 Excel（.xlsx/.xls），自动匹配剧名库
- 视图切换：全部 / 仅匹配 / 仅未匹配
- 搜索过滤、列排序
- 导出完整表格，匹配行黄色高亮
- 数据统计，大数值自动转万元单位
- SQLite 本地持久化

## 开发

```bash
pip install -r requirements.txt
python -m src.app
```

## 发布新版本

1. 更新 `src/version.py` 中的版本号
2. 提交并推送 tag：
```bash
git tag v1.0.1
git push origin v1.0.1
```
3. GitHub Actions 会自动构建 `.exe` 并创建 Release
