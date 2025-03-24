

import openai

# 设置 OpenAI API 密钥
openai.api_key = "your-openai-api-key"

# 定义一个示例函数
def get_current_time():
    import datetime
    return str(datetime.datetime.now())

# 创建一个能够流式输出的函数
def handle_streaming_function_call():
    try:
        # 发起请求并启用流式输出
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 使用 GPT-4 模型
            messages=[
                {"role": "system", "content": "你是一个有用的助手。"},
                {"role": "user", "content": "请告诉我当前时间。"}
            ],
            functions=[{
                "name": "get_current_time",
                "description": "返回当前的时间。",
                "parameters": {}
            }],
            function_call="auto",  # 自动触发 function call
            stream=True             # 启用流式输出
        )

        # 处理流式输出的每一块
        for part in response:
            # 输出流式内容
            if 'choices' in part:
                choice = part['choices'][0]
                message = choice.get('message', {})
                if message.get('function_call'):
                    # 执行 function call
                    function_name = message['function_call']['name']
                    print(f"Function called: {function_name}")
                    
                    # 例如，在这里你可以直接执行该函数并返回结果
                    if function_name == "get_current_time":
                        result = get_current_time()
                        print(f"Function result: {result}")
                if message.get('content'):
                    print(message['content'], end='', flush=True)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    handle_streaming_function_call()
