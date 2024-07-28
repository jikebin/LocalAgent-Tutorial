"""
用于统一的内存管理
"""
#%%
import copy

class MemoryManage(object):
    def __init__(self, messages=None):
        self.Q = 'Question'
        self.A = 'Answer'
        self.P = 'Process'
        self.USER = "user"
        self.ASSISTANT = "assistant"
        if messages is None:
            self.Messages = []    # 统一的消息存储队列
            self.memory_dict = {} # 各自Agent自己的队列信息
        else:
            self.Messages = messages  # 传入的消息列表
            self.__init_memory_dict() # 统一数据
        self.len = len(self.Messages)

    # 根据messages初始化memory_dict
    def __init_memory_dict(self):
        self.memory_dict = {}
        for i,message in enumerate(self.Messages):
            name,_,state,time = message
            memory = self.memory_dict.get(name,None)
            if memory:
                memory["memory"].append(i)
                if state == self.Q:
                    # 这个字段标记了每个Q的索引位置，用于获取最近几轮的方案
                    memory['Q'].append(len(memory["memory"])-1)
            else:
                self.memory_dict[name] = {"memory":[i],"Q":[0]}
                

    # 插入消息
    def append(self,agent_name:str,message:dict,time=0):
        """
        message: {'role':'user','content':''}
        time: 模型输出或工具调用所用的时长
        """
        
        # 添加到统一的消息存储队列中
        ## 1.先判断是哪个流程：questions or answers or process
        state = ""
        # 获取当前name的消息队列索引
        indexs = self.memory_dict.get(agent_name)
        if message.get("role") == self.USER and not indexs:
            state = self.Q
        elif message.get("role") == self.USER and self.Messages[indexs.get("memory")[-1]][2] != self.P: #增加条件并且上一个不是P
            state = self.Q
        elif message.get("role") == self.ASSISTANT and not "Action:" in message.get("content"):
            state = self.A
        else:
            state = self.P
        ## 2.整理信息，添加到self.Messages
        self.Messages.append((agent_name,message,state,time))

        # 获得每个用户的记忆列表在Messages中的索引位置
        memory = self.memory_dict.get(agent_name,None)
        if memory:
            memory["memory"].append(self.len)
            if state == self.Q:
                # 这个字段标记了每个Q的索引位置，用于获取最近几轮的方案
                memory['Q'].append(len(memory["memory"])-1)
            self.memory_dict[agent_name] = memory
        else:
            self.memory_dict[agent_name] = {"memory":[self.len],"Q":[0]}
            

        self.len += 1

    
    # 获取消息,保留最近几轮,是否要过滤中间过程
    def get_memory(self,agent_name:str,top_n=5,ignore_p=False):
        # 增加健壮性
        if top_n == 0:
            top_n = 1
        memory = []
        
        
        index_dict = self.memory_dict.get(agent_name,{})
        
        if not index_dict and agent_name != "planner":
            return memory
        
        if agent_name == "planner":
            vv = []
            v_list = []
            for k,v in self.memory_dict.items():
                for i in v['Q']:
                    vv.append(v['memory'][i])
                v_list = v_list + v['memory']
            v_list.sort()
            q = []
            for i in range(len(v_list)):
                if v_list[i] in vv:
                    q.append(i)
            index_dict = {'memory':v_list, "Q":q}
                
        # 总长度超过top_n的情况
        if top_n < 0 or len(index_dict["Q"]) <=top_n:
            start = 0
        else:
            start = index_dict['Q'][-top_n]
        
        for i in index_dict['memory'][start:]:
            if ignore_p:
                if self.Messages[i][2] != self.P:
                    memory.append(self.Messages[i][1])
            else:
                memory.append(self.Messages[i][1])
        return memory


    # copy 消息,并清空原有的memory_dict
    def copy_memory(self,source:str,target:str,top_n=6,ignore_p=True):
        # 清空原有的memory_dict,相当于清空了历史记录（伪清除）
        self.memory_dict[target] = {}
        # 增加健壮性
        if top_n == 0:
            top_n = 1
        index_dict = self.memory_dict.get(source,{})
        if not index_dict:
            return
        # 总长度超过top_n的情况
        if top_n < 0 or len(index_dict["Q"]) <=top_n:
            start = 0
        else:
            start = index_dict['Q'][-top_n]
        
        for i in index_dict['memory'][start:]:
            if ignore_p:
                if self.Messages[i][0] != self.P:
                    message = copy.deepcopy(self.Messages[i][1])
                    self.append(agent_name=target,message=message)
            else:
                self.append(agent_name=target,message=self.Messages[i][1])


    # 获取所有消息
    def get_messages(self):
        return self.Messages


if __name__ == "__main__":
    messages = [
        ('route', {'role': 'user', 'content': '你好'}, 'Question', 0),
        ('route', {'role': 'assistant', 'content': '你好'}, 'Answer', 0),
        ('route', {'role': 'user', 'content': '你好1'}, 'Question', 0),
        ('route', {'role': 'assistant', 'content': '你好1'}, 'Answer', 0),
        ('route', {'role': 'user', 'content': '你好2'}, 'Question', 0),
        ('route', {'role': 'assistant', 'content': '你好2'}, 'Answer', 0),
        ('11', {'role': 'user', 'content': '你好3'}, 'Question', 0),
        ('11', {'role': 'assistant', 'content': '你好3'}, 'Answer', 0),
        ('route', {'role': 'user', 'content': '你好4'}, 'Question', 0),
        ('route', {'role': 'assistant', 'content': '你好4'}, 'Answer', 0),
        ('22', {'role': 'user', 'content': '你好5'}, 'Question', 0),
        ('22', {'role': 'assistant', 'content': '你好5'}, 'Answer', 0)
    ]
    mm = MemoryManage(messages)
    # mm.append("route",{"role" :"user" , 'content': "你好"})
    # mm.append("route",{"role" :"assistant" , 'content':"你好"})
    # mm.append("route",{"role" :"user" , 'content': "你好1"})
    # mm.append("route",{"role" :"assistant" , 'content': "你好1"})
    # mm.append("route",{"role" :"user" ,'content': "你好2"})
    # mm.append("route",{"role" :"assistant" , 'content':"你好2"})
    # mm.append("11",{"role" :"user",'content': "你好3"})
    # mm.append("11",{"role" :"assistant" , 'content':"你好3"})
    # mm.append("route",{"role" :"user" , 'content': "你好4"})
    # mm.append("route",{"role" :"assistant" , 'content': "你好4"})
    # mm.append("22",{"role" :"user" , 'content': "你好5"})
    # mm.append("22",{"role" :"assistant" , 'content': "你好5"})

# %%
