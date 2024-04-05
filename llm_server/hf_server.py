#%%
from fastapi import FastAPI, Request
from transformers import AutoModelForCausalLM, AutoTokenizer,StoppingCriteria,StoppingCriteriaList
import uvicorn
from transformers import TextIteratorStreamer
from sse_starlette.sse import ServerSentEvent, EventSourceResponse
from threading import Thread
import torch

device = "cuda"
app = FastAPI()


"""
如果要使用下面的命令启动，请打开下面的模型加载方法，并注释掉： __name__ == '__main__' ，下面的模型加载内容
uvicorn Qwen_server_stream_new:app --workers 2 --host 0.0.0.0 --port 11434
"""
# -------------------------------------------------
# model = None
# tokenizer = None

# @app.on_event("startup")
# async def load_model():
#     global model, tokenizer
#     model = AutoModelForCausalLM.from_pretrained(
#         "/home/QwenProject/gemma-7b-it",
#         torch_dtype="auto",
#         device_map="cuda"
#     )
#     tokenizer = AutoTokenizer.from_pretrained("/home/QwenProject/gemma-7b-it")


class _SentinelTokenStoppingCriteria(StoppingCriteria):

    def __init__(self, sentinel_token_ids: torch.LongTensor,
                 starting_idx: int):
        StoppingCriteria.__init__(self)
        self.sentinel_token_ids = sentinel_token_ids
        self.starting_idx = starting_idx

    def __call__(self, input_ids: torch.LongTensor,
                 _scores: torch.FloatTensor) -> bool:
        for sample in input_ids:
            trimmed_sample = sample[self.starting_idx:]
            # Can't unfold, output is still too tiny. Skip.
            if trimmed_sample.shape[-1] < self.sentinel_token_ids.shape[-1]:
                continue

            for window in trimmed_sample.unfold(
                    0, self.sentinel_token_ids.shape[-1], 1):
                if torch.all(torch.eq(self.sentinel_token_ids, window)):
                    return True
        return False


# 如果希望可以并发访问，去掉async，重新启动即可
async def predict(message: list):
    try:
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        text = tokenizer.apply_chat_template(
            message,
            tokenize=False,
            add_generation_prompt=True,
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        # 添加停用词列表,这里可以添加自定义停用词，或者修改为传入参数
        stop_words = ["Observation:","Observation:\n"]
        # 将停用词进行向量化
        stop_words_ids = [ tokenizer(stop_word,add_special_tokens=False,return_tensors="pt",).input_ids.to("cuda") for stop_word in stop_words]
        # 创建停用词操作列表
        stopping_criteria_list = StoppingCriteriaList([
            _SentinelTokenStoppingCriteria(
                sentinel_token_ids=stop_words_id,
                starting_idx=model_inputs.input_ids.shape[-1]) 
            for stop_words_id in stop_words_ids
        ])
        # 将停用词列表添加到 推理模型中
        generation_kwargs = dict(model_inputs, streamer=streamer, max_new_tokens=512,stopping_criteria=stopping_criteria_list)
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        for content in streamer:
            yield content.replace("\n", "\\n")
        yield "[DONE]"
    except:
        import traceback
        print(traceback.format_exc())


@app.post("/")
async def create_item(request: Request):
    json_post_raw = await request.json()
    generate  = predict(json_post_raw)
    return EventSourceResponse(generate)
    

if __name__ == '__main__':
    model = AutoModelForCausalLM.from_pretrained(
        "Qwen1.5-72B-Chat-AWQ", # 本地模型全路径
        # device_map="cuda:0"
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained("Qwen1.5-72B-Chat-AWQ") # 本地模型全路径
    
    uvicorn.run(app, host='0.0.0.0', port=11434, workers=1)


# nohup python hf_server.py > output.log &
#%%