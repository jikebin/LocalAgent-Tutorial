
# %%

import requests
import queue

class HuggingFaceClient:
    def __init__(self,model="") -> None:
        self.model = model
        self.url = "http://127.0.0.1:11434"
        self.stop = ['Observation:']
        self.content_all = ""
        

    # 流式输出
    def stream(self,messages=[],stop=[]):
        if stop:
            self.stop = stop
        try:
            response = requests.post(self.url, json=messages, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data:"):
                    content = decoded_line.replace("data: ","")
                    yield content
                
        except requests.exceptions.RequestException as e:
            yield f"请求发生错误：{e}"
        
                
if __name__ == "__main__":
    ll = HuggingFaceClient()

    mes = [{'role': 'system',
  'content': 'A helpful and general-purpose AI assistant that has strong language skills.\nSystem current date:2024-04-03\nAnswer the following questions as best you can. You have access to the following APIs:\n\nplot: Call this tool to interact with the 绘图工具 API. What is the 绘图工具 API useful for? 该工具可以在有excel数据的链接前提下或自定义json格式数据下，对这个数据进行绘图。它支持各种绘图任务，包括生成各种类型的图表，如柱状图、条形图、折线图和饼图等。 Parameters: [{"name": "task", "description": "请明确说明需操作的文件或JSON数据任务，包括所需的数据图表绘制要求（包括图表类型）。请务必在每次请求时提供完整的数据或相关链接。", "required": true, "schema": {"type": "string"}}] Format the arguments as a JSON object.\n\ndata: Call this tool to interact with the 环境污染物数据查询分析及污染原因查询 Agent API. What is the 环境污染物数据查询分析及污染原因查询 Agent API useful for? 可以查询环境数据、环境数据分析及污染原因查询的Agent，根据条件查询环境类（水，大气）污染物浓度、预测浓度、排名、同比、环比、首要污染物、污染等级、保优余量、水平余量、综合分析、污染原因等数据信息以及环境数据分析及污染原因分析。支持多时间，多地点等复杂任务处理。 Parameters: [{"name": "task", "description": "需要查询数据的信息任务描述", "required": true, "schema": {"type": "string"}}] Format the arguments as a JSON object.\n\nnews: Call this tool to interact with the 新闻信息查询 API. What is the 新闻信息查询 API useful for? 用于查询各种新闻和热点，并且可以对查询到的结果进行分析和统计 Parameters: [{"name": "task", "description": "查询的新闻相关任务描述", "required": true, "schema": {"type": "string"}}] Format the arguments as a JSON object.\n\nreport: Call this tool to interact with the 生成报告 API. What is the 生成报告 API useful for? 会自动总结对话内容并生成pdf报告链接 Parameters: [{"name": "task", "description": "生成报告的任务描述", "required": true, "schema": {"type": "string"}}] Format the arguments as a JSON object.\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [plot, data, news, report]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can be repeated zero or more times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\n'},
           {'role': 'user', 'content': '北京今天的pm2.5'}
           ]
    
    res = ll.stream(messages=mes,stop=[])
    for r in res:
        print(r,end="")
# %%
