#%%
import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])


from multi_agent.base_agent import Agent
import json


tools = [
    {
        "name_for_human": "SQL Interpreter",
        "name_for_model": "sql_interpreter",
        "description_for_model": "将输入的SQL代码传输至MySQL数据库的环境中进行运行，并最终返回SQL代码运行结果。 ",
        "parameters": [
            {
                "name": "sql_query",
                "description": "字符串形式的SQL查询语句，用于执行对MySQL数据库中各张表进行查询，并获得各表中的各类相关信息",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "args_format" : "json",
    },
]

def sql_interpreter(sql_query,**kwargs):
    return  {
        "observation": sql_query,
        "is_show": True,
        "interval": 0,
    }

available_functions = {
    "sql_interpreter" : sql_interpreter, 
}


class SqlAgent(Agent):
    def __init__(self, text,**kwargs):
        self.text = text
        setting = self.init_setting()  # 初始化配置信息
        super().__init__(ini_setting=setting,text=text)


    def init_setting(self,**kwargs):
        with open("./sql_desc.md","r",encoding="utf-8") as f:
            SYS_SUFFIX = f.read()  # sys的补充信息，增加数据字典
        
        config = {
            "name" : "sql",
            "tools_description" : tools,
            "available_functions" : available_functions,
            "top_n" : 6,
            "maxLoops" : 5,  # 表示最大循环次数
            "direct_output" : False, # 表示直接输出调用工具内容
            "sys_suffix" : SYS_SUFFIX,
        }
        config.update(kwargs) # 更新自定义配置

        return config
    

if __name__ == "__main__":
    text = {
        "is_debug" : True,
    }

    agent = SqlAgent(text=text)
    que = "北京昨天各区的pm2.5分别是多少"
    for content in agent.chat(que,agent.get_memory()):
        print(content,end="")
#%%

