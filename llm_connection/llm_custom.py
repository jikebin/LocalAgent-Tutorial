#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_connection.hf_client import HuggingFaceClient
from llm_connection.ollama_client import OllamaClient
from llm_connection.qwen_online_client import QwenOnlineClient
from llm_connection.qianfan_client import QianFanClient

class CustomLLM:

    def __init__(self,source="huggingface",llm_name="") -> None:
        mapping_source = {
            "huggingface":HuggingFaceClient,
            "ollama":OllamaClient,
            "qwen_online":QwenOnlineClient,
            "qianfan_online":QianFanClient,
        }
        llm_obj = mapping_source.get(source,HuggingFaceClient)
        if llm_name:
            self.llm = llm_obj(llm_name)
        else:
            self.llm = llm_obj()

    
    # 流式输出
    def stream(self,messages=[],stop=[]):
        return self.llm.stream(messages,stop)


if __name__ == "__main__":
    llm = CustomLLM(source="huggingface")
    res = llm.stream(messages=[{"role": "user", "content": "你好"}],stop=["什么","!"])

    for r in res:
        print(r,end="")
# %%
