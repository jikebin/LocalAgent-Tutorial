#%%
from langgraph.graph import StateGraph,END
from typing import Annotated,Any,TypedDict,List,Optional
from langgraph.types import StreamWriter
from openai_client import OpenAIClient
from Tools_and_Templates import get_system_prompt,available_functions
import json

import operator

# 创建状态结构

class GlobalState(TypedDict):
    messages : Annotated[List[Any],operator.add]
    stop : List[str] # 停用词
    system : List[Any] # 系统提示
    

def parse_plugin_split(text: str):
    text = text.replace("\\n","\n")
    i = text.rfind('\nAction:')
    j = text.rfind('\nAction Input:')
    k = text.rfind('\nObservation')
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

def fuction_to_call(function_name, function_args):
    function_obj = available_functions.get(function_name, None)
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

# 创建Agent节点函数
def chat_node(state: GlobalState, writer: StreamWriter):
    llm = OpenAIClient()
    res = llm.stream(messages=state["system"] + state["messages"], stop=state["stop"])
    content = ""
    for r in res:
        writer(r)
        content += r
    return {"messages": [{"role": "assistant", "content": content}]}

# 创建Function节点函数
def function_node(state: GlobalState, writer: StreamWriter):
    content = state["messages"][-1]["content"]
    plugin_name, plugin_args = parse_plugin_split(content)
    observation = fuction_to_call(plugin_name, plugin_args)
    observation = "Observation:" + str(observation)
    writer(observation)
    return {"messages": [{'role': "user", 'content': observation}]}

# 创建条件边
def condition_edge(state: GlobalState, writer: StreamWriter):
    content = state["messages"][-1]["content"]
    plugin_name, plugin_args = parse_plugin_split(content)
    if plugin_name:
        return True
    else:
        return False
    

builder = StateGraph(GlobalState)
builder.add_node("chat", chat_node)
builder.add_node("tool", function_node)
builder.set_entry_point("chat")
builder.add_conditional_edges(source="chat",path=condition_edge,path_map={True: "tool", False: END})
builder.add_edge("tool", "chat")
graph = builder.compile()

#%%
state = {
    "messages": [{"role": "user", "content": "帮我调用工具生成一个md5加密的哈希值"}],
    "stop": ["Observation:", "Observation:\n"],
    "system": [{"role": "system", "content": get_system_prompt()}],
}

for event in graph.stream(state, stream_mode="custom"):
# for event in graph.stream(state, stream_mode="values"):
    print(event)

# %%
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))
# %%
# from langgraph.checkpoint.memory import MemorySaver
# from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import create_react_agent
# def check_weather(location: str) -> str:
#     return f"The weather in {location} is sunny."

# tools = [check_weather]
# model = ChatOpenAI(model="gpt-4o")
# graph = create_react_agent(model, tools=tools)
# inputs = {"messages": [("user", "what is the weather in sf")]}
# for s in graph.stream(inputs, stream_mode="values"):
#     message = s["messages"][-1]
#     if isinstance(message, tuple):
#         print(message)
#     else:
#         message.pretty_print()