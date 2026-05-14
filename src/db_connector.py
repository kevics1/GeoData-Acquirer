"""
数据库连接模块
负责连接PostgreSQL数据库并获取行政区划边界数据
"""
import psycopg2
import json
import os
from typing import Optional, Dict


class DBConnector:
    """PostgreSQL数据库连接器"""

    def __init__(self):
        """从环境变量初始化数据库连接"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("GEODATA_DB_HOST", "localhost"),
                port=int(os.getenv("GEODATA_DB_PORT", "5432")),
                user=os.getenv("GEODATA_DB_USER", "postgres"),
                password=os.getenv("GEODATA_DB_PASSWORD", ""),
                dbname=os.getenv("GEODATA_DB_NAME", "Administrator")
            )
            print("[OK] 数据库连接成功")
        except Exception as e:
            print(f"[ERROR] 数据库连接失败: {e}")
            raise

    def get_boundary(self, table: str, code: str, code_field: str) -> Optional[Dict]:
        """
        获取行政区划边界(GeoJSON格式)

        Args:
            table: 数据库表名(province/city/county/village)
            code: 行政区划代码
            code_field: 代码字段名

        Returns:
            GeoJSON几何对象,如果未找到则返回None
        """
        cursor = self.conn.cursor()

        try:
            # 查询几何边界
            query = f"""
            SELECT ST_AsGeoJSON(geom) as boundary
            FROM {table}
            WHERE "{code_field}" = %s
            """

            cursor.execute(query, (code,))
            result = cursor.fetchone()

            if result and result[0]:
                return json.loads(result[0])
            else:
                return None

        except Exception as e:
            print(f"[ERROR] 查询边界失败: {e}")
            raise
        finally:
            cursor.close()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("[OK] 数据库连接已关闭")
