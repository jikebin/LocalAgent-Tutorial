#%%
from langgraph.graph import StateGraph,END
from typing import Annotated,Any,TypedDict,List,Optional
from langgraph.types import StreamWriter
from openai_client import OpenAIClient
from Tools_and_Templates import get_system_prompt,available_functions
from langgraph.checkpoint.memory import MemorySaver # 添加记忆功能
from langgraph.checkpoint.memory import PersistentDict
# from langgraph.checkpoint.memory import PostgresSaver
import json

import operator

# 创建状态结构

class GlobalState(TypedDict):
    messages : Annotated[List[Any],operator.add]
    stop : List[str] # 停用词
    system : List[Any] # 系统提示
    is_show : Optional[bool]
    

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
    if state["is_show"]:
        tmp = "Observation: 该用户无权限调用此工具!"
        writer(tmp)
        return {"messages": [{'role': "user", 'content': tmp}]}

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
memory = MemorySaver()
graph = builder.compile(checkpointer=memory,interrupt_before=["tool"])

#%%
state = {
    "messages": [],
    "stop": ["Observation:", "Observation:\n"],
    "system": [{"role": "system", "content": get_system_prompt()}],
    "is_show" : False,
}
config = {"configurable": {"thread_id": "1"}} # 与memory相关，通过thread_id区分不同用户的会话
while True:
    question = input("请输入问题：")
    if question == "exit":
        break
    state["messages"] = [{"role": "user", "content": question}]
    for event in graph.stream(state, config=config, stream_mode="custom"):
        print(event,end="")
    new_state = graph.get_state(config=config)
    if new_state.tasks: # 这里也可以使用new_state.next 来判断是否是断点终止。
        print("是否允许模型调用该工具？")
        input_str = input("请输入 是 或 否：")
        if input_str == "是":
            pass
        else:
            new_state.values["is_show"] = True
            graph.update_state(config, new_state.values)
        for event in graph.stream(None, config=config, stream_mode="custom"):
            print(event,end="")


#%%

# 查询memory
# m_all = memory.list(config=None) # 查询所有线程的memory的所有状态变化,生成式
# m_one = memory.list(config=config) # 查询单线程的状态变化。
# tup = memory.get_tuple(config=config) # 返回当前图状态
# %%
