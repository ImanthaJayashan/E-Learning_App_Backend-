import io
import torch
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from torchvision import transforms

app = Flask(__name__)
CORS(app)

transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    img_bytes = request.files['image'].read()
    image = Image.open(io.BytesIO(img_bytes))

    processed_image = transform(image).unsqueeze(0)

    return jsonify({
        "message": "Image processed successfully",
        "tensor_shape": list(processed_image.shape)
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
