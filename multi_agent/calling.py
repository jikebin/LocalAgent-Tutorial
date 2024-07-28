#%%
import sys
import os
sys.path.append(os.path.split(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))[0])
import json
import requests
import pickle

        

# 解析markdown格式的python代码段
def python_code_interpreter(code_markdown, text={},**kwargs):
    url = "http://10.10.8.211:8080/sandbox_api" # 使用本地Docker服务执行code

    args = {"code": code_markdown}
    data_pickle = pickle.dumps(args)
    result = requests.post(url, data=data_pickle)
    assert (result.status_code == 200), f"The status_code of {url} is {result.status_code}"
    res = json.loads(result.text)
    try:
        return res.get('result')
    except Exception as e:
        pass
    return {
        "observation": "网络出现异常～～，请刷新后再试",
        "is_show": False,
        "interval": 0,
    }






tools_single = [
    {
        "name_for_human": "Code Interpreter",
        "name_for_model": "code_interpreter",
        "description_for_model": "A code interpreter capable of executing plot Python code.When you submit code to this tool, it will be executed directly. ",
        "parameters": [
            {
                "name": "code",
                "description": "Code to be executed",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "args_format" : "code",
    },
]


available_functions = {
    "code_interpreter" : python_code_interpreter,  # 动态获取
}


if __name__ == "__main__":
    text = {
      
    }
   
#%%


