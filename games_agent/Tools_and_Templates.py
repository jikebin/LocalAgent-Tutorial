#%%
import hashlib
import json

PROMPT_REACT = """你的任务是扮演一个贪吃蛇游戏玩家，根据用户的输入反馈来调用工具移动蛇头。
请尽可能保证自己存活的情况下吃掉食物获取更多的分数，你可以使用以下工具：

{tools_text}

Use the following format:

Observation: 用户给出的贪吃蛇当前状态
Thought: 你的思考，根据观察结果给出下一步的移动方向
Action: the action to take, should be one of [{tools_name_text}]
Action Input: the input to the action
... (this Observation/Thought/Action/Action Input/Observation can be repeated zero or more times)

游戏基本信息介绍：
1.游戏范围：你是在一个宽800像素，高600像素的矩形内进行游戏。
2. 食物和蛇的初始像素大小为20x20。
3. 每次调用工具只会移动一格，也就是20x20像素。
4. 蛇头碰到墙壁或自己的身体会死亡。
5. 蛇头碰到食物会吃到食物，食物会消失，蛇的身体会变长，并且分数会增加。

现在，请开始你的游戏。
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
        "name_for_human": "移动贪吃蛇",
        "name_for_model": "move",
        "description_for_model": "输入移动的指令包括【UP, DOWN, LEFT, RIGHT】",
        "parameters": [
            {
                "name": "instruct",
                "description": "移动指令",
                "required": True,
                "schema": {"type": "string"},
                "enum": ["UP","DOWN","LEFT","RIGHT"],
            }
        ],
    },
]


def move(instruct):
    instruct = instruct.strip()
    # 移动指令
    if instruct == "UP":
        return "UP"
    elif instruct == "DOWN":
        return "DOWN"
    elif instruct == "LEFT":
        return "LEFT"
    elif instruct == "RIGHT":
        return "RIGHT"
    else:
        return "Invalid instruction"


def get_system_prompt():
    return build_input_text(tools)

available_functions = {
    "move": move,
}

if __name__ == "__main__":
    # 示例字符串
    text = "你好"
    system_prompt = build_input_text(tools)
# %%
