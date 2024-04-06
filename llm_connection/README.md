# 统一的调用接口

我们将所有的LLM服务接口封装到一个统一的接口中，以方便调用。
可以通过 [llm_custom.py](./llm_custom.py) 文件来查看具体的调用方法。

## 环境安装

```
pip install -r requirements.txt
```

## huggingface 服务客户端

- [x] [hf_client.py](./hf_client.py)

## ollama 服务客户端

- [x] [ollama_client.py](./ollama_client.py)

## 阿里云灵积模型平台客户端

- [x] [qwen_online_client.py](./qwen_online_client.py)

[灵积官网](https://dashscope.aliyun.com/)

## 腾讯千帆平台客户端

- [x] [qianfan_client.py](./qianfan_client.py)

[千帆官网](https://cloud.baidu.com/product/wenxinworkshop)

## 自定义客户端

满足如下要求：

- 实现一个 stream 方法即可


## 统一的调用接口

- [x] [llm_custom.py](./llm_custom.py)

## 说明

目前封装了部分的线上api服务，是方便前期本地化算力不足的情况下进行开发使用。这些平台也都支持各种开源模型的使用，后续在正式运行后可以替换成本地部署的相同模型服务。