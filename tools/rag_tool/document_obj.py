"""
该类用于提取pdf文档中的：表格，文本和图片信息
"""
#%%
import fitz
import pdfplumber
import cv2
import os
import shutil
# from cnocr import CnOcr

class PdfDocument(object):
    def __init__(self,path,tmp_img_dir="./tmp"):
        if not os.path.exists(tmp_img_dir):
            os.makedirs(tmp_img_dir)
        else:
            # 先删除在重新创建
            shutil.rmtree(tmp_img_dir)
            os.makedirs(tmp_img_dir)

        self.tmp_img_dir = tmp_img_dir
        self.path = path
        self.table_dict = {}  # 包括页码和表格内容
        self.text_dict = {}   # 包括页码和文本内容
        self.img_dict = {}    # 包括页码，图像地址 和 图像转文本信息

    
    # 读取pdf中的表格信息
    def _get_tables(self):
        with pdfplumber.open(self.path) as a:
            page_all = a.pages
            for i,page in enumerate(page_all):
                page_tables = page.extract_tables()
                if len(page_tables)==0:
                    continue
                else:
                    self.table_dict[i] = page_tables  # 这个是多个表格的列表
        
    
    # 读取pdf中的文本和图像
    def _read_pdf(self):
        img_index = 0
        doc = fitz.open(self.path)
        for i,page in enumerate(doc):
            # 提取文本信息
            text = page.get_text()
            # 添加到属性中
            self.text_dict[i] = text

            # 提取图片信息
            image_list = page.get_images(full=True)
            for img in image_list:
                base_image = doc.extract_image(img[0])
                image_bytes = base_image["image"]

                file_name = f"image_{img_index}.jpg"
                img_path = os.path.join(self.tmp_img_dir,file_name)
                print()
                # 保存图片
                with open(img_path, "wb") as f:
                        f.write(image_bytes)
                # 将图片路径添加到属性中
                self.img_dict[i] = {img_path: ""}
                img_index += 1
        doc.close()


    # 查看图像
    def _show_img(self,img_path):
        img = cv2.imread(img_path)
        cv2.imshow(img_path,img)
        cv2.waitKey(0)
    

    # 解析pdf数据
    def analysis_pdf(self):
        # 读取表格信息
        self._get_tables()

        # 读取pdf中的文本和图像
        self._read_pdf()

        print("解析完毕")

    # 读取所有的文本信息
    def read_text(self):
        content = ""
        for i,page in self.text_dict.items():
            content += page
        return content



#%%
if __name__ == "__main__":
    path = r"D:\学习笔记\19向量检索\大连爱渥特机器人科技有限公司八角管抓手项目环境影响报告表.pdf"
    doc = PdfDocument(path)
    doc.analysis_pdf()

# %%
