import os
import io
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    img_bytes = file.read()

    image = Image.open(io.BytesIO(img_bytes)).convert('L')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    image.save(file_path)

    return jsonify({'message': 'Image saved successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
