from flask import Flask, request, jsonify
from duckduckgo_search import DDGS

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def process_string():
    data = request.get_json()
    news = data.get('news', '')
    num = data.get('num',10)

    with DDGS() as ddgs:
       processed_data = [r for r in ddgs.news(news, region='cn-zh', max_results=num)]
    return jsonify(processed_data)

if __name__ == '__main__':
    app.run(debug=True, port=10001)
