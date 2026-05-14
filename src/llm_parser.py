"""
LLM解析器模块
使用LangChain + ModelScope DeepSeek解析用户的自然语言查询
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .models import QueryParams
import os


class LLMParser:
    """LLM查询解析器"""

    def __init__(self):
        """从环境变量初始化LLM"""
        self.llm = ChatOpenAI(
            model=os.getenv("GEODATA_LLM_MODEL", "deepseek-ai/DeepSeek-V3.2"),
            api_key=os.getenv("GEODATA_LLM_API_KEY"),
            base_url=os.getenv("GEODATA_LLM_BASE_URL", "https://api-inference.modelscope.cn/v1"),
            temperature=0
        )

        self.parser = JsonOutputParser(pydantic_object=QueryParams)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个地理数据查询解析器。用户会用自然语言描述他们需要的地理数据，你需要提取关键参数。

数据类型的可选值(以及对应的中文关键词):
- boundary: 行政区划、边界、行政边界
- road: 道路、路网、公路、街道
- building: 建筑、建筑物、房屋
- poi: 兴趣点、POI、设施、景点、学校、医院
- landuse: 土地利用、用地、耕地、林地
- elevation: 高程、DEM、地形、海拔
- weather: 天气、气象、温度、降水、气候
- climate: 气候数据、历史气候
- population: 人口、人口密度
- imagery: 影像、遥感、卫星影像

格式可选值: GeoJSON, Shapefile, GeoTIFF, CSV, NetCDF

示例:
输入: "我需要武汉市的行政区划边界"
输出: {{"region": "武汉市", "data_type": "boundary", "raw_input": "我需要武汉市的行政区划边界"}}

输入: "武汉的路网数据"
输出: {{"region": "武汉市", "data_type": "road", "raw_input": "武汉的路网数据"}}

输入: "武汉2023年天气"
输出: {{"region": "武汉市", "data_type": "weather", "temporal": {{"start": "2023-01-01", "end": "2023-12-31"}}, "raw_input": "武汉2023年天气"}}

输入: "北京建筑分布"
输出: {{"region": "北京市", "data_type": "building", "raw_input": "北京建筑分布"}}

输入: "下载湖北省30米分辨率土地利用数据"
输出: {{"region": "湖北省", "data_type": "landuse", "spatial_resolution": "30m", "raw_input": "下载湖北省30米分辨率土地利用数据"}}

{format_instructions}"""),
            ("user", "{input}")
        ])

        print("[OK] LLM解析器初始化完成")

    def parse(self, user_input: str) -> dict:
        """
        解析用户输入，提取地理查询参数

        Args:
            user_input: 用户的自然语言输入

        Returns:
            包含region, data_type等字段的字典
        """
        chain = self.prompt | self.llm | self.parser

        result = chain.invoke({
            "input": user_input,
            "format_instructions": self.parser.get_format_instructions()
        })

        # Ensure raw_input is always set
        if not result.get("raw_input"):
            result["raw_input"] = user_input

        return result
