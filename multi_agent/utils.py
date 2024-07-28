#%%
import json
import datetime
import re
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multi_agent.prompt_templates import TOOL_DESC, PROMPT_REACT

def parse_plugin_split(text: str):
    i = text.rfind('\nAction:')
    j = text.rfind('\nAction Input:')
    k = text.rfind('\nObservation:')
    if 0 <= i < j:  # If the text has `Action` and `Action input`,
        if k < j:  # but does not contain `Observation`,
            # then it is likely that `Observation` is ommited by the LLM,
            # because the output text may have discarded the stop word.
            text = text.rstrip() + '\nObservation:'  # Add it back.
            k = text.rfind('\nObservation:')
    if 0 <= i < j < k:
        plugin_name = text[i + len('\nAction:'):j].strip()
        plugin_args = text[j + len('\nAction Input:'):k].strip()
        return plugin_name, plugin_args
    return '', ''


    
       
def build_input_text(list_of_plugin_info,sample_list_str="") -> str:
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
        elif plugin_info['args_format'] == 'markdown':
            tool += ' Enclose the markdown within triple backticks (`) at the beginning and end of the markdown.'
        else:
            raise NotImplementedError
        tools_text.append(tool)
    tools_text = '\n\n'.join(tools_text)

    # 候选插件的代号
    tools_name_text = ', '.join([plugin_info["name_for_model"] for plugin_info in list_of_plugin_info])
    system_prompt = PROMPT_REACT.format(
                    current_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                    tools_text=tools_text,
                    tools_name_text=tools_name_text,
                    sample_list_str=sample_list_str,
                )
    return system_prompt



def get_system_prompt(tools,source, question=""):
    # exam = search_exam(query=question,source=source)
    # 先忽略样例，防止影响
    exam = ''
    return build_input_text(tools,exam)




# markdown 转为 json
def markdown_to_json(json_str):
    pattern = r'```json\s*(.*?)\s*```'
    json_blocks = re.findall(pattern, json_str, re.DOTALL)
    if json_blocks:
        return json.loads(json_blocks[0])
    return {}


def api_calling(function_name,function_args=""):
    # TODO:根据名称获取对应的url信息
    url = ""

    # 解析 json 数据
    try:
        if "```json" in function_args:
            kwargs = markdown_to_json(function_args)
        else:
            kwargs = json.loads(function_args)
    except Exception as e:
        return {
            "observation": f'参数解析异常：{function_args}',
            "is_show": True,
            "interval": 0,
        }

    
    result = requests.post(url, json=kwargs)
    try:
        assert result.status_code == 200  #, f'The status_code of {url} is {result.status_code}'
        return {
            "observation": result.text,
            "is_show": False,
            "interval": 0,
        }
    except Exception as e:
        return {
            "observation": f'The status_code of {url} is {result.status_code}',
            "is_show": True,
            "interval": 0,
        }
        
if __name__ == "__main__":
    res = api_calling(function_name="呵呵",function_args="666哈哈")
# %%
