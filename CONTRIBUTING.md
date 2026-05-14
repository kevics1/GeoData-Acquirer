# Contributing to GeoData-Acquirer

感谢你考虑为 GeoData-Acquirer 做出贡献！

## 开发流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/your-feature`)
3. 提交变更 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

## 代码规范

- Python 3.12+，遵循 PEP 8
- 新数据源请继承 `src/datasources/base.py` 中的 `GeoDataSource`
- 在 `src/datasources/registry.py` 中注册新数据源
- 添加必要的注释和文档字符串

## 新增数据源指南

1. 在 `src/datasources/` 下创建新文件，例如 `my_source.py`
2. 继承 `GeoDataSource`，实现 `can_handle()`、`search()`、`download()` 方法
3. 在文件末尾注册：`DataSourceRegistry().register(MySource())`
4. 更新 `README.md` 中的数据源表格

## Bug 报告

请使用 GitHub Issues，并包含：
- 使用的查询语句
- 期望行为 vs 实际行为
- Python 版本和操作系统

## 联系方式

- 开发者：何夕2077
- 指导教师：洪松 教授
