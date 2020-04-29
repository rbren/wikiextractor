import os
from flask import Flask, request, jsonify, send_from_directory
import json
import numpy as np

from ..vectors import get_vectors

BROWSER_DIR = os.path.dirname(__file__) + "/web/dist/browser/"
app = Flask(__name__, static_folder=BROWSER_DIR, static_url_path="/")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/vectors')
def reload_model():
    category = request.args.get('category')
    print(category)
    vecs = get_vectors(category)
    return jsonify(vecs)

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
