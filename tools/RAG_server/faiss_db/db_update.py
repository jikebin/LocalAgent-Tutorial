#%%
import sys
import os
sys.path.append(os.path.split(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))[0])
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from typing import List
import shutil

# 项目根目录
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Embedding 模型路径
EMBEDDING_MODEL_PATH = os.path.join(ROOT_PATH,"model","piccolo-large-zh")
# 数据库ID映射配置路径
DB_MAPPING_PATH = os.path.join(ROOT_PATH,"faiss_db","db_mapping.json")
# 数据库的根目录
DB_ROOT_PATH = os.path.join(ROOT_PATH,"db")



class EmbeddingDB:
    def __init__(self,db,save_path,embeddings=None) -> None:
        self.db = db
        self.save_path = save_path
        self.embeddings = embeddings
        self.id_mapping = {} # 内容和ID的映射关系,不保留重复id
        self.id_mapping_deep = {} # 内容和ID的映射关系,保留重复id


    # 构建内容和id的映射关系，这里先假设没有重复内容
    def init_mapping(self):
        for _,id in self.db.index_to_docstore_id.items():
            doc = self.id_search(id)
            self.id_mapping[doc.page_content] = id


    # 构建内容和id的映射关系，允许内容有重复
    def init_mapping_deep(self):
        for _,id in self.db.index_to_docstore_id.items():
            doc = self.id_search(id)
            if self.id_mapping_deep.get(doc.page_content):
                # 存在表示已经有内容了，需要添加即可
                self.id_mapping_deep.get(doc.page_content).append(id)
            else:
                self.id_mapping_deep[doc.page_content] = [id]

    # 添加数据
    def add(self,passages: List[str],metadata={},auto_save=True):
        assert type(passages) == list, "passages参数格式应该为：List[str]"
        assert type(metadata) == dict, "metadata参数格式应该为 Dict"
        documents_all=[]
        for p in passages:
            documents_all.append(Document(page_content=p,metadata=metadata))
        self.db.add_documents(documents_all)
        if auto_save:
            self.save()
        print("添加完成")

 
    # 添加document数据
    def add_document(self,docs:List[Document],auto_save=True):
        assert type(docs) == list and type(docs[0] == Document), "docs参数格式应该为：List[Document]"
        self.db.add_documents(docs)

        if auto_save:
            self.save()
        
        print("添加完成")
      

    # 保存数据
    def save(self):
        self.db.save_local(self.save_path)
        

    # 相似度搜索k个内容
    def similarity_search(self,query,k=5):
        return self.db.similarity_search_with_score(query, k=k)
    


    def mmr_search(self,query, k=5):
        # 调用原始方法或实现
        query_vector = self.embeddings.embed_query(query)
        return self.db.max_marginal_relevance_search_with_score_by_vector(query_vector, k=k)
    

    
    # 根据ID搜索文件
    def id_search(self,id) -> Document:
        return self.db.docstore.search(id)
    
    # 根据meta信息删除数据
    def del_metadata(self,**kwargs):
        auto_save = kwargs.get("auto_save",False)
        del_ids = []
        for _,id in self.db.index_to_docstore_id.items():
            doc = self.id_search(id)
            # 用于判断metadata 和传入的参数是否完全相等
            for key, value in kwargs.items():
                if doc.metadata.get(key) != value:
                    break
            else:
                del_ids.append(id)
        # 获取所有待删除的id信息，准备删除
        if del_ids:
            self.db.delete(del_ids)
            if auto_save:
                self.save()
        print(f"已删除{len(del_ids)}条数据")

    
    # 根据content删除，只删除最后一个content
    def del_content(self,chunk_list:List[str],auto_save=False):
        assert type(chunk_list) == list, "参数格式应该为：List[str]"
        # 构建id映射关系
        self.init_mapping()
        del_ids = []
        for chunk in chunk_list:
            id = self.id_mapping.get(chunk,"")
            if id:
                del_ids.append(id)

        # 获取所有待删除的id信息，准备删除
        if del_ids:
            self.db.delete(del_ids)
            if auto_save:
                self.save()
        # 清空旧的id映射关系
        self.id_mapping = {}
        print(f"已删除{len(del_ids)}条数据")
        

    # 根据content删除，删除所有相同的 content
    def del_content_all(self,chunk_list:List[str],auto_save=False):
        assert type(chunk_list) == list, "参数格式应该为：List[str]"
        # 构建id映射关系
        self.init_mapping_deep()
        del_ids = []
        for chunk in chunk_list:
            id = self.id_mapping_deep.get(chunk,"")
            if id:
                del_ids.extend(id)

        # 获取所有待删除的id信息，准备删除
        if del_ids:
            self.db.delete(del_ids)
            if auto_save:
                self.save()
        
        # 清空旧的id映射关系
        self.id_mapping_deep = {}
        print(f"已删除{len(del_ids)}条数据")

    # 清空数据
    def clear(self,auto_save=False):
        # 获取所有的id数据
        id_list = [id for id in self.db.index_to_docstore_id.values()]
        # 删除
        if id_list:
            self.db.delete(id_list)
        
        # 自动保存清空后的数据
        if auto_save:
            self.save()
        print("清空数据完成")

    # 显示db文件中所有的Document信息
    def show(self):
        return [self.id_search(id) for _,id in self.db.index_to_docstore_id.items()]

    

class FaissDB:

    def __init__(self) -> None:
        # 加载向量数据库
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_PATH,
            model_kwargs={'device': 'cuda'},
            encode_kwargs={'batch_size': 64, 'normalize_embeddings': True, 'show_progress_bar': False}
        )
        # 加载数据库配置信息
        with open(DB_MAPPING_PATH, 'r') as json_file:
            self.db_mapping = json.load(json_file)


        # 加载数据库字典
        self.db_group = self.init_db_group()


    # 初始化db_group 数据
    def init_db_group(self):
        dbs = {}
        for key in self.db_mapping.keys():
            dbs[key] = self.get_embedding(key)
        return dbs


    def update_config(self):
        # 更新映射配置文件
        with open(DB_MAPPING_PATH, 'w') as json_file:
            json.dump(self.db_mapping, json_file, indent=4)
            

    # 创建新的 db 数据库
    def create_db(self,db_id,db_name=""):
        db_id = str(db_id)
        if not db_name:
            db_name = str(db_id)
        
        # 判断数据库中是否存在该ID,如果存在请报错
        assert not self.db_mapping.get(db_id,False), "数据库创建失败，该ID已经存在，请重新输入新的ID"

        # 创建新的空数据库
        db = FAISS.from_documents([Document(page_content="",metadata={})],self.embeddings)
        # 清空数据
        self.clear(db)
        # 保存到对应的目录下
        db.save_local(os.path.join(DB_ROOT_PATH,db_name))

        # 添加到映射中
        self.db_mapping[db_id] = db_name

        # 添加到db_group中
        self.db_group[db_id] = db

        # 更新映射配置文件
        self.update_config()
        

    # 清空数据
    def clear(self,db,auto_save=False):
        # 获取所有的id数据
        id_list = [id for id in db.index_to_docstore_id.values()]
        # 删除
        if id_list:
            db.delete(id_list)
            if auto_save:
                self.save()


    # 删除数据库 
    def del_db(self,db_id):
        db_id = str(db_id)
        # 获取id对应的文件夹名称
        db_name = self.db_mapping.pop(db_id,None)
        if db_name:
            remove_dir = os.path.join(DB_ROOT_PATH,db_name)
            shutil.rmtree(remove_dir) # 删除文件夹及下面的所有内容
            # 更新配置文件
            self.update_config()
            # 删除db_group
            self.db_group.pop(db_id)


    # 获取对应的 原始db 对象
    def get_db(self,db_id):
        db_id = str(db_id)
        db_name = self.db_mapping.get(db_id,"")
        if db_name:
            db_path = os.path.join(DB_ROOT_PATH,db_name)
            db = FAISS.load_local(db_path, self.embeddings)
            return db


    # 获取对应的 可进行增删改的 embedding 对象
    def get_embedding(self,db_id):
        db_id = str(db_id)
        db_name = self.db_mapping.get(db_id,"")
        if db_name:
            db_path = os.path.join(DB_ROOT_PATH,db_name)
            db = FAISS.load_local(db_path, self.embeddings)
            return EmbeddingDB(db=db,save_path=db_path,embeddings=self.embeddings)


    # 获取所有的 ID 与 name 的映射
    def show_db(self):
        return self.db_mapping


    # 修改 映射关系 和 数据库加载
    def update_db(self,db_id,db_name):
        db_id = str(db_id)
        if self.db_mapping.get(db_id):
            self.db_mapping[db_id] = db_name
            self.update_config()
            # 重新加载一下 db_group
            self.db_group[db_id] = self.get_embedding(db_id)


    # 对数据库文件夹和映射名称进行重命名
    def rename_db(self,db_id,rename):
        db_id = str(db_id)
        db_name =  self.db_mapping.get(db_id,"")
        if db_name:
            # 修改文件夹名称
            old_name = os.path.join(DB_ROOT_PATH,db_name)
            new_name = os.path.join(DB_ROOT_PATH,rename)
            os.rename(old_name, new_name)
            self.db_mapping[db_id] = rename
            self.update_config()



if __name__ == "__main__":
    # 创建一个新的db数据
    db = FaissDB()


# %%
