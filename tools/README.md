# Code_Interpreter

代码解释器的功能，在实际开发中如果安装在本地是一个非常危险的事情，所以一般都是单独创建一个虚拟环境来运行的。可以使用Docker容器来构建一个服务。

## 环境
[requirements.txt](./Code_Interpreter/requirements.txt)

## 测试代码

[code_interpreter.py](./Code_Interpreter/code_interpreter.py)

如果要测试绘图功能，需要先执行 [update_server.py](../utils/update_server.py) 服务，这样生成的图像才会以url的形式输出。


## LLM使用Code_Interpreter

- 首先，需要先封装成一个方法
- 然后，编写对应方法的功能描述，一般为Json Schema 格式
- 最后，将 Prompt 加入到 System 中即可。

> 该功能会加入到 multi_agent 中


# markdown 转 PDF

## 环境
在使用requirements.txt安装依赖包之前请先安装 wkhtmltopdf,因为`pdfkit`是wkhtmltopdf的一个Python封装

[wkhtmltopdf的官网](https://wkhtmltopdf.org/downloads.html)

[requirements.txt](./Markdown_To_PDF/requirements.txt)
```python
pip install -r requirements.txt
```