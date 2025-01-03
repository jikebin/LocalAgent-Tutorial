#%%
import sys
import os
sys.path.append(os.path.split(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))[0])
import json
import requests
import datetime
from  example_agent.Tools_and_Templates import build_input_text


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
    {
        "name_for_human": "搜索工具",
        "name_for_model": "web_search_new",
        "description_for_model": "在回答用户问题前，请先使用该工具进行相关信息的搜索，以确保回答的准确性。",
        "parameters": [
            {
                "name": "query",
                "description": "输入要查询的问题",
                "required": True,
                "schema": {"type": "string"},
            },
            {
                "name": "freshness",
                "description": '数据新鲜度，可选值为"oneDay", "oneWeek", "oneMonth", "oneYear","noLimit"不限（默认）',
                "required": False,
                "schema": {"type": "string"},
                "enum" : ["oneDay","oneWeek","oneMonth","oneYear","noLimit"],
                "default": "noLimit",
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


# 使用博查API实现
def web_search_new(query, count=8, freshness="noLimit"):
    """
    网页搜索工具
    :param query: 查询内容
    :param count: 返回结果数量
    :param freshness: 数据新鲜度，可选值为"oneDay", "oneWeek", "oneMonth", "oneYear","noLimit"不限（默认）
    """
    url = "https://api.bochaai.com/v1/web-search"
    payload = json.dumps({
      "query": query,
      "count": count,
      "freshness" : freshness,
      # "summary" : True,
    })

    headers = {
       # TODO:这里要填入你的key
      'Authorization': 'key',
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if not response.status_code == 200:
        return  "未找到相关信息"
    
    res = response.json()
    if str(res.get("code")) == "403":
        return "余额不足"
    elif str(res.get("code")) != "200":
        return  "未找到相关信息"
    
    data_list = res["data"]["webPages"]["value"]
    observation = "搜索结果：\n\n"
    for data in data_list:
        title = data["name"]
        url = data["url"]
        content = data["snippet"]
        # dateLastCrawled = data["dateLastCrawled"] # 最后爬取时间
        observation += f"# title: {title}\n## freshness\n{content}\n## URL\n{url}\n\n"
    return observation


available_functions = {
    "web_search": web_search,
    "web_search_new" : web_search_new,
}

if __name__ == "__main__":
    # 示例字符串
    query = "王者荣耀道歉原因"
    res = web_search(query)
    # prompt = get_system_prompt()
    info = format_web_info(res)


    
    







# %%
