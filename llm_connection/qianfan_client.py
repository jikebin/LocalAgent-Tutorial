#%%
import os
from typing import Any
import qianfan

os.environ["QIANFAN_ACCESS_KEY"] = ""
os.environ["QIANFAN_SECRET_KEY"] = ""

# 通过AppID设置使用的应用，该参数可选；如果不设置该参数，SDK默认使用最新创建的应用AppID；如果设置，使用如下代码，替换示例中参数，应用AppID替换your_AppID
os.environ["QIANFAN_APPID"]=""

class QianFanClient:
    def __init__(self):
        self.chat_comp = qianfan.ChatCompletion()
        # self.model="ERNIE-Bot-4"
        self.model="ERNIE-Bot-8k"
        # self.model="ERNIE-Bot"

    def __call__(self,messages=[],stop=[]) -> Any:
        
        resp = self.chat_comp.do(model=self.model,messages=messages,stop=stop,disable_search=True)
        if resp.code!= 200:
            raise RuntimeError(f"请求失败，错误码：{resp.code}, 错误信息：文心4.0访问异常")
        return resp
    
    def stream(self,messages=[],stop=[]) -> Any:
        resp = self.chat_comp.do(model=self.model,messages=messages, stream=True,stop=stop,disable_search=True)

        for r in resp:
            text = r["body"]["result"]
            yield text

#%%

if __name__ == "__main__":
    llm = QianFanClient()
    res = llm.stream([{"role" : "user","content" : "你好"}],stop=["帮助"])
    for r in res:
        print(r,end="")
# %%
