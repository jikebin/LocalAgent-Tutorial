#%% 同步代码
import queue
from ollama import Client

class OllamaClient:
    def __init__(self,model="yi:34b-chat-fp16") -> None:
        self.model = model
        self.host = "http://127.0.0.1:11434"
        self.stop = ['Observation:']
        self.pipeline = queue.Queue()
        self.client = Client(host=self.host)
        self.content_all = ""
        self.temperature = 0.7
        self.repeat_penalty = 1.1

    # 停用词过滤
    def stop_word_filter(self,content):
        # 向队列中添加元素
        self.pipeline.put(content)
        # 添加到content_all中
        self.content_all += content

        # 获取停用词中最大的停用词长度
        max_len = len(max(self.stop,key=lambda x:len(x)))
        if max_len < len(self.content_all):
            # 开始进行停用词过滤判断
            if any([word in self.content_all for word in self.stop]):
                # 有任意一个包含停用词，则将所有数据取出来，然后截断停用词后输出
                word_all = self.__clearqueue()
                # 根据分隔符列表对字符串进行分割
                for s in self.stop:
                    word_all = word_all.replace(s, '<|stop|>')
                split_data = word_all.split('<|stop|>')
                self.content_all = ""
                return split_data[0],False
            else:
                # 无停用词，则弹出最前面的内容，然后截取content_all
                word = self.pipeline.get()
                self.content_all = self.content_all[len(word):]
                return word,True

        # 无操作则返回空字符
        return "",True


    def __clearqueue(self):
        content = ""
        # 取出队列中的所有数据
        while not self.pipeline.empty():
            data = self.pipeline.get()
            content += data
        return content
        
                
    # 流式输出
    def stream(self,messages=[],stop=[]):
        if stop:
            self.stop = stop
        response = self.client.chat(
            model=self.model, 
            messages=messages,
            options={'temperature': self.temperature,"repeat_penalty": self.repeat_penalty},
            stream=True
        )
        for chunk in response:
            message = chunk.get("message", "")
            content = message.get("content", "")
            word,flag = self.stop_word_filter(content)  
            yield word   # 使用 yield 关键字生成输出
            if not flag: # 当 flag 为 Flase 时，停止输出
                return
            if chunk.get("done", False):
                #清空 pipeline
                yield self.__clearqueue()
                return

            
    # 非流式输出
    def chat(self,messages=[],stop=[]):
        if stop:
            self.stop = stop

        response = self.client.chat(
            model=self.model, 
            messages=messages,
            options={'temperature': self.temperature,'frequency_penalty': self.frequency_penalty,"repeat_penalty": self.repeat_penalty},
        )
        content = response.get("message", dict()).get("content", "")
        return content
                
                
if __name__ == "__main__":
    ll = OllamaClient()
    res = ll.stream(messages=[{"role": "user", "content": "你好"}],stop=["什么","!"])

    for r in res:
        print(r,end="")






# %%
