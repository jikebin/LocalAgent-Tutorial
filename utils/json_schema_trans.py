#%%
import json

def convert_to_openai_schema(custom_tools):
    """
    将自定义的 JSON Schema 格式转换为 OpenAI 支持的 JSON Schema 格式。

    参数:
        custom_tools (list): 自定义的工具列表，每个工具包含名称、描述和参数等信息。

    返回:
        list: 转换后的 OpenAI 格式工具列表。
    """
    openai_tools = []

    # 定义类型映射
    type_mapping = {
        "int": "integer",
        "string": "string",
        "boolean": "boolean",
        "array": "array",
        "object": "object",
        "number": "number"
    }

    for tool in custom_tools:
        openai_tool = {
            "name": tool.get("name_for_model"),
            "description": tool.get("description_for_model"),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }

        for param in tool.get("parameters", []):
            param_name = param.get("name")
            param_description = param.get("description", "")
            param_required = param.get("required", False)
            param_schema = param.get("schema", {})
            param_type = param_schema.get("type", "string")
            openai_type = type_mapping.get(param_type, "string")

            # 构建参数的 JSON Schema
            property_schema = {
                "type": openai_type,
                "description": param_description
            }

            # 处理枚举
            if "enum" in param:
                property_schema["enum"] = param["enum"]

            # 处理默认值
            if "default" in param:
                property_schema["default"] = param["default"]

            # 如果是数组类型，假设 items 为字符串类型
            if openai_type == "array":
                property_schema["items"] = {"type": "string"}

            # 添加到 properties
            openai_tool["parameters"]["properties"][param_name] = property_schema

            # 如果参数是必需的，添加到 required 列表
            if param_required:
                openai_tool["parameters"]["required"].append(param_name)

        # 如果没有必需的参数，移除 required 字段
        if not openai_tool["parameters"]["required"]:
            del openai_tool["parameters"]["required"]

        openai_tools.append(openai_tool)

    return openai_tools

# 示例使用
if __name__ == "__main__":
    tools_single = [
        {
            "name_for_human" : '大气污染物数据查询',
            "name_for_model": "air_pollution_data_query",
            "description_for_model": "根据条件查询城市、区县、街道、站点等位置的大气类污染物（PM2.5、PM10、SO2、NO2等）浓度数值",
            "parameters": [
                {
                    "name" : "location",
                    "description" : "查询的地点参数，地点类型包括：城市,街道,站点,微站等，如：北京，丰台区,卢沟桥街道，丰台小屯站",
                    "required": True,
                    "schema": {"type": "array"},
                    "default" : ["北京"],
                },
                {
                    "name" : "time",
                    "description" : '查询的时间范围可以是单个日期、多个具体日期、月份、季度或自定义的时间区间。例如：["1到3月"] 或 ["2024年1季度"] 或 ["本周一"]。请尽可能保留并使用用户输入的原始时间格式进行描述。',
                    "required": True,
                    "schema": {"type": "array"},
                    "default" : ["今天"],
                },
                {
                    "name" : "time_granularity",
                    "description" : "查询数据的时间粒度。默认为平均，表示查询时间范围内的平均值数据。说明：每日、每天等同逐日。",
                    "required": False,
                    "schema": {"type": "string"},
                    "enum" : ["逐年","逐月","逐周","逐日","逐小时","平均","逐季度"],
                    "default" : "平均",
                },
                {
                    "name" : "para",
                    "description" : "查询的参数，常见大气污染物有：污染六参数（PM2.5,SO2,NO2,CO,O3,PM10）,TVOC,AQI（空气质量）,TSP,CO2,综合指数等",
                    "required": True,
                    "schema": {"type": "array"},
                    "enum" : ["PM2.5","PM10","O3","AQI","CO2","SO2","NO2","CO","TVOC","TSP"],
                },
                {
                    "name" : "group_type",
                    "description" : "查询的地点范围级别，如：各街道、所有城市、各区县、各站点等。默认为空表示只查询单个地点。",
                    "required": False,
                    "schema": {"type": "string"},
                    "enum": ["城市","街道","区县","站点","2+26城市","2+36城市","339城市","337城市"],
                }
            ], 
        },
        # 其他工具项...
    ]

    openai_schema = convert_to_openai_schema(tools_single)
    print(json.dumps(openai_schema, ensure_ascii=False, indent=4))

# %%
