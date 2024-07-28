#%%
import sys
import os
sys.path.append(os.path.split(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))[0])
import json
import requests
import datetime


tools = [
    {
        "name_for_human": "web搜索引擎",
        "name_for_model": "web_search",
        "description_for_model": "可以通过该工具来搜索互联网实时信息",
        "parameters": [
            {
                "name": "query",
                "description": "搜索信息",
                "required": True,
                "schema": {"type": "string"},
            },
        ],
    },
]



def call_api(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()  # Returns the JSON response content
    except requests.exceptions.RequestException as e:
        return {'error': str(e),"code" : 500}
    

def web_search(query=""):
    url = "http://127.0.0.1:10001/search"
    header = {
        "Content-Type": "application/json"
    }
    data = {
        "news": query,
        "num":10
    }
    try:
        response = requests.post(url, json=data, headers=header)
        # 判断请求是否成功
        if response.status_code == 200:
            data = response.json()  # 如果响应内容是JSON格式
            json_data = json.dumps(data, ensure_ascii=False)
            return json_data
        else:
            err_data = f"请求失败，状态码: {response.status_code}" + "\n错误信息:" + response.text
            return err_data
    except requests.exceptions.RequestException as e:
        err_data = f"请求过程中发生错误:{e}"
        return err_data

def format_web_info(json_data):
    data = json.loads(json_data)
    news_list = []
    for news in data:
        title = news.get("title")
        url = news.get("url")
        # news_list.append(f"[{title}]({url})")
        news_list.append(f"<div><a herf='{url}'>{title}</a></div>")
    return "\n".join(news_list)


def get_system_prompt():
    return build_input_text(tools)

available_functions = {
    "web_search": web_search,
}

if __name__ == "__main__":
    # 示例字符串
    query = "王者荣耀道歉原因"
    res = web_search(query)
    # prompt = get_system_prompt()
    info = format_web_info(res)


    
    







# %%
