import os
from vllm import AsyncEngineArgs, AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from modelscope import AutoTokenizer, GenerationConfig
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
import uvicorn
from prompt_utils_qwen2 import build_message
import uuid
import json
from collections import defaultdict

# http接口服务
app = FastAPI()

# vLLM参数(按实际情况配置)
# model_dir = "/home/QwenProject/Qwen1.5-72B-Chat-AWQ"
model_dir = "/home/QwenProject/Qwen2.5-72B-Instruct-AWQ"
# model_dir = "/home/QwenProject/Qwen1.5-0.5B-Chat-AWQ"
tensor_parallel_size = 1
# gpu_memory_utilization=0.6
# quantization='gptq'
dtype = 'float16'


# vLLM模型加载
def load_vllm():
    global generation_config, tokenizer, stop_words_ids, engine

    # 模型生成参数配置qwen1.5默认配置 #########################
    generation_config = GenerationConfig.from_pretrained(model_dir, trust_remote_code=True)
    generation_config.top_p = 0.5 # default:0.8
    generation_config.temperature = 0.7 # default:0.7
    generation_config.repetition_penalty = 1.05
    generation_config.max_new_tokens = 1024 # 1024
    generation_config.max_window_size = 8192  # 组装prompt长度判断使用
    # ############### 结束 ####################################

    # qwen2.5配置 #################################################
    # generation_config = GenerationConfig.from_pretrained(model_dir, trust_remote_code=True)
    # generation_config.top_p = 0.8 # default:0.8
    # generation_config.temperature = 0.7 # default:0.7
    # generation_config.repetition_penalty = 1.05
    # generation_config.max_new_tokens = 1024 # 1024
    # generation_config.max_window_size = 8192  # 组装prompt长度判断使用
    # #####################结束 ######################################

    # 加载分词器
    tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)


    # 推理终止词
    stop_words_ids = list(tokenizer.added_tokens_decoder.keys())

    # 模型启动参数配置（vllm）
    args = AsyncEngineArgs(model_dir)
    args.tokenizer = model_dir
    args.tensor_parallel_size = tensor_parallel_size
    args.trust_remote_code = True
    args.max_num_batched_tokens = 8192  # 每个batch处理token的最大数量（即：每个iteration）
    args.max_model_len = 8192  # 最大模型上下文长度（batch中的每个sequence长度，包括 prompt + generated_tokens），Qwen-14B存在长文推理问题，此参数不可用。
    # args.enforce_eager = True  # 节约显存（每个GPU节约1~3GB），但是会导致推理速度变慢（因为每次运行都要构建图了）。
    # args.quantization=quantization
    # args.gpu_memory_utilization=gpu_memory_utilization
    args.dtype = dtype
    # args.worker_use_ray=False
    # args.engine_use_ray=False

    # 使用model_scope加载在线模型，默认是从huggingface加载，从本地加载模型时无需启用。
    # os.environ['VLLM_USE_MODELSCOPE']='True'

    engine = AsyncLLMEngine.from_engine_args(args)
    return generation_config, tokenizer, stop_words_ids, engine


generation_config, tokenizer, stop_words_ids, engine = load_vllm()



# 基于chat对话接口，自定义LLM生成参数
@app.post("/customized_chat")
async def customized_chat(request: Request):
    request = await request.json()

    message = request.get('message', [])
    stream = request.get("stream", False)
    stop = request.get("stop",[])
    
    prompt_text, prompt_tokens = build_message(generation_config, tokenizer,message=message)

    # vLLM请求配置
    sampling_params = SamplingParams(stop_token_ids=stop_words_ids,
                                     early_stopping=False,
                                     top_p=generation_config.top_p,
                                     top_k=-1 if generation_config.top_k == 0 else generation_config.top_k,
                                     temperature=generation_config.temperature,
                                     repetition_penalty=generation_config.repetition_penalty,
                                     max_tokens=generation_config.max_new_tokens,
                                     stop= stop)
    # vLLM异步推理（在独立线程中阻塞执行推理，主线程异步等待完成通知）
    results_iter = engine.generate(prompt=None, sampling_params=sampling_params, prompt_token_ids=prompt_tokens,
                                   request_id=str(uuid.uuid4().hex))

    # 流式返回，即迭代transformer的每一步推理结果并反复返回
    if stream:
        async def streaming_resp():
            async for result in results_iter:
                text = result.outputs[0].text
                for token_id in stop_words_ids:
                    text = text.replace(tokenizer.decode(token_id), '')
                yield (json.dumps({'text': text}) + '\0').encode('utf-8')

        return StreamingResponse(streaming_resp())

    # 整体返回
    async for result in results_iter:
        text = result.outputs[0].text

    # 清理停止词
    for token_id in stop_words_ids:
        text = text.replace(tokenizer.decode(token_id), '')
    ret = {"text": text}
    return JSONResponse(ret)


if __name__ == '__main__':
    uvicorn.run(app,
                host='0.0.0.0',
                port=11434,
                log_level="debug")

# conda activate  /home/user/.conda/envs/vllm
# nohup python vllm_server_qwen2.py > output.log &