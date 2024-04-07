#%%
import requests

def upload_file(file_path):
    """上传文件
    参数：
    - file_path: 要上传的文件的路径。
    """
    url = "http://127.0.0.1:5000/upload"
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files)
    return response.text

if __name__ == "__main__":
      # Flask服务的URL，确保和你的服务地址匹配
    file_path = r"D:\git_project\LocalAgent-Tutorial\qanything_arch.png"  # 替换为你要上传的文件的实际路径

    print("Uploading file...")
    result = upload_file(file_path)
    print("Server response:", result)

# %%
