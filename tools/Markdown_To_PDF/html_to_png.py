import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from utils.random_id import get_id
from utils.update_file import upload_file

"""
这个一般用于将 ECharts 图链接，转换为png图的链接，方便模型生成 pdf 文件
如果要使用这个方法，需要下载对应的浏览器驱动如：geckodriver
"""



# 将 html的url 转换为 png 的 url,方便生成pdf文件
def html_to_png(echarts_url):
    # Setup Firefox options
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Ensure GUI is off
    # TODO:指定geckodriver的路径
    geckodriver_path = '/usr/local/bin/geckodriver'  # 替换为您的geckodriver路径

    # Set up driver service
    service = Service(executable_path=geckodriver_path)
    # Set up driver
    driver = webdriver.Firefox(service=service, options=firefox_options)
    # Get web page
    driver.get(echarts_url)
    # Give time for all elements to load (adjust as necessary)
    driver.implicitly_wait(10)

    # 获取一个名称
    root_dir = os.path.split(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))[0]
    file_name = get_id() + ".png"
    file_path = os.path.join(root_dir,file_name)
    # Take screenshot of the page and save it
    driver.save_screenshot(file_path)
    # Clean up (close the browser)
    driver.quit()

    # 将保存到本地的png图像，转换为url
    file_url = upload_file(file_path)
    return file_url