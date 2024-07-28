#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multi_agent.base_agent import Agent
from multi_agent.calling import available_functions,tools_single

class SingleAgent(Agent):
    def __init__(self, text,config={},**kwargs):
        self.text = text
        setting = self.init_setting(**config)  # 初始化配置信息
        super().__init__(ini_setting=setting,text=text)


    def init_setting(self,**kwargs):
        
        SYS_SUFFIX = "" # sys的补充信息

        config = {
            "name" : "single",
            "tools_description" : tools_single,
            "available_functions" :available_functions,
            "top_n" : 6,
            "maxLoops" : 5,  # 表示最大循环次数
            "direct_output" : False, # 表示直接输出调用工具内容
            "sys_suffix" : SYS_SUFFIX,
        }
        config.update(kwargs) # 更新自定义配置

        return config
    

if __name__ == "__main__":
    text = {

    }
    config = {
         "tools_description" : [
        {
            "name_for_human": "大气污染物预测",
            "name_for_model": "api_calling_air_predict",
            "description_for_model": "预测大气污染物",
            "parameters": [
                {
                    "name": "location",
                    "description": "地点名",
                    "required": True,
                    "schema": {"type": "String"}
                },
                {
                    "name": "time",
                    "description": "时间",
                    "required": True,
                    "schema": {"type": ["String"]}
                },
                {
                    "name": "pollutant",
                    "description": "污染物",
                    "required": True,
                    "schema": {"type": ["String"]}
                },
                
            ]
        }
        ],
    }
    agent = SingleAgent(text=text,config=config)
    que = "北京明天的pm2.5"
    # que = "45 + 34 - 10"
    for content in agent.chat(que,agent.get_memory()):
            print(content,end="")


# %%
