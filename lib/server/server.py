import os
from flask import Flask, request, jsonify, send_from_directory
import json
import numpy as np

from ..vectors import get_vectors
from ..extract import db

BROWSER_DIR = os.path.dirname(__file__) + "/../../web/src"
app = Flask(__name__, static_folder=BROWSER_DIR, static_url_path="/")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

categories = db.get_categories()

@app.route('/api/categories')
def get_categories():
    return jsonify(categories)

@app.route('/api/articles')
def get_articles():
    category = request.args.get('category')
    print(category)
    docs = db.get_documents_for_category(category)
    vecs, idfs, tokens = get_vectors([doc['id'] for doc in docs])
    for i in range(len(docs)):
        docs[i]['vector'] = vecs[i]
    return jsonify({'articles': docs, 'tokens': tokens, 'weights': idfs})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file("index.html")

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

app.json_encoder = NpEncoder

if __name__ == "__main__":
    app.run(port=3003, host='0.0.0.0')
