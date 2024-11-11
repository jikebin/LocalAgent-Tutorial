"""
agent 显示设置
"""
#%%
import sys
import os
sys.path.append(os.path.split(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))[0])
import queue
import time
import json
import re

class AgentShow:
    def __init__(self,agent) -> None:
        self.agent = agent
        self.pipeline = queue.Queue()  # 存储流式的输出队列
        self.cache_size = 4   # 输出队列的缓存长度
        self.content_all = ""
        self.answer = "process"
        self.flow = ""  # 用于标记流程的状态：Thought,Action,Action Input,Observation,Final Answer
        self.id = 0
        self.type = self.answer


        # 用于替换的映射内容
        self.mapping_dict = {
            "Thought:" : {"state":"process", "replace" : ""},
            "Action:" : {"state":"process", "replace" : "工具调用中..."},
            "Action Input:" : {"state":"process", "replace" : "\n"},
            "Observation" : {"state":"process", "replace" : "获取数据中...\n"},
            "Final Answer:" : {"state":"answer", "replace" : ""},
        } 
    
    # 通过正则表达式匹配文档列表
    def document_split(self,text):
        # 正则表达式
        pattern = re.compile(
            r'<div class="thoughtItem">参考信息:\s*(?P<content>.*?)\s*以上内容来自：<a href="(?P<url>[^"]*?)"[^>]*?>(?P<source>.*?)</a>',
            re.DOTALL
        )

        # 提取内容
        matches = pattern.finditer(text)

        # 生成列表
        file = [{"content": match.group("content").strip(), 
                "source": match.group("source").strip(), 
                "url": match.group("url")} for match in matches]
        return file


    # Event Stream 事件流
    def event_stream(self,content):
        # 用于判断是否替换为隐藏信息,存在则隐藏
        replace = self.mapping_dict.get(self.flow,{}).get("replace")
        # 判断是否为 document 数据
        file = self.document_split(content)
        data = {
            "type" : self.type
        }
        
        if file:
            return [f'data: {json.dumps({"type": "file","msg":msg},ensure_ascii=False)}\n\n' for msg in file]
        
        elif replace:
            if self.id == 0:
                data["text"] = replace
            else:
                # 隐藏数据
                data["text"] = "" 
        else:
            data["text"] = content
        # 用于计数，判断是否为第一个数据
        
        self.id +=1
        return  [f"data: {json.dumps(data,ensure_ascii=False)}\n\n"]

    # 输出内容过滤
    def output_filter(self,content):        
        self.content_all += content.strip()
        # 向队列中添加元素
        self.pipeline.put(content)

        if self.cache_size <= self.pipeline.qsize():
            # 获取队列中的缓存信息
            cache_content = "".join(self.pipeline.queue)
            for k,v in self.mapping_dict.items():
                if k in cache_content:
                    # 清空缓存队列
                    self.pipeline.queue.clear()
                    # 数据拆分
                    sp_list = cache_content.split(k)
                    self.pipeline.put(sp_list[-1])
                    # 转换为 event_stream 数据
                    stream = self.event_stream(sp_list[0])
                    # 切换状态
                    self.type = v["state"]
                    self.id = 0
                    self.flow = k
                    return stream

            
            text = self.pipeline.get()
            return self.event_stream(text)
        
        return self.event_stream("")
    
        

    # chat内容
    def chat(self,query, history):
        for content in self.agent.chat(query = query, history = history):
       
            if isinstance(content,str):
                new_content = self.output_filter(content)
                for stream in new_content:
                    yield stream
            else:
                print("非str数据：",content)
        # 最后输出
        text = "".join(self.pipeline.queue)
        self.pipeline.queue.clear()
        for stream in self.event_stream(text):
            yield stream
            

    # 历史记录
    def get_messages(self):
        return self.agent.get_messages()
    

    # 获取memory
    def get_memory(self):
        return self.agent.get_memory()


    def get_system(self):
        return self.agent.system
    

if __name__ == "__main__":
    from ..example_agent.AgentDemo import AgentDemo
    agent = AgentDemo()
    agent = AgentShow(agent=agent)
    que = "北京的pm2.5"
    for content in agent.chat(que,history=[]):
        print(content,end="")
# %%
