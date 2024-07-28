# %%
from openai import OpenAI
from typing import Any

class OpenAIClient:
    def __init__(self,api_key = "",base_url="",model=""):
        self.api_key = api_key
        self.base_url = base_url
        self.model=model
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        
    
    def stream(self,messages=[],stop=[]) -> Any:
        response = self.client.chat.completions.create(
                        model=self.model,  # 填写需要调用的模型名称
                        messages=messages,
                        stream=True,
                        stop = stop
                    )

        for chunk in response:
            yield str(chunk.choices[0].delta.content)

if __name__ == "__main__":

    api_key = "EMPTY"
    base_url = "http://localhost:8080/v1"
    model = "chatglm3-6b"
    llm = OpenAIClient(api_key=api_key,base_url=base_url,model=model)
    res = llm.stream([{"role" : "user","content" : "你是谁"}])
    for r in res:
        print(r.replace("None",""),end="")

# %%
