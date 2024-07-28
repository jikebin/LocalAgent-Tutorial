"""
统一的调用接口，基础Agent
"""
#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_connection.llm_custom import CustomLLM
from multi_agent.utils import parse_plugin_split, get_system_prompt,markdown_to_json,api_calling
from multi_agent.memory_manage import MemoryManage
import time
import json5
from types import GeneratorType

class Agent:
    def __init__(self,**kwargs):
        self.ini_setting = kwargs.get("ini_setting",{})
        self.llm = CustomLLM()
        self.system = [] # 系统消息
        self.memory =  MemoryManage([])# 统一记忆存储
        self.NAME = self.ini_setting.get("name","base") # 用于记忆名称，以及工具调用的标识符，路由映射的标识符
        self.USER = "user"  # 角色
        self.ASSISTANT = "assistant" # 角色
        self.SYSTEM = 'system' # 角色
        self.top_n = self.ini_setting.get("top_n",6) # 最多提取最近n轮对话
        self.text=kwargs.get("text",{})  # 全局的临时变量存储
        self.maxLoops=self.ini_setting.get("maxLoops",1)  # 最大循环次数
        self.interval = self.ini_setting.get("interval",0)  # 自定义流式输出时间间隔
        self.chunk_size = self.ini_setting.get("chunk_size",20)  # 自定义流式输出截断长度
        self.ignore_p = self.ini_setting.get("ignore_p",False) # 是否忽略中间过程
        self.available_functions = self.ini_setting.get("available_functions",{}) # Agent可以调用的工具列表，在 init_system 中实现
        self.direct_output = self.ini_setting.get("direct_output",False)
        self.copy_source = self.ini_setting.get("copy_source",None)  # 拷贝数据的来源
        self.func = self.ini_setting.get("task_background",None)
        self.sys_suffix = self.ini_setting.get("sys_suffix","")
        self.screen = self.text.get("screen",False)
        tools_description = self.ini_setting.get("tools_description",[])
        if tools_description:
            sys = get_system_prompt(tools = tools_description,source = self.NAME,question=self.text.get('question', ""))
            self.system = [{"role": "system", "content": sys + self.sys_suffix}]
        self.start = -1
        self.text["config_name"] = self.ini_setting.get("name","") # 添加配置名称到text中

        
    # 初始化system
    def __update_system(self,system):
        if isinstance(system, dict):
            self.system = [system]
        elif isinstance(system,list):
            self.system = system
        elif isinstance(system, str):
            self.system = [{"role": "system", "content": system}]

    # 返回当前Agent的最近top_n轮对话
    def get_messages_n(self):
        return self.memory.get_memory(self.NAME,self.top_n,self.ignore_p)

    # 拷贝历史记录，一般用于总结或压缩内容的Agent
    def copy_memory(self):
        # 如果copy_source 存在，则开始拷贝，并清空历史记录
        if self.copy_source:
            self.memory.copy_memory(source=self.copy_source,target=self.NAME,top_n=self.top_n,ignore_p=self.ignore_p)


    # 判断是否需要将结果交给大模型输出
    def repetition_output(self,observation):
        try:
            if observation.get('is_show', False) == True:
                answer = "\nFinal Answer: " + observation.get("observation","")
                self.memory.append(agent_name=self.NAME,message={'role': self.ASSISTANT, 'content': answer})
                self.interval = observation.get('interval',0)
                return answer
        except Exception as e:
            pass
        return False
    

    def function_call_error(self,info):
        res = {
            "observation": f"{info}",
            "is_show": False,
        }
        return res
    
    # TODO:这里需要进一步优化
    def fuction_to_call(self,function_name, function_args):
        try:
            function_name = function_name.strip()
            # 解析 function_args to dict
            if "```" in function_args:
                if "```json" in function_args:
                    function_args = markdown_to_json(function_args)
            else:
                # 格式化json
                function_args = function_args[:function_args.rfind("}")+1]
                function_args = json5.loads(function_args)
            

            # 判断是否为 function_calling
            if function_name.startswith("api_calling") and type(function_args) == dict:
                return api_calling(function_name=function_name,**function_args,text=self.text)
            
            # 本地通用工具调用
            function_obj = self.available_functions.get(function_name, None)
            if function_obj:
                if type(function_args) == dict:
                    return function_obj(**function_args, text=self.text,memory=self.memory, function_name = function_name)
                else:
                    return function_obj(function_args,text=self.text)
        
        except Exception as e:
                return self.function_call_error(f"{function_name} 调用错误：{e}")
        

        return self.function_call_error(f"未找到该方法名称")

        
    # 初始化chat 变量
    def __init_chat(self,query,history,system):
        # 重新初始化history
        if isinstance(history, MemoryManage):
            self.memory = history
        elif isinstance(history,list):
            self.memory = MemoryManage(history)
        # 判断是否需要拷贝数据
        if self.copy_source:
            self.copy_memory()
        # 初始化计时器
        self.start = time.time()
        # 添加问题
        if self.func:
            query = self.func(query,self.text)
        self.memory.append(agent_name=self.NAME,message={'role': self.USER, 'content': query})
        # 更新system
        if system:
            self.__update_system(system)
    

    def chat(self, query, history=None,system=[],stop=["Observation:", "Observation:\n",]):
        self.__init_chat(query=query,history=history,system=system)
        loop_count = 0
        while True:
            # 控制循环次数
            if loop_count >= self.maxLoops and self.maxLoops > 0:
                # yield f"""Final Answer:{str(observation.get('observation',''))}"""
                yield f"""Final Answer:工具异常，无法完成任务"""
                break
            # 输出内容
            content_all = ""
            for content in self.llm.stream(self.system + self.get_messages_n(),stop):
                content_all += content
                yield content
            # 模型输出计时
            self.memory.append(agent_name=self.NAME,message={'role': self.ASSISTANT, 'content': content_all},time=time.time() - self.start)
            self.start = time.time()
            # 解析内容，不同的System描述，对应着不同的解析方式，可以自定义
            plugin_name, plugin_args = parse_plugin_split(content_all)
            if plugin_name and plugin_args:
                observation = self.fuction_to_call(plugin_name, plugin_args)
                # 如果是生成器则直接返回，兼容planning调用
                if isinstance(observation,GeneratorType):
                    for r in observation:
                        if type(r)==str:
                            yield r
                        elif isinstance(r,dict):
                            observation = r
                            break
                # 如果是字典则进行处理
                if isinstance(observation,dict):
                    # 输出大屏信息
                    if self.screen:
                        time.sleep(0.5)
                        yield observation.get("screen_info","")
                        self.text["screen_info"] = observation.get("screen_info","")
                        time.sleep(0.5)
                    # observation_content = "Observation:" + str(observation.get('observation',""))
                    observation_content = str(observation.get('observation',""))
                    # 工具调用计时
                    self.memory.append(agent_name=self.NAME,message={'role': self.USER, 'content': "Observation:" + observation_content},time=time.time() - self.start)
                    self.start = time.time()
                    if self.direct_output:
                        yield observation
                        break
                    else:
                        yield observation_content + "\n"
                    # 判断是否要给大模型回答
                    result_answer = self.repetition_output(observation)
                    if result_answer:
                        # 将直接返回的结果变为流式输出
                        for i in range(0, len(result_answer), self.chunk_size):
                            yield result_answer[i:i+self.chunk_size]
                            time.sleep(self.interval)
                        break
            else:
                break
            loop_count += 1
          
    # 获取统一的memory对象，用于在不同Agent之间进行传递
    def get_memory(self):
        return self.memory
    
    # 查看所有的 message 信息
    def get_messages(self):
        return self.memory.get_messages()


if __name__ == "__main__":
    text = {
        # "question" : "帮我计算一下 45 -23 + 10 等于多少",
    }
    env = Agent()
    que = "帮我计算一下 45 -23 + 10 等于多少"
    for content in env.chat(que,env.get_memory()):
            print(content,end="")
# %%
