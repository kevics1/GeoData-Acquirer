"""
知识图谱查询模块
负责从行政区划知识图谱中查询地名对应的行政代码
"""
import json
from typing import Optional, Dict


class KnowledgeGraphQuery:
    """知识图谱查询类"""

    def __init__(self, kg_path: str):
        """
        初始化知识图谱查询器

        Args:
            kg_path: 知识图谱JSON文件路径
        """
        # 加载知识图谱JSON
        with open(kg_path, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)

        # 构建地名→代码索引
        self.name_to_info = {}
        for node in kg_data['nodes']:
            name = node.get('name')
            code = node.get('id')
            level = node.get('level')

            if name and code:
                self.name_to_info[name] = {
                    'code': code,
                    'level': level
                }

        print(f"[OK] 知识图谱加载完成: {len(self.name_to_info)} 个地区")

    def get_admin_info(self, region_name: str) -> Optional[Dict[str, str]]:
        """
        根据地名查询行政区划信息

        Args:
            region_name: 地区名称,如"武汉市"、"湖北省"

        Returns:
            包含code和level的字典,如果未找到则返回None
        """
        return self.name_to_info.get(region_name)

    def determine_table(self, admin_code: str, level: str) -> str:
        """
        根据行政代码和级别确定数据库表名

        Args:
            admin_code: 行政区划代码
            level: 行政级别(province/city/county/village)

        Returns:
            数据库表名
        """
        # 直接使用level作为表名
        return level

    def get_code_field(self, table: str) -> str:
        """
        根据表名获取对应的代码字段名

        Args:
            table: 数据库表名

        Returns:
            代码字段名
        """
        code_field_map = {
            'province': '省级码',
            'city': '地级码',
            'county': '县级码',
            'village': 'area_code'
        }

        return code_field_map.get(table, 'code')
