# %%
from openai import OpenAI
from typing import Any

class OpenAIClient:
    def __init__(self,api_key = "",base_url="",model=""):
        self.api_key = ""
        self.base_url = ""
        self.model=""
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        
    
    def stream(self,messages=[],stop=[],tools=[]) -> Any:
        response = self.client.chat.completions.create(
                        model=self.model,  # 填写需要调用的模型名称
                        messages=messages,
                        stream=True,
                        stop = stop,
                        # tools=tools,
                        # tool_choice="auto",  # 让模型自动决定是否调用函数
                    )

        for chunk in response:
            yield str(chunk.choices[0].delta.content)

if __name__ == "__main__":

    llm = OpenAIClient()
    res = llm.stream(messages=[{"role" : "user","content" : "你是谁"}])
    for r in res:
        print(r.replace("None",""),end="")

# %%
