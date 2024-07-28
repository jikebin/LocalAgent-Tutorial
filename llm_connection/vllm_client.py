# %%
import requests
import json 

class VllmClient:
    def __init__(self,**kwagrs):
        self.url = ""

    def stream(self,messages=[],stop=[]):
        response=requests.post(self.url,json={
            'message':messages,
            'stream': True,
            'stop':stop,
        },stream=True)
        
        # 流式读取http response body, 按\0分割
        start = 0
        for chunk in response.iter_lines(chunk_size=8192,decode_unicode=False,delimiter=b"\0"):
            if chunk:
                data=json.loads(chunk.decode('utf-8'))
                text=data["text"]
                yield text[start:]
                start = len(text)
                

if __name__ == "__main__":
    llm = VllmClient()
    res = llm.stream([{"role" : "user","content" : "介绍一下你自己"}],stop=[])
    for r in res:
        print(r,end="")
# %%
