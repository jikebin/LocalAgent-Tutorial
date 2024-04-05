# 本地化部署 LLM Server

**特别说明**：我们所有的Agent开发都是基于 Chat 模型，并且以流式输出来实现的。
 
## 基于Hugging Face的Chat模型本地化部署

### 环境

在安装python项目环境之前，请确保您的电脑支持NVIDIA GPU，并且已经安装了CUDA和cuDNN。

[requirements.txt](./requirements.txt)

```
pip install -r requirements.txt
```

### 下载Chat模型

例如：
[Qwen1.5-72B-Chat-AWQ](https://huggingface.co/Qwen/Qwen1.5-72B-Chat-AWQ)

### 本地化部署

```
python hf_server.py
```

### 后台运行

```
nohup python hf_server.py > output.log &
```

### 访问客户端

> [hf_client.py](../llm_connection/hf_client.py)


## 基于Ollama的Chat模型本地化部署

[Ollama github](https://github.com/ollama/ollama)

补充：Ollama 虽然响应速度快，但是截止目前并不支持并发操作(后续可能会更新)，很难用于高并发的开发场景。

## 自定义Chat模型本地化

满足如下要求即可：
- 支持三种基本角色[system, user, assistant]
- 支持流式输出
- 支持并发操作（根据需求）
- 支持自定义停用词