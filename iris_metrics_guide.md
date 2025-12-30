# Iris Center Deviation Metrics Guide

## Overview
This project now captures detailed iris metrics during eye classification. These metrics measure eye position, gaze direction, and eye openness.

## Key Metrics Collected

### Iris Center Coordinates (pixels)
- **`left_iris_cx`, `left_iris_cy`**: Center position of left iris relative to image
- **`right_iris_cx`, `right_iris_cy`**: Center position of right iris relative to image

### Iris Radius (pixels)
- **`left_iris_radius`**: Estimated radius of left iris
- **`right_iris_radius`**: Estimated radius of right iris

### Iris Center Deviation
Deviation is the distance of the iris center from the estimated eye center.
- **Formula**: `sqrt((iris_cx - eye_center_x)² + (iris_cy - eye_center_y)²)`
- **Interpretation**: 
  - Indicates how much the iris is offset from the eye region center
  - Higher values = more pronounced deviation
  - Used to detect lazy eye characteristics

### Gaze Ratio (0 to 1)
- **`left_gaze_ratio`, `right_gaze_ratio`**: Horizontal position of iris within eye
  - **0.0** = iris at inner corner (near nose)
  - **0.5** = iris centered in eye
  - **1.0** = iris at outer corner (temporal side)
- **Interpretation**: Indicates gaze direction relative to eye corners

### Eye Aspect Ratio (EAR)
- **`left_ear`, `right_ear`**: Ratio of eye height to eye width
  - Indicates eye openness
  - Values < ~0.20 typically indicate blink or closed eye
  - Helps filter out bad captures

### Interpupillary Distance (IPD)
- **`ipd_px`**: Distance between left and right iris centers (pixels)
- **Interpretation**: 
  - Natural IPD for adult ≈ 60-65mm
  - Relative size in image tells us about camera distance
  - Can help normalize measurements across different capture conditions

## How to Use

### Method 1: Web Application (Recommended)
1. Start Flask server:
   ```bash
   python flask_onnx_server.py
   ```
2. Open browser to `http://localhost:5000`
3. Check **"Show eye iris metrics"** checkbox
4. Click **"Start"** and allow camera access
5. Metrics will display in real-time on screen
6. When you stop, predictions and metrics are automatically saved to:
   ```
   received_samples/inference_results.json
   ```

### Method 2: Export to CSV
After collecting predictions via the web app:
```bash
python extract_iris_metrics.py --json received_samples/inference_results.json --output-csv iris_metrics.csv
```

This generates `iris_metrics.csv` with all metrics and summary statistics.

## Interpretation for Lazy Eye Detection

### Normal Eye Characteristics
- Iris centered in eye (gaze_ratio ≈ 0.4-0.6)
- EAR > 0.20 (eye open)
- Minimal iris deviation from eye center
- Steady IPD measurements

### Lazy Eye Characteristics
- Iris offset toward center/nose (gaze_ratio < 0.4 or > 0.6)
- Possible misalignment between the two eyes
- Variable IPD or asymmetry
- EAR indicates blink/squinting

## Advanced Analysis

### Detecting Asymmetry
```python
import pandas as pd
df = pd.read_csv('iris_metrics.csv')
df['asymmetry'] = abs(df['left_gaze_ratio'] - df['right_gaze_ratio'])
print(df[df['asymmetry'] > 0.1])  # Find high asymmetry cases
```

### Tracking Eye Behavior Over Time
```python
# If you have multiple captures in a session:
predictions_lazy = df[df['prediction'] == 'lazy_eye']
print(f"Average left iris deviation (lazy): {predictions_lazy['left_iris_deviation_px'].mean():.2f}px")
```

### Baseline Calibration
1. Capture 10-20 images of normal eyes under various lighting conditions
2. Record mean/std of metrics
3. Use as reference baseline for comparison

## Technical Details

### Landmark Indices (MediaPipe Face Mesh)
- Left iris landmarks: [468, 469, 470, 471, 472]
- Right iris landmarks: [473, 474, 475, 476, 477]
- Left eye corners: outer=33, inner=133
- Right eye corners: outer=362, inner=263

### Coordinate System
- Origin (0,0) is top-left of image
- X increases rightward
- Y increases downward
- All coordinates in pixels

## Troubleshooting

### Metrics Show Zero or Invalid Values
- Ensure face is clearly visible in frame
- Check lighting (avoid shadows on eyes)
- Keep face centered in frame
- Ensure EAR > 0.20 (eyes are open)

### Inconsistent Measurements
- Camera distance should be consistent (~50-75 cm)
- Face should remain at similar angle
- Lighting should be even across both eyes

### High False Positive Rate (Normal Eyes Marked as Lazy)
- Adjust the lazy_eye threshold in `flask_onnx_server.py`:
  ```python
  LAZY_THRESHOLD = 0.95  # Increase from 0.90 to be more conservative
  ```
- Collect more normal-eye training data similar to your capture conditions

## See Also
- [flask_onnx_server.py](flask_onnx_server.py) - Server that captures metrics
- [extract_iris_metrics.py](extract_iris_metrics.py) - CSV export tool
- [static/app.js](static/app.js) - Web app that computes and sends metrics
