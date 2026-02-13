# 实现计划：Excel剧名匹配工具

## 概述

基于Python + openpyxl实现命令行Excel剧名匹配工具，按管道式架构逐步构建各组件，每步构建在前一步基础上。

## 任务

- [x] 1. 项目初始化与基础结构
  - [x] 1.1 创建项目结构和依赖配置
    - 创建 `pyproject.toml` 或 `requirements.txt`，声明依赖：openpyxl, pytest, hypothesis
    - 创建目录结构：`src/` 下包含 `__init__.py`, `main.py`, `reader.py`, `matcher.py`, `highlighter.py`, `writer.py`
    - 创建 `tests/` 目录和 `conftest.py`
    - _Requirements: 全局_

  - [x] 1.2 实现数据模型
    - 在 `src/models.py` 中创建 `MatchResult` 数据类
    - _Requirements: 2.4, 4.3_

- [x] 2. 实现Excel读取器
  - [x] 2.1 实现 `resolve_column_index` 和 `read_drama_names` 函数
    - 在 `src/reader.py` 中实现列标识解析（支持列名和列号）
    - 实现从指定列读取剧名，去除首尾空格，跳过空值
    - 实现文件路径校验和格式校验的错误处理
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ]* 2.2 编写读取器属性测试：空单元格过滤
    - **Property 1: 空单元格过滤**
    - **Validates: Requirements 1.5**

  - [ ]* 2.3 编写读取器单元测试
    - 测试文件不存在、格式无效、列不存在的错误处理
    - 测试空Excel文件处理
    - _Requirements: 1.2, 1.3, 1.4_

- [x] 3. 实现剧名匹配器
  - [x] 3.1 实现 `match_dramas` 函数
    - 在 `src/matcher.py` 中实现基于set的匹配逻辑
    - 去除首尾空格后进行精确匹配
    - 返回匹配行号列表和 `MatchResult`
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ]* 3.2 编写匹配器属性测试：匹配等于集合交集
    - **Property 2: 匹配等于集合交集**
    - **Validates: Requirements 2.1, 2.2**

- [x] 4. 实现高亮标记器
  - [x] 4.1 实现 `highlight_rows` 函数
    - 在 `src/highlighter.py` 中实现行高亮逻辑
    - 使用 `PatternFill` 设置黄色背景
    - 通过 `copy()` 保留原有格式
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ]* 4.2 编写高亮标记器属性测试：高亮精确性与格式保留
    - **Property 3: 高亮精确性与格式保留**
    - **Validates: Requirements 3.1, 3.2, 3.3**

- [x] 5. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 6. 实现Excel写入器与保存
  - [x] 6.1 实现 save_workbook 函数
    - 在 `src/writer.py` 中实现将工作簿保存回原文件路径
    - _Requirements: 4.1, 4.2_

  - [ ]* 6.2 编写保存功能属性测试
    - **Property 4: 保存覆盖原文件**
    - **Validates: Requirements 4.1**

- [x] 7. 实现命令行入口与组件串联
  - [x] 7.1 实现 `main.py` 命令行入口
    - 使用 argparse 解析命令行参数
    - 串联读取器 → 匹配器 → 高亮标记器 → 写入器的完整流程
    - 输出匹配统计信息
    - _Requirements: 1.1, 2.3, 2.4, 4.2_

  - [ ]* 7.2 编写往返一致性属性测试
    - **Property 5: Excel数据往返一致性**
    - **Validates: Requirements 5.3**

- [x] 8. Final Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

## 备注

- 标记 `*` 的任务为可选任务，可跳过以加快MVP开发
- 每个任务引用了具体的需求编号以确保可追溯性
- Checkpoint任务用于阶段性验证
- 属性测试验证通用正确性属性，单元测试验证具体示例和边界情况
