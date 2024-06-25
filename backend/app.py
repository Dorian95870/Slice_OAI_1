from flask import Flask, request, jsonify
from flask_cors import CORS
from controllers.slice_controller import create_slice

app = Flask(__name__)
CORS(app)

app = Flask(__name__)
CORS(app)

@app.route('/api/slice', methods=['POST'])
def handle_create_slice():
    data = request.json
    response = create_slice(data)
    return jsonify(response), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)

