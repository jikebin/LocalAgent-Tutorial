import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from faiss_db.db_update import FaissDB
from faiss_db.single_file_embedding import SingleFileSplite,txt_splite

# 根目录
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 文件的根目录
DOCUMENT_ROOT_PATH = os.path.join(ROOT_PATH,"document_embedding","document")
# txt文件的根目录
TXT_ROOT_PATH = os.path.join(ROOT_PATH,"document_embedding","txt")



class Item(BaseModel):
    operator: str   # CRUD(增删改查)
    file_db: str     # 数据库id
    file_names: Optional[list] = None  # 要添加或者删除的文件名称
    query: Optional[str] = None   # 要查询的内容

class FaissAPI:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()
        self.db = FaissDB()

    def setup_routes(self):

        @self.app.post("/faiss/")
        def route_inner(item:Item):
            result = {'code': 1001, 'result': 'operator in [C, R, U, D]', 'msg':'error!'}

            if item.operator == "R" or item.operator == "read":
                result = self.query(item)

            elif item.operator == "C" or item.operator == "create":
                result = self.add(item)

            elif item.operator == "D" or item.operator == "delete":
                result = self.delete(item)

            return result
        

    # 添加数据
    def add(self,item:Item):
        # 获取对应数据库
        db = self.db.db_group.get(item.file_db,None)
        # 获取文件名称列表
        file_names = item.file_names
        if file_names:
            doc_list = []
            for document in file_names:
                f_name,suffix = os.path.splitext(document)
                # 先查找 txt 目录下是否有该文件名
                if os.path.exists(os.path.join(TXT_ROOT_PATH,f"{f_name}.txt")):
                    file_path = os.path.join(TXT_ROOT_PATH,f"{f_name}.txt")
                    fs = txt_splite(file_path)
                    doc_list.extend(fs)

                #TODO: 这里还需要再测试一下
                elif suffix in [".txt",".pdf",".doc",".docx"]:
                    file_path = os.path.join(DOCUMENT_ROOT_PATH,document)
                    print(file_path)
                    fs = SingleFileSplite(TXT_ROOT_PATH)
                    doc_list.extend(fs.auto_split(file_path))
                else:
                    return {'code': 1001, 'result': f"{document}文件类型不符合，可解析类型包括：[.txt,.pdf,.doc,.docx]", 'msg':'error!'}
            
            # 添加到数据库中
            db.add_document(doc_list)

            return {'code': 2000, 'result': "添加数据完成", 'msg':'success!'}
        else:
            return {'code': 1001, 'result': "请添加文件", 'msg':'error!'}
    

    # 删除数据
    def delete(self,item:Item):
        # 获取对应的数据库
        db = self.db.db_group.get(item.file_db,None)
        if db:
            # 过滤文件列表后缀并删除对应数据
            for name in item.file_names:
                f_name,_ = os.path.splitext(name)
                db.del_metadata(source = f_name)
            # 保存更新到本地
            db.save()

            return {'code': 2000, 'result': "删除数据完成", 'msg':'success!'}
        else:
            return {'code': 1001, 'result': '数据库不存在', 'msg':'error!'}


    # 查询数据
    def query(self,item:Item):
        # 获取对应的数据库
        db = self.db.db_group.get(item.file_db,None)
        if db:
            res = db.mmr_search(item.query)
            format_data = [ [doc.page_content,float(score)] for doc,score in  res]
            return {'code': 2000, 'result': format_data, 'msg':'success!'}
        else:
            return {'code': 1001, 'result': '数据库不存在', 'msg':'error!'}


    def get_app(self):
        return self.app

# 实例化 MyAPI 类并获取 FastAPI 应用
api = FaissAPI()
app = api.get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)

#%%
# '1001': 'test'