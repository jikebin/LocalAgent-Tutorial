#%%
import hashlib
import json

PROMPT_REACT = """A helpful and general-purpose AI assistant that has strong language skills.
Answer the following questions as best you can. You have access to the following APIs:

{tools_text}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tools_name_text}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
"""

TOOL_DESC = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters}"""



def build_input_text(list_of_plugin_info) -> str:
    # 候选插件的详细信息
    tools_text = []
    for plugin_info in list_of_plugin_info:
        tool = TOOL_DESC.format(
            name_for_model=plugin_info["name_for_model"],
            name_for_human=plugin_info["name_for_human"],
            description_for_model=plugin_info["description_for_model"],
            parameters=json.dumps(plugin_info["parameters"], ensure_ascii=False),
        )
        if plugin_info.get('args_format', 'json') == 'json':
            tool += " Format the arguments as a JSON object."
        elif plugin_info['args_format'] == 'code':
            tool += ' Enclose the code within triple backticks (`) at the beginning and end of the code.'
        else:
            raise NotImplementedError
        tools_text.append(tool)
    tools_text = '\n\n'.join(tools_text)

    # 候选插件的代号
    tools_name_text = ', '.join([plugin_info["name_for_model"] for plugin_info in list_of_plugin_info])
    system_prompt = PROMPT_REACT.format(
                    tools_text=tools_text,
                    tools_name_text=tools_name_text,
                )
    return system_prompt


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


def get_system_prompt():
    return build_input_text(tools)

available_functions = {
    "generate_md5_hash": generate_md5_hash,
}

if __name__ == "__main__":
    # 示例字符串
    text = "你好"
    md5_hash = generate_md5_hash(text)
    system_prompt = build_input_text(tools)
# %%
