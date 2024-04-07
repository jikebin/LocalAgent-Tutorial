#%%
import os
from flask import Flask, request, send_from_directory

app = Flask(__name__)
directory = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(directory, 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '没有文件上传'
    file = request.files['file']
    if file.filename == '':
        return '没有选择文件'
    if file:
        # 获取文件名称
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return f'http://127.0.0.1:5000/uploads/{filename}'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=5000, debug=True)

#%%