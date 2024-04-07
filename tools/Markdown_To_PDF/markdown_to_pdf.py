import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import pdfkit
from xvfbwrapper import Xvfb
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin
from utils.update_file import upload_file
from utils.random_id import get_id


class GenerateReport:
    def __init__(self):
        self.root_dir = os.path.split(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))[0]

    # 将 markdown 文本 转换为 pdf 文件
    def _mar2pdf(self,markdown_string, output_file):
        # 将Markdown转换为HTML
        md = (
                MarkdownIt('commonmark' ,{'breaks':True,'html':True,'linkify':True,'typographer':  True})
                .use(front_matter_plugin)
                .use(footnote_plugin)
                .enable('table')
            )
        html_text = md.render(markdown_string)

        # 在HTML中嵌入CSS样式来使用已安装的中文字体
        # 在HTML中嵌入CSS样式来使用已安装的中文字体
        html_with_style = f"""<html>
        <head>
            <meta charset="UTF-8">
            <style>
            table {{
                /* 给表格添加边框 */
                border-collapse: collapse;
                width: 100%;
                text-align: center; /* 表格内的文本居中 */
            }}
            th, td {{
                border: 1px solid black; /* 表头和表格数据单元格边框 */
                padding: 8px; /* 单元格内填充空间 */
            }}
        </style>
        </head>
        <body><div align="left">{html_text}</div></body>
        </html>"""
        # 配置pdfkit选项
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Content-Type', 'text/html; charset=utf-8')
            ],
            'no-outline': None
        }
        # 配置pdfkit
        # TODO:这里需要更改
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        # 启动虚拟 X server
        with Xvfb():
            # 将HTML转换为PDF
            pdfkit.from_string(html_with_style, output_file, options=options, configuration=config)
        
        return 'ok'

    # markdown 转换为 url
    def markdown_to_url(self,str_markdown):
        file_name = get_id() + ".pdf"
        file_path = os.path.join(self.root_dir,file_name)
        # 解析markdown格式
        try:
            if "```" in str_markdown:
                pattern = r'```(markdown)\s*(.*?)\s*```'
                blocks = re.findall(pattern, str_markdown, re.DOTALL)
                blocks[0] = list(blocks[0])
                if blocks:
                    mar_content = blocks[0][1]
                    # 将markdown转换为pdf
                    res = self._mar2pdf(mar_content,file_path)
                    if res == 'ok':
                        # 将pdf上传，获得url链接
                        file_url = upload_file(file_path)
                        return  f"""<iframe src="{file_url}" style="width:90%;height:400px;display:block;margin:0 auto;border:none"></iframe>"""
                        
        except Exception as e:
            pass

        return "markdown转换失败"
    
    
    

#%%
if __name__ == "__main__":
    gr = GenerateReport()
    markdown_str = """
```mardown
## 标题


### 表格

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Row 1, Col 1 | Row 1, Col 2 | Row 1, Col 3 |
| Row 2, Col 1 | Row 2, Col 2 | Row 2, Col 3 |
| Row 3, Col 1 | Row 3, Col 2 | Row 3, Col 3 |

```
"""
    gr.markdown_to_url()