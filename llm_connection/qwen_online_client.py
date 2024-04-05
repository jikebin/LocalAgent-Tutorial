#%%
import os
import dashscope
from http import HTTPStatus


dashscope.api_key=""

class QwenOnlineClient:
    def __init__(self,model='qwen-max-0107'):
        self.model=model
    def __call__(self,messages=[],stop=[]):
        
        response = dashscope.Generation.call(
            self.model,
            messages=messages,
            stop = stop,
            result_format='message',  # set the result to be "message" format.
        )
        if response.status_code == HTTPStatus.OK:
            assistant = response['output']['choices'][0]['message']['content']
            return assistant
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
        
    
    def stream(self,messages=[],stop=[]):
        responses = dashscope.Generation.call(
            self.model,
            messages=messages,
            result_format='message',  # set the result to be "message" format.
            stream=True,
            stop = stop,
            incremental_output=True  # get streaming output incrementally
        )
        for response in responses:
            if response.status_code == HTTPStatus.OK:
                yield response.output.choices[0]['message']['content']
            else:
                print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                    response.request_id, response.status_code,
                    response.code, response.message
                ))


#%%

if __name__ == "__main__":
    ll = QwenOnlineClient()
    res = ll.stream(messages=[{"role": "user", "content": "你好"}])

    for r in res:
        print(r,end="")

# %%
