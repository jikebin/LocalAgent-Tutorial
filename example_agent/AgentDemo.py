"""
可以调用基础大气查询工具的Agent
"""
#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_connection.llm_custom import CustomLLM
from Tools_and_Templates import get_system_prompt,available_functions  # 调用所有可用工具
import json
import copy
class AgentDemo:
    def __init__(self):
        self.llm = CustomLLM()
        self.system = [{"role": "system", "content": get_system_prompt()}] # 系统消息
        self.memory = [] # 记忆存储
        self.USER = "user"
        self.ASSISTANT = "assistant"
        self.available_functions = available_functions
    

    def fuction_to_call(self,function_name, function_args):
        function_obj = self.available_functions.get(function_name, None)
        if function_obj:
            try:
                if "```" in function_args:
                    return function_obj(function_args)
                # 解析json参数
                function_args = json.loads(function_args)
                return function_obj(**function_args)
            except Exception as e:
                return f"参数解析错误：{e}"
        else:
            return "未找到该方法名称"
        

    # 用于解析模型输出的工具内容
    def parse_plugin_split(self,text: str):
        text = text.replace("\\n","\n")
        i = text.rfind('\nAction:')
        j = text.rfind('\nAction Input:')
        k = text.rfind('\nObservation:')
        if 0 <= i < j:  # If the text has `Action` and `Action input`,
            if k < j:  # but does not contain `Observation`,
                # then it is likely that `Observation` is ommited by the LLM,
                # because the output text may have discarded the stop word.
                text = text.rstrip() + '\nObservation:'  # Add it back.
                k = text.rfind('\nObservation:')
        if 0 <= i < j < k:
            plugin_name = text[i + len('\nAction:'):j].strip()
            plugin_args = text[j + len('\nAction Input:'):k].strip()
            return plugin_name, plugin_args
        return '', ''

    

    def chat(self,query:str,history=[],system=[],stop=["Observation:", "Observation:\n"]):
        # 初始化历史记录
        self.memory = copy.copy(history)
        # 初始化system
        if system:
            self.system = system
        # 初始化问题
        self.memory.append({'role': self.USER, 'content': query})
       
        while True:
            content_all = ""
            for content in self.llm.stream(self.system + self.get_memory(),stop):
                content_all += content
                yield content
            self.memory.append({'role': self.ASSISTANT, 'content': content_all})
            # 解析内容，不同的System描述，对应着不同的解析方式，可以自定义
            plugin_name, plugin_args = self.parse_plugin_split(content_all)
            if plugin_name and plugin_args:
                observation = self.fuction_to_call(plugin_name, plugin_args)
                observation = "Observation:" + str(observation)
                yield observation
                self.memory.append({'role': self.USER, 'content': observation})
            else:
                break
    
    
    def get_memory(self):
        return self.memory

#%%
if __name__ == "__main__":
    # 工具测试：将“hello” 转换为MD5
    agent = AgentDemo()
    # 实现多轮对话
    while True:
        query = input("请输入您的问题：")
        if query == "exit":
            break
        for content in agent.chat(query,history=agent.get_memory()):
            print(content,end="")



# %%

