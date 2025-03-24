#%%
import hashlib

tools = [
    {
        "name_for_human": "生成md5的哈希值",
        "name_for_model": "generate_md5_hash",
        "description_for_model": "将任意字符串转换为一个md5哈希值",
        "parameters": [
            {
                "name": "text",
                "description": "输入要转换的字符串",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
    },
]


def generate_md5_hash(text):
    # 创建一个md5 hash对象
    hash_object = hashlib.md5()
    # 提供需要哈希的数据（需要将字符串转换为字节）
    hash_object.update(text.encode())
    # 获取十六进制格式的哈希值
    return hash_object.hexdigest()


available_functions = {
    "generate_md5_hash": generate_md5_hash,
}

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



if __name__ == "__main__":
    # 示例字符串
    text = "你好"
    md5_hash = generate_md5_hash(text)

    res = convert_to_openai_schema(tools)
# %%
