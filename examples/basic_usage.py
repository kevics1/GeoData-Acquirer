"""
GeoData-Acquirer 基础使用示例
使用前请复制 config/.env.example 为 config/.env 并填写你的 API Key
"""

from src.main import GeoDataAcquirer


def main():
    app = GeoDataAcquirer()

    # 示例1：获取行政区划边界
    result = app.run("我需要武汉市的行政区划边界")
    print(f"输出文件：{result}")

    # 示例2：获取路网数据
    result = app.run("下载武汉市的道路数据")
    print(f"输出文件：{result}")

    # 示例3：获取天气数据
    result = app.run("武汉今天天气怎么样")
    print(f"输出文件：{result}")


if __name__ == "__main__":
    main()
