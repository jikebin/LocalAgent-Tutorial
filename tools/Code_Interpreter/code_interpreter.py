#%%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.Code_Interpreter.BaseCodeInterpreter import BaseCodeInterpreter
from utils.update_file import upload_file
from utils.random_id import get_id


class CodeInterpreter:
    def __init__(self):
        self.dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.bc = BaseCodeInterpreter()

    # 解析plt代码
    def fig_interpret(self,py_code):
        """
        用于执行一段包含可视化绘图的Python代码，并最终获取一个图片类型对象
        :param py_code: 字符串形式的Python代码，用于根据需求进行绘图，代码中必须包含Figure对象创建过程
        :return：代码运行的最终结果
        """
        file_name = get_id() + ".png"
        file_path = os.path.join(self.dir_path,file_name)

        # 若存在plt.show()，则替换
        py_code = py_code.replace('plt.show()', f'plt.savefig("{file_path}")\nplt.close()')
        font_zh = """
import matplotlib
import pandas as pd
import numpy as np
# 配置matplotlib字体为支持中文的字体
matplotlib.rcParams['font.family'] = 'SimHei'  # 例如使用黑体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题
"""
        py_code = font_zh + py_code

        outputs,error_flag = self.bc.execute_code_and_return_output(py_code)
        if error_flag:
            return outputs
        
        # 上传图像
        url = upload_file(file_path)
        return "plt_img_url:" + url
    
    def run(self,code_markdown):
        if "```" in code_markdown:
            code_blocks = self.bc.extract_code_blocks(code_markdown)
            if code_blocks:
                if "plt.show()" in code_blocks[0]:
                    return self.fig_interpret(code_blocks[0])
        
                # 正常调用
                bc = BaseCodeInterpreter()
                observation,error_flag = bc.execute_code_and_return_output(code_blocks[0])
                if error_flag:
                    observation = f"代码执行出错，请检查代码\n{observation}"
                return observation
            else:
                return "请检查代码块是否以```python\n开头，以```结尾"
        else:
            return "未找到markdonw格式中的python代码段"

#%%
if __name__ == "__main__":
    code = CodeInterpreter()
    str_code ="""
```py
import matplotlib.pyplot as plt

# 创建数据点
x = [1, 2, 3, 4, 5]
y = [1, 4, 9, 16, 25]

# 绘制折线图
plt.plot(x, y)
plt.xlabel('x轴')
plt.ylabel('y轴')
plt.title('简单折线图示例')
plt.show()
```
"""
    res = code.run(str_code)

# %%
