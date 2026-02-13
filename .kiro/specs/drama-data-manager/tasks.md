# Implementation Plan: 剧名数据管理系统

## Overview

基于 Python + tkinter + SQLite 构建剧名数据管理系统。按数据层 → 业务逻辑层 → 表现层的顺序逐步实现，每层完成后通过测试验证。

## Tasks

- [x] 1. 初始化项目结构和数据库层
  - [x] 1.1 创建数据库管理器 `src/database.py`
    - 实现 `Database` 类：初始化连接、创建所有表（backends, drama_names, months, imported_headers, imported_rows, match_results）、启用外键级联删除
    - _Requirements: 9.1, 9.4_
  - [x] 1.2 实现 `BackendDAO` 在 `src/dao/backend_dao.py`
    - 实现 create、delete（级联）、list_all 方法
    - _Requirements: 1.1, 1.2_
  - [ ]* 1.3 编写 BackendDAO 属性测试
    - **Property 1: 后台 CRUD 不变量**
    - **Validates: Requirements 1.1, 1.2**
  - [x] 1.4 实现 `DramaDAO` 在 `src/dao/drama_dao.py`
    - 实现 add、add_batch、delete、list_all、get_set 方法
    - _Requirements: 2.2, 2.3, 2.4, 2.6_
  - [ ]* 1.5 编写 DramaDAO 属性测试
    - **Property 2: 剧名库添加不变量**
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.6**
  - [x] 1.6 实现 `MonthDAO` 在 `src/dao/month_dao.py`
    - 实现 create、delete（级联）、list_all 方法
    - _Requirements: 3.1, 3.2, 3.5_
  - [x] 1.7 实现 `ImportedDataDAO` 在 `src/dao/imported_data_dao.py`
    - 实现 save_data、get_headers、get_all_rows、save_match_results、get_match_results、has_data 方法
    - _Requirements: 4.1, 4.3, 4.5, 5.3_
  - [ ]* 1.8 编写 ImportedDataDAO 属性测试
    - **Property 7: 导入数据往返**
    - **Property 9: 重新导入替换**
    - **Validates: Requirements 4.1, 4.3, 4.5**

- [x] 2. Checkpoint - 数据层验证
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. 实现业务逻辑层
  - [x] 3.1 实现 `MatchEngine` 在 `src/match_engine.py`
    - 实现 match 静态方法（去除首尾空格后精确匹配）和 find_column_index 方法
    - _Requirements: 5.1, 5.4, 5.5, 5.6_
  - [ ]* 3.2 编写 MatchEngine 属性测试
    - **Property 4: 匹配正确性**
    - **Validates: Requirements 5.1, 5.4, 5.5**
  - [x] 3.3 实现 `ExcelImporter` 在 `src/excel_importer.py`
    - 实现 import_file（读取完整 Excel）和 import_drama_names（从 Excel/文本导入剧名列表）方法
    - _Requirements: 4.1, 2.4_
  - [x] 3.4 实现 `Exporter` 在 `src/exporter.py`
    - 实现 export_to_excel 静态方法
    - _Requirements: 8.1_
  - [ ]* 3.5 编写导出往返属性测试
    - **Property 8: 导出往返**
    - **Validates: Requirements 8.1**
  - [x] 3.6 实现视图筛选和统计函数在 `src/view_helpers.py`
    - 实现 filter_rows（按匹配状态筛选）和 compute_column_sums（数值列求和）函数
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 7.1, 7.3_
  - [ ]* 3.7 编写视图筛选属性测试
    - **Property 5: 视图筛选分区**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
  - [ ]* 3.8 编写列合计属性测试
    - **Property 6: 列合计正确性**
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [x] 4. Checkpoint - 业务逻辑层验证
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. 实现 GUI 表现层
  - [x] 5.1 实现主窗口 `MainWindow` 在 `src/gui/main_window.py`
    - 后台列表（Listbox）、新建/删除后台按钮、双击进入后台
    - 应用启动时从数据库加载后台列表
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 9.2_
  - [x] 5.2 实现后台界面 `BackendView` 在 `src/gui/backend_view.py`
    - 月份列表、新建/删除月份按钮、管理剧名库按钮、返回按钮
    - 双击月份进入 MonthView
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - [x] 5.3 实现剧名库管理对话框 `DramaLibraryDialog` 在 `src/gui/drama_library_dialog.py`
    - 剧名列表、添加/删除/批量导入功能
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  - [x] 5.4 实现月份数据界面 `MonthView` 在 `src/gui/month_view.py`
    - 数据表格（ttk.Treeview）、工具栏（导入/匹配/重新匹配/导出按钮）
    - 视图切换（RadioButton：全部/仅匹配/仅未匹配）
    - 底部统计栏（合计行 + 匹配统计）
    - 返回按钮
    - _Requirements: 4.2, 5.1, 5.2, 5.4, 5.6, 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 8.1, 8.2_

- [x] 6. 实现应用入口和集成
  - [x] 6.1 创建应用入口 `src/app.py`
    - 初始化 Database、创建 tk.Tk 根窗口、启动 MainWindow
    - 窗口关闭时正确关闭数据库连接
    - _Requirements: 9.1, 9.2, 9.4_
  - [ ]* 6.2 编写数据持久化往返属性测试
    - **Property 3: 数据持久化往返**
    - **Validates: Requirements 2.5, 4.3, 5.3, 9.2**

- [x] 7. Final checkpoint - 全部验证
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- 数据层和业务逻辑层优先实现并测试，确保核心功能正确
- GUI 层依赖数据层和业务逻辑层，最后实现
- 属性测试使用 hypothesis 库，每个测试至少 100 次迭代
- 单元测试使用 pytest，覆盖边界情况和错误条件
