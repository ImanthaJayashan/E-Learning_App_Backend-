from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import onnxruntime as ort
from PIL import Image
import numpy as np
import io
import torch
from pathlib import Path
import json
from datetime import datetime, timezone, timedelta
from collections import deque
from gaze_analysis import enhance_lazy_eye_detection

# Sri Lankan timezone (UTC+5:30)
SRI_LANKA_TZ = timezone(timedelta(hours=5, minutes=30))

def get_srilanka_time():
    """Get current time in Sri Lankan timezone"""
    return datetime.now(SRI_LANKA_TZ).isoformat()

app = Flask(__name__)
CORS(app)

# Minimum probability required to call a lazy_eye; below this we fall back to uncertain/normal.
LAZY_THRESHOLD = 0.9

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

# Rolling window for temporal smoothing of probabilities
SMOOTH_WINDOW = 5
PROB_HISTORY = deque(maxlen=SMOOTH_WINDOW)

# Keep the most recent inference in memory for quick dashboard access
LAST_RESULT = None


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


def extract_iris_xy(iris_metrics):
    """Extract flattened iris centers if provided by client."""
    try:
        left_c = iris_metrics.get('left', {}).get('center', {}) if iris_metrics else {}
        right_c = iris_metrics.get('right', {}).get('center', {}) if iris_metrics else {}
        left_gaze = iris_metrics.get('left', {}).get('gazeX') if iris_metrics else None
        right_gaze = iris_metrics.get('right', {}).get('gazeX') if iris_metrics else None
        return {
            'left_iris_x': left_c.get('x'),
            'left_iris_y': left_c.get('y'),
            'right_iris_x': right_c.get('x'),
            'right_iris_y': right_c.get('y'),
            'ipd_px': iris_metrics.get('ipd'),
            'left_gaze_ratio': left_gaze,
            'right_gaze_ratio': right_gaze,
        }
    except Exception:
        return {}


def save_inference_result(prediction_label, confidence, raw_label, iris_metrics=None, lazy_confidence=None,
                          smooth_label=None, smooth_confidence=None, smooth_lazy_confidence=None, extra=None):
    """Save inference result with optional iris metrics to JSON."""
    try:
        results_file = Path('received_samples/inference_results.json')
        results_file.parent.mkdir(exist_ok=True)
        
        result = {
            'timestamp': get_srilanka_time(),
            'label': prediction_label,
            'raw_label': raw_label,
            'confidence': float(confidence),
            'lazy_eye_confidence': float(lazy_confidence) if lazy_confidence is not None else None,
            'smooth_label': smooth_label,
            'smooth_confidence': float(smooth_confidence) if smooth_confidence is not None else None,
            'smooth_lazy_eye_confidence': float(smooth_lazy_confidence) if smooth_lazy_confidence is not None else None,
        }

        if extra and isinstance(extra, dict):
            result.update(extra)
        
        if iris_metrics:
            result['iris_metrics'] = iris_metrics
            result.update(extract_iris_xy(iris_metrics))
        
        # Load existing records or start new
        records = []
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        records = data
                    elif isinstance(data, dict) and 'records' in data:
                        records = data['records']
            except Exception:
                pass
        
        records.append(result)
        
        # Save back
        with open(results_file, 'w') as f:
            json.dump(records, f, indent=2)

        # Update in-memory cache for fast access
        global LAST_RESULT
        LAST_RESULT = result
    except Exception as e:
        print(f"Failed to save inference result: {e}")


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
    raw_label = CLASSES[idx] if idx < len(CLASSES) else str(idx)
    confidence = float(probs[idx])
    # lazy-eye specific probability (if class exists)
    lazy_idx = None
    try:
        lazy_idx = CLASSES.index('lazy_eye')
    except Exception:
        lazy_idx = None
    lazy_confidence = float(probs[lazy_idx]) if lazy_idx is not None and lazy_idx < len(probs) else None

    # Temporal smoothing (simple average over last N probability vectors)
    PROB_HISTORY.append(probs)
    if len(PROB_HISTORY) > 0:
        avg_probs = np.mean(np.stack(PROB_HISTORY, axis=0), axis=0)
        smooth_idx = int(np.argmax(avg_probs))
        smooth_label = CLASSES[smooth_idx] if smooth_idx < len(CLASSES) else str(smooth_idx)
        smooth_confidence = float(avg_probs[smooth_idx])
        smooth_lazy_confidence = float(avg_probs[lazy_idx]) if lazy_idx is not None and lazy_idx < len(avg_probs) else None
    else:
        avg_probs = probs
        smooth_label = raw_label
        smooth_confidence = confidence
        smooth_lazy_confidence = lazy_confidence

    # Keep the lazy_eye label but surface uncertainty instead of relabeling as normal.
    label = raw_label
    is_uncertain = False
    uncertainty_reason = None
    if raw_label == 'lazy_eye' and confidence < LAZY_THRESHOLD:
        is_uncertain = True
        uncertainty_reason = f"lazy_eye confidence {confidence:.3f} below threshold {LAZY_THRESHOLD}"

    # Try to extract iris metrics if provided by client
    iris_metrics = None
    gaze_analysis = None
    try:
        # Client may send iris metrics as JSON in request
        metrics_str = request.form.get('iris_metrics')
        if metrics_str:
            iris_metrics = json.loads(metrics_str)
    except Exception:
        pass
    
    # Enhanced lazy eye detection using gaze analysis if we have iris metrics
    if iris_metrics and raw_label == 'lazy_eye':
        try:
            left_gaze_x = iris_metrics.get('left', {}).get('gazeX')
            right_gaze_x = iris_metrics.get('right', {}).get('gazeX')
            left_ear = iris_metrics.get('left', {}).get('ear')
            right_ear = iris_metrics.get('right', {}).get('ear')
            ipd_px = iris_metrics.get('ipd')
            
            # Try to get vertical iris positions if available
            left_iris_y = None
            right_iris_y = None
            if 'left' in iris_metrics and 'center' in iris_metrics['left']:
                left_iris_y = iris_metrics['left'].get('center', {}).get('y')
            if 'right' in iris_metrics and 'center' in iris_metrics['right']:
                right_iris_y = iris_metrics['right'].get('center', {}).get('y')
            
            if all([left_gaze_x is not None, right_gaze_x is not None, left_ear is not None, right_ear is not None, ipd_px is not None]):
                gaze_analysis = enhance_lazy_eye_detection(
                    raw_label=raw_label,
                    confidence=confidence,
                    left_gaze_x=left_gaze_x,
                    right_gaze_x=right_gaze_x,
                    left_ear=left_ear,
                    right_ear=right_ear,
                    ipd_px=ipd_px,
                    left_iris_y=left_iris_y,
                    right_iris_y=right_iris_y,
                    image_height=224
                )
                if gaze_analysis['refined_label'] != raw_label:
                    label = gaze_analysis['refined_label']
                    confidence = gaze_analysis['refined_confidence']
                    is_uncertain = True
                    uncertainty_reason = f"Gaze analysis: {gaze_analysis['analysis']['eye_condition_notes']}"
        except Exception as e:
            pass

    response = {
        'label': label,
        'raw_label': raw_label,
        'confidence': confidence,
        'lazy_eye_confidence': lazy_confidence,
        'threshold': LAZY_THRESHOLD,
        'all_probs': probs.tolist(),
        'smooth_label': smooth_label,
        'smooth_confidence': smooth_confidence,
        'smooth_lazy_eye_confidence': smooth_lazy_confidence,
        'smooth_window': SMOOTH_WINDOW,
        'smooth_count': len(PROB_HISTORY),
        'is_uncertain': is_uncertain,
        'uncertainty_reason': uncertainty_reason,
    }
    
    # Add gaze analysis to response
    if gaze_analysis:
        response['gaze_analysis'] = {
            'looking_at_screen': gaze_analysis['analysis']['looking_at_screen'],
            'looking_at_camera': gaze_analysis['analysis']['looking_at_camera'],
            'gaze_direction': gaze_analysis['analysis']['gaze_direction'],
            'horizontal_alignment': gaze_analysis['analysis']['horizontal_alignment'],
            'eye_openness': gaze_analysis['analysis']['eye_openness'],
            'accommodation_state': gaze_analysis['analysis']['accommodation_state'],
            'gaze_confidence': gaze_analysis['analysis']['confidence'],
            'screen_visibility_ratio': gaze_analysis['analysis']['screen_visibility_ratio'],
            'eye_condition_notes': gaze_analysis['analysis']['eye_condition_notes'],
            'diagnostics': gaze_analysis['diagnostics'],
            'model_vs_refined_agreement': gaze_analysis['model_vs_refined_agreement'],
        }
    
    # Add iris metrics to response
    if iris_metrics:
        response['iris_metrics'] = iris_metrics
        response.update(extract_iris_xy(iris_metrics))
    
    # Save prediction result with metrics
    response['timestamp'] = get_srilanka_time()

    save_inference_result(
        label,
        confidence,
        raw_label,
        iris_metrics,
        lazy_confidence,
        smooth_label=smooth_label,
        smooth_confidence=smooth_confidence,
        smooth_lazy_confidence=smooth_lazy_confidence,
        extra={
            'is_uncertain': is_uncertain,
            'uncertainty_reason': uncertainty_reason,
            'gaze_analysis': response.get('gaze_analysis'),
        }
    )

    # Update in-memory cache for fast access
    global LAST_RESULT
    LAST_RESULT = response

    # optionally return the raw uploaded image as base64 when debug=1 is passed
    try:
        debug_flag = request.args.get('debug', '0')
        if debug_flag == '1':
            import base64
            response['debug_image_b64'] = base64.b64encode(img_bytes).decode('ascii')
    except Exception:
        pass

    return jsonify(response)


@app.route('/latest', methods=['GET'])
def latest():
    # Return cached latest if available
    if LAST_RESULT:
        return jsonify(LAST_RESULT)

    # Fallback to file storage
    try:
        results_file = Path('received_samples/inference_results.json')
        if results_file.exists():
            with open(results_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return jsonify(data[-1])
                if isinstance(data, dict) and 'records' in data and data['records']:
                    return jsonify(data['records'][-1])
    except Exception:
        pass

    return jsonify({'message': 'no results yet'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
