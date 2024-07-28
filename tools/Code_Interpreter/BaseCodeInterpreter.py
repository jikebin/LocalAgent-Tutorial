#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from tools.Code_Interpreter.JupyterClient import JupyterNotebook

"""
只能用于非绘图的code场景
"""
class BaseCodeInterpreter:
    def __init__(self):
        self.nb = JupyterNotebook()

    @staticmethod
    def extract_code_blocks(text: str):
        # pattern = r'```python\s*(.*?)\s*```'
        pattern = r'```(python|py)\s*(.*?)\s*```'
        code_blocks = re.findall(pattern, text, re.DOTALL)
        if code_blocks:
            return [block[1].strip() for block in code_blocks]
    
    

    def execute_code_and_return_output(self, code_str: str):
        """
        outputs: Jupyter返回的内容
        error_flag:False表示正常返回，True表示代码错误
        """
        outputs, error_flag = self.nb.add_and_run(code_str)
        self.nb.close() # 清除内核
        return outputs, error_flag


if __name__ == '__main__':
    str = "```py\nprint('hello world')\n```"
    str ="""
```py
def add(a,b):
    return a + b
add(1,23)
```
"""
    # str = "```python\nresult = 5 + 5 + 12\nresult\n```"
    code_blocks = BaseCodeInterpreter.extract_code_blocks(str)
    print(code_blocks)

    bc = BaseCodeInterpreter()
    res = bc.execute_code_and_return_output(code_blocks[0])

# %%
