# GeoData-Acquirer

基于大语言模型的智能地理数据获取系统

## 项目简介

GeoData-Acquirer 是一个智能地理数据获取工具，通过自然语言交互实现"说话即获取数据"。

**核心功能**:
- 自然语言查询: 用中文描述需求，无需专业术语
- 知识图谱查询: 基于全国四级行政区划知识图谱(37,905个节点)
- 插件化数据源: 统一接口，轻松扩展新数据源
- 智能匹配: 自动选择最适合的数据源
- 标准格式输出: GeoJSON/JSON，兼容所有GIS软件

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `config/.env` 文件:

```bash
# LLM配置(ModelScope DeepSeek)
GEODATA_LLM_API_KEY=your-api-key-here

# 数据库配置
GEODATA_DB_HOST=localhost
GEODATA_DB_PORT=5432
GEODATA_DB_USER=postgres
GEODATA_DB_PASSWORD=your-password
GEODATA_DB_NAME=Administrator
```

### 3. 运行示例

```bash
# 获取行政区划边界
python cli.py "我需要武汉市的行政区划边界"

# 获取路网数据
python cli.py "武汉的路网数据"

# 获取天气数据
python cli.py "武汉今天天气"

# 查看所有可用数据源
python cli.py --list-sources

# 强制使用特定数据源
python cli.py "武汉边界" --source admin_boundary
```

## 项目结构

```
GeoData-Acquirer/
├── src/
│   ├── models.py               # Pydantic数据模型
│   ├── llm_parser.py           # LLM查询解析器(增强版)
│   ├── kg_query.py              # 知识图谱查询
│   ├── db_connector.py          # PostGIS数据库连接
│   ├── downloader.py            # HTTP下载器(重试+进度条)
│   ├── matcher.py               # 数据源匹配引擎
│   ├── main.py                  # 主流程(多源分发)
│   └── datasources/
│       ├── base.py              # GeoDataSource抽象基类
│       ├── registry.py          # 数据源注册表
│       ├── admin_boundary.py    # 行政区划边界(PostGIS)
│       ├── osm.py               # OpenStreetMap(Overpass API)
│       └── open_meteo.py        # 天气/气候数据(免费API)
├── config/
│   └── .env                     # 环境变量
├── data/
│   └── admin_kg.json            # 知识图谱
├── output/                      # 输出目录
├── requirements.txt
├── cli.py                       # 命令行入口
└── README.md
```

## 可用数据源

| 数据源 | 数据类型 | 覆盖范围 | 认证 |
|--------|---------|---------|------|
| admin_boundary | 行政区划边界 | 中国 | 本地PostGIS |
| osm | 道路、建筑、POI、土地利用、水系 | 全球 | 无需 |
| open_meteo | 天气、气候、空气质量 | 全球 | 无需 |

## 技术架构

```
用户输入 → LLM解析(地名+数据类型+时间) → 知识图谱解析行政代码
                                                    ↓
输出GeoJSON/JSON ← 下载 ← 数据源匹配(osm/open_meteo/admin_boundary)
```

**核心技术**:
- **LLM**: LangChain + ModelScope DeepSeek-V3.2
- **知识图谱**: 全国四级行政区划(省/市/县/村, 37,905个节点)
- **数据库**: PostgreSQL + PostGIS
- **插件系统**: GeoDataSource抽象基类 + 注册表模式
- **输出格式**: GeoJSON / JSON

## 输出示例

### 行政区划边界 (GeoJSON)
```json
{
  "type": "Feature",
  "properties": {
    "name": "武汉市",
    "code": "420100",
    "level": "city"
  },
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [...]
  }
}
```

### 天气数据 (JSON)
```json
{
  "daily": {
    "time": ["2026-05-14", "2026-05-15", ...],
    "temperature_2m_max": [28.5, 26.3, ...],
    "precipitation_sum": [0.0, 2.1, ...]
  }
}
```

## 开发阶段

| 阶段 | 状态 | 内容 |
|------|------|------|
| Phase 1 | 完成 | 行政区划边界查询(LLM + KG + PostGIS) |
| Phase 2 | 完成 | 插件架构 + OSM + Open-Meteo + 匹配引擎 |
| Phase 3 | 规划中 | Landsat/Sentinel遥感数据、高德地图、Web UI |

## 许可证

MIT License

