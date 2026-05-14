# Changelog

## [Unreleased]

### Planned
- Landsat / Sentinel 遥感数据源
- 地名→坐标转换（Geocoding）
- Web UI（FastAPI + React）
- Shapefile 输出格式

---

## [v1.0.0] - 2026-05-15

### Added
- 自然语言查询（中文输入，LLM 解析）
- 全国四级行政区划知识图谱（37,905 个节点）
- 插件化数据源架构（`GeoDataSource` 抽象基类 + 注册表）
- 数据源匹配引擎（加权评分：质量 0.4 + 认证 0.2 + 覆盖 0.2 + 分辨率 0.2）
- 已集成数据源：
  - `admin_boundary` — 行政区划边界（PostGIS）
  - `osm` — OpenStreetMap 数据（Overpass API）
  - `open_meteo` — 天气 / 气候 / 空气质量（免费 API）
- HTTP 下载器（重试 + 进度条）
- CLI 入口（`cli.py`），支持 `--list-sources` 和 `--source` 强制指定
- `.env.example` 模板
- MIT License

### Fixed
- Windows 控制台中文乱码（输出文件 UTF-8 不受影响）

---

## [v0.1.0] - 2026-05-14

### Added
- 初始提交：Phase 1（行政区划边界查询）+ Phase 2（插件架构 + OSM + Open-Meteo）
