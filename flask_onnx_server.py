from flask import Flask, request, jsonify, render_template
import onnxruntime as ort
from PIL import Image
import numpy as np
import io
import torch

app = Flask(__name__)

# Load classes from checkpoint if available
try:
    ckpt = torch.load('checkpoints/best_checkpoint.pth', map_location='cpu')
    CLASSES = ckpt.get('classes', ['lazy_eye', 'normal_eye'])
except Exception:
    CLASSES = ['lazy_eye', 'normal_eye']

# Load ONNX model
ORT_SESSION = ort.InferenceSession('model.onnx')
INPUT_NAME = ORT_SESSION.get_inputs()[0].name
OUTPUT_NAME = ORT_SESSION.get_outputs()[0].name


def preprocess_image_bytes(image_bytes, img_size=224):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((img_size, img_size))
    arr = np.array(img).astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    arr = (arr - mean) / std
    # HWC -> CHW
    arr = arr.transpose(2, 0, 1)
    arr = np.expand_dims(arr, axis=0).astype(np.float32)
    return arr


def softmax(x):
    e = np.exp(x - np.max(x))
    return e / e.sum()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'no image uploaded (use form field `image` with multipart/form-data)'}), 400

    file = request.files['image']
    img_bytes = file.read()
    try:
        x = preprocess_image_bytes(img_bytes)
    except Exception as e:
        return jsonify({'error': f'failed to preprocess image: {e}'}), 400

    # Save a debug copy of the received image for inspection (rotate samples directory)
    try:
        from datetime import datetime
        samples_dir = Path('received_samples')
        samples_dir.mkdir(exist_ok=True)
        fname = samples_dir / f"recv_{datetime.utcnow().strftime('%Y%m%dT%H%M%S%f')}.jpg"
        with open(fname, 'wb') as f:
            f.write(img_bytes)
    except Exception:
        pass

    ort_inputs = {INPUT_NAME: x}
    ort_outs = ORT_SESSION.run([OUTPUT_NAME], ort_inputs)
    logits = ort_outs[0][0]
    probs = softmax(logits)
    idx = int(np.argmax(probs))
    label = CLASSES[idx] if idx < len(CLASSES) else str(idx)
    confidence = float(probs[idx])

    response = {'label': label, 'confidence': confidence, 'all_probs': probs.tolist()}

    # optionally return the raw uploaded image as base64 when debug=1 is passed
    try:
        debug_flag = request.args.get('debug', '0')
        if debug_flag == '1':
            import base64
            response['debug_image_b64'] = base64.b64encode(img_bytes).decode('ascii')
    except Exception:
        pass

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
