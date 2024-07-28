#%%
import requests

# 服务器地址
base_url = "http://127.0.0.1:8101"



# POST 请求示例
def create_item(item_data):
    response = requests.post(f"{base_url}/faiss/", json=item_data)
    return response

if __name__ == "__main__":

    # 调用 POST 请求
    # 添加请求
    # item = {
    #     "operator": "C",
    #     "file_db": 1001,
    #     # "file_names": ["“四个意识”“四个自信”“两个维护”是相辅相成的整体.pdf","《城镇污水处理厂污染物排放标准》（GB18918-2002）.pdf"],
    #     "file_names": ["“四个意识”“四个自信”“两个维护”是相辅相成的整体.pdf"],
    #     # "query": ""
    # }

    item = {
        "operator": "D",
        "file_db": 1001,
        "file_names": ["“四个意识”“四个自信”“两个维护”是相辅相成的整体.pdf"],
    }

    # item = {
    #     "operator": "R",
    #     "file_db": "1001",
    #     "query" : "—3—“十四五”环境影响评价与排污许可工作实施方案为贯彻落实“十四五”生态环境保护目标、任务，深入打好污染防治攻坚战，健全以环境影响评价（以下简称环评）制度为主体的源头预防体系，构建以排污许可制为核心的固定污染源监管制度体系，推动生态环境质量持续改善和经济高质量发展，制定本方案。"
    # }
    response = create_item(item)
    print(response.json()['result'])

# %%
