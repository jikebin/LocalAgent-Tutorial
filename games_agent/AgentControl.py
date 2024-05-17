"""
可以调用基础大气查询工具的Agent
"""
#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_connection.llm_custom import CustomLLM
from games_agent.Tools_and_Templates import get_system_prompt,available_functions  # 调用所有可用工具
import json
import time

class AgentControl:
    def __init__(self):
        self.llm = CustomLLM()
        self.system = [{"role": "system", "content": get_system_prompt()}] # 系统消息
        self.memory = [] # 记忆存储
        self.USER = "user"
        self.ASSISTANT = "assistant"
        self.available_functions = available_functions
        self.top_n = 6 # 最多提取最近n轮对话
        self.max_loop = 10 # 最多循环n轮
    

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

    

    def control(self,process,control_queue, output_queue,stop=["Observation:", "Observation:\n"]):
        # 控制循环次数
        loop = 0
        while process.is_alive():
            # 等待片刻以便状态更新
            time.sleep(0.1)

            # 获取当前状态，保存到上下文中
            while not output_queue.empty():
                result = output_queue.get()
                self.memory.append({'role': self.USER, 'content': result})

            # 将状态发送给模型，让模型进行下一次行动
            content_all = ""
            for content in self.llm.stream(self.system + self.get_messages_n(),stop):
                content_all += content
                yield content

            # 解析内容，不同的System描述，对应着不同的解析方式，可以自定义
            plugin_name, plugin_args = self.parse_plugin_split(content_all)
            if plugin_name and plugin_args:
                # 获取用户输入并发送控制指令
                direction = self.fuction_to_call(plugin_name, plugin_args)
                if direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
                    control_queue.put(direction)
                elif direction == "EXIT":
                    process.terminate()
                    process.join()
                    print("游戏结束")
                    break
            else:
                self.memory.append({'role': self.USER, 'content': "输入的指令格式不正确，请重新按照格式输入指令完成贪吃蛇游戏"})
            
            # 控制循环次数
            loop += 1
            if loop >= self.max_loop:
                process.terminate()
                process.join()
                print("游戏结束")
                break
    
    
    def get_memory(self):
        return self.memory
    

    def get_messages_n(self):
        """
        从messages中提取top n 轮数据
        :param messages:  原始的messages数据
        :param n:  要提取的最近n轮对话
        :return: messages
        """
        memory = []
        top = 0
        for i in range(len(self.memory) -1,-1,-1):
            if self.memory[i]["role"] == "user":
                top += 1
            
            if top > self.top_n:
                memory = self.memory[i:]
                break
        else:
            memory = self.memory

        return list(memory)

#%%
if __name__ == "__main__":
    # 工具测试：将“hello” 转换为MD5
    agent = AgentControl()
    # 实现多轮对话
    while True:
        query = input("请输入您的问题：")
        if query == "exit":
            break
        for content in agent.chat(query,history=agent.get_memory()):
            print(content,end="")



# %%

