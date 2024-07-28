#%%
import os
import shutil
from docx2pdf import convert
import subprocess
import fitz 
import simplejson
import pandas as pd
import numpy as np
import re
import os
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
import warnings
warnings.filterwarnings('ignore')
#%%
class SingleFileSplite:
    def __init__(self, txt_dir) -> None:
        self.txt_dir = txt_dir
        self.all_dpf=[]
        self.documents_all = []
    def file_to_pdf(self, file_path):
        output_path = os.path.split(file_path)[0]
        f_name= os.path.splitext(file_path)
        if file_path.endswith(".pdf"):
            return file_path
        elif file_path.endswith(".docx"):
            subprocess.call(["soffice","--headless","--convert-to","pdf","--outdir", output_path , file_path,])
            os.remove(file_path)
            pdf_file_path = f_name[0] + '.pdf'
            return pdf_file_path
        elif file_path.endswith(".doc"):
            subprocess.call(["soffice","--headless","--convert-to", 'docx',"--outdir", output_path, file_path,],)
            os.remove(file_path)
            docx_path = f_name[0] + '.docx'
            subprocess.call(["soffice","--headless","--convert-to","pdf","--outdir", output_path, docx_path],)
            os.remove(docx_path)
            pdf_file_path = f_name[0] + '.pdf'
            return pdf_file_path
        elif file_path.endswith(".txt"):
            shutil.copy(file_path, self.txt_dir)
            os.remove(file_path)
            f_name= os.path.splitext(file_path)
            file_name = os.path.split(file_path)[-1]            
            txt_file_path = os.path.join(self.txt_dir, file_name)
            return txt_file_path
        else:
            print("文件格式不支持")  


    def get_num(self,str_a):
        al_num=re.findall(r"^\d+\s?\.+\s?\d*\s?\.?\s?\d*\s?\.?\s?\d*",str_a)#它匹配一个或多个数字，后面可以跟随一个或多个点（.），以及后续的可选数字。示例：1.23、2.3.4。
        bl_num=re.findall(r"^\d+\s?\．+\s?\d*\s?\．?\s?\d*\s?\．?\s?\d*",str_a)#用于匹配全角句号（．）分隔的数字格式。示例：１．２３、２．３．４。
        cl_num=re.findall(r"^[一二三四五六七八九十]+[、，]?",str_a)#匹配中文数字（如一、二、三）以及后续的可选逗号（、）或顿号（，）。示例：一、、二，。
        dl_num=re.findall(r"^\d+[、，]?",str_a)#匹配阿拉伯数字，后面可以跟随一个可选的逗号（、）或顿号（，）。示例：1、、2，。
        if len(al_num)>0:return al_num
        elif len(bl_num)>0:return bl_num
        elif len(cl_num)>0:return cl_num
        else:return dl_num
    #读取 PDF 文件中的文本内容，标记段落的开始和结束，并将处理后的段落文本合并保存到一个新的文本文件中。
    def pdf_to_dataframe(self,pdf_path):
        #每一页pdf转化为dataframe
        with fitz.open(pdf_path) as doc:  # open document
            for page_num, page in enumerate(doc, start=1):
                json_text = page.get_text('json')
                blocks = page.get_text('blocks')
                json_data = simplejson.loads(json_text)
                for k, block in enumerate(json_data['blocks']):
                    # 去除空白字符
                    try:
                        data = ''.join([char for char in blocks[k][4] if char.strip()])
                        if data:
                            if 'lines' in block.keys():
                                size = block['lines'][0]['spans'][0]['size']
                                self.all_dpf.append([size, data, len(data), page_num])
                    except:
                        pass
            all_data = pd.DataFrame(self.all_dpf, columns=['rank1', 'content', 'len_data', 'page_num'])
            all_data = all_data[~((all_data['len_data'] == 1) & (all_data['content'].str.match(r'^\d+$')))]#删除页数的行
            all_data[['is_sta', 'is_end']] = 0  # 标记出数据集中每条记录的开始（is_sta）和结束（is_end）
            #判断每一行的文字是否为开始或者结束
            for i in np.arange(1,len(all_data)):
                last_dt = all_data.iloc[i-1:i,:].content.values[0] #上一条记录的内容
                now_dt = all_data.iloc[i:i+1,:].content.values[0] #当前记录的内容
                p_list = self.get_num(now_dt) #从当前记录的内容中提取数字或编号信息，并将结果存储在 p_list
                if len(p_list)!=0:# 如果p_list 不为空（即当前记录中存在数字或编号），则将 is_sta 列的对应值设置为1，表示该行是段落的开始。
                    all_data['is_sta'].iloc[i:i+1] = 1
                if now_dt[-1]=='。' and  len(now_dt) < (len(last_dt)*0.8):#当前记录以句号（。）结尾且其长度小于上一记录长度的80%，则将 is_end 列的对应值设置为1，表示该行是段落的结束。
                    all_data['is_end'].iloc[i:i+1] = 1
            if not all_data.empty:
                if 'is_sta' not in all_data.columns:
                    all_data['is_sta'] = 0
                all_data.iloc[0, all_data.columns.get_loc('is_sta')] = 1
            else:
                print("all_data is empty.")
        return all_data

    def write_txt(self,all_data,txt_dir_path):
        dtas= pd.DataFrame()    #   用于存储标记为段落开始 (is_sta 列值为1) 的行数据
        start_end = all_data[all_data.is_sta==1]
        dtas = start_end.copy()
        if len(dtas) == 0:
            return True
        for i in range(len(start_end) - 1):
            s_index = start_end.index[i]
            e_index = start_end.index[i + 1]
            dd = all_data.loc[s_index:e_index - 1]
            dtas.at[s_index, 'content'] = ''.join(dd['content'])
        s_index = start_end.index[-1]
        dd = all_data.loc[s_index:]
        dtas.at[s_index, 'content'] = ''.join(dd['content'])
        content_list = dtas['content'].tolist()
        content_str = '\n'.join(content_list).encode('utf-8', errors='replace').decode('utf-8', errors='ignore')
        txt_file_path = os.path.join(txt_dir_path, self.file_name+ '.txt')
        with open(txt_file_path, "w", encoding='utf-8') as f:
            f.write(content_str)
        return txt_file_path

    def txt_splite(self, txt_path):
        file = os.path.split(txt_path)[-1]
        file_name = file[:file.rfind('.')] #文件名
        raw_documents = TextLoader(txt_path, encoding='utf8').load()
        dd = ''
        for i in raw_documents[0].page_content.split('\n'):
            if len(dd) + len(i) < 1500:
                dd += i + '\n'
            else:
                self.documents_all.append(Document(page_content=dd.strip() + f' {file_name}', metadata={'heading': dd.split('\n')[0], 'source': file_name}))
                dd = i + '\n'
        # 处理最后一段文本
        if dd:
            self.documents_all.append(Document(page_content=dd.strip() + f' {file_name}', metadata={'heading': dd.split('\n')[0], 'source': file_name}))
        return self.documents_all
    
    # 保存txt文件的文件夹路径
    def auto_split(self, file_path):
        file = os.path.split(file_path)[-1]
        self.file_name = file[:file.rfind('.')] #文件名
        pdf_file = self.file_to_pdf(file_path)
        if pdf_file.endswith('.pdf'):
            df = self.pdf_to_dataframe(pdf_file)
            path = self.write_txt(df,self.txt_dir)
            document = self.txt_splite(path)
        elif pdf_file.endswith('.txt'):
            document = self.txt_splite(pdf_file)
        return document
if __name__ == '__main__':
    txt_dir = r'txt'
    file_path = r'/'
    a = SingleFileSplite(txt_dir)
    path = a.file_to_pdf(file_path)
    doc = a.auto_split(path)
#%%
def txt_splite(txt_path):
    documents_all = []
    file = os.path.split(txt_path)[-1]
    file_name = file[:file.rfind('.')] #文件名
    raw_documents = TextLoader(txt_path, encoding='utf8').load()
    dd = ''
    for i in raw_documents[0].page_content.split('\n'):
        if len(dd) + len(i) < 1500:
            dd += i + '\n'
        else:
            documents_all.append(Document(page_content=dd.strip() + f' {file_name}', metadata={'heading': dd.split('\n')[0], 'source': file_name}))
            dd = i + '\n'
    # 处理最后一段文本
    if dd:
        documents_all.append(Document(page_content=dd.strip() + f' {file_name}', metadata={'heading': dd.split('\n')[0], 'source': file_name}))
    return documents_all

# %%
