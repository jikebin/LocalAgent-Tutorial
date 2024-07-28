"""
实现将文档向量化的功能
"""
#%%
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from urllib.parse import unquote


class DocumentEmbedding:
    def __init__(self,pdf_name) -> None:
        self.base_dir = os.path.split(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))[0]
        self.document_dir = os.path.join(self.base_dir,"statics","zhaobiao")
        f_name,_ = os.path.splitext(unquote(pdf_name)) # 拆分文件名和后缀
        self.f_name = f_name
        self.SUFFIX = ".txt"
        self.document_path = os.path.join(self.document_dir,self.f_name + self.SUFFIX)  # 获取文件路径
        # 定义文档分割相关配置  
        self.text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size = 256,           # 分割长度
            chunk_overlap  = 100,       # 重合长度
            length_function = len,      # 长度判断方法
            add_start_index = True,     # 添加开始索引
        )
        # 加载向量模型
        self.model_name = os.path.join(self.base_dir,"statics","model","bce-embedding-base_v1")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={'device': 'cuda'},
            encode_kwargs={'batch_size': 64, 'normalize_embeddings': True, 'show_progress_bar': False}
        )
        self.db = self.doc_embedding()
        self.top = 20  # 返回搜索的top_n
        

    def doc_embedding(self):
        # 获取文档内容
        with open(self.document_path,"r",encoding="utf8") as f:
            raw_documents = f.read()

        # 分割文档
        texts = self.text_splitter.create_documents([raw_documents])

        #进行句子转换并再生成向量空间
        db = FAISS.from_documents(texts,self.embeddings)
        return db
    

    # 相似度搜索
    def similarity_search(self,query):
        embedding_vector = self.embeddings.embed_query(query)
        docs = self.db.similarity_search_by_vector(embedding_vector,k=self.top)
        return [d.page_content for d in docs]
    
    def similarity_search_test(self, query):
        # embedding_vector = self.embeddings.embed_query(query)
        docs = self.db.similarity_search_with_score(query, k=self.top)
        return docs


if __name__ == "__main__":
    doc = DocumentEmbedding("文档.pdf")
    docs = doc.similarity_search_test("搜索内容")
    res = []
    import pandas as pd
    for doc in docs:
        res.append([doc[0].page_content, doc[1]])
    res = pd.DataFrame(res, columns=['content','em'])
    res = res.sort_values(by='em')
    # s1 = set(content_list1)





        
