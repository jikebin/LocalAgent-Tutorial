"""
实现将文档向量化的功能
"""
#%%
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from document_obj import PdfDocument

class DocumentEmbedding:
    def __init__(self,pdf_path) -> None:
        self.pdf_path = pdf_path
        self.base_dir = os.path.dirname(os.path.abspath(__file__))


        # 定义文档分割相关配置  
        self.text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size = 256,           # 分割长度
            chunk_overlap  = 100,       # 重合长度
            length_function = len,      # 长度判断方法
            add_start_index = True,     # 添加开始索引
        )
        # 加载向量模型
        # self.model_name = os.path.join(self.base_dir,"bce-embedding-base_v1")
        self.model_name = r"D:\models\piccolo-large-zh"
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'batch_size': 64, 'normalize_embeddings': True}
        )
        self.db = self.doc_embedding()
        self.top = 20  # 返回搜索的top_n
        

    def doc_embedding(self):
        # 获取文档内容
        doc = PdfDocument(self.pdf_path)
        doc.analysis_pdf()
        raw_documents = doc.read_text()

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
    path = r"D:\学习笔记\19向量检索\大连爱渥特机器人科技有限公司八角管抓手项目环境影响报告表.pdf"
    doc = DocumentEmbedding(path)
    # content_list1 = doc.similarity_search("招标代理机构名称")
    docs = doc.similarity_search_test("加工工艺流程图 ")



# %%
