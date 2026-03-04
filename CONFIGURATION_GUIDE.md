# Configuration Guide

## Customizable Parameters

You can adjust these settings in the code to fine-tune the system for your needs:

### Flask Server (`flask_onnx_server.py`)

#### Model Confidence Threshold
```python
LAZY_THRESHOLD = 0.9
```
- **Current:** 0.9 (90% confidence required to call lazy_eye)
- **Lower to:** 0.7 if getting too many false negatives (missing lazy eye cases)
- **Raise to:** 0.95 if getting false positives (diagnosing normal as lazy)
- **Range:** 0.5 - 0.99

#### Temporal Smoothing Window
```python
SMOOTH_WINDOW = 5
```
- **Current:** 5 predictions averaged for smoothing
- **Increase to:** 8-10 for more stable results (higher latency)
- **Decrease to:** 2-3 for faster response (noisier results)
- **Typical range:** 3-8

### Gaze Analyzer (`gaze_analysis.py`)

#### Camera Position
```python
analyzer = GazeAnalyzer(camera_position='top', screen_height_px=1080, screen_width_px=1920)
```
- `camera_position`: 'top', 'center', or 'bottom'
  - Set based on where camera is mounted on your device
  - Affects gaze direction interpretation
- `screen_height_px`: Your display height (for reference)
- `screen_width_px`: Your display width (for reference)

#### Eye Openness Thresholds
```python
def _classify_eye_openness(self, avg_ear: float) -> Tuple[str, float]:
    if avg_ear < 0.15:
        return 'closed/blinking', 0.9
    elif avg_ear < 0.25:
        return 'partially_closed', 0.85
    else:
        return 'normal', 0.95
```
- **EAR < 0.15:** Blinking/closed
- **EAR 0.15-0.25:** Partially closed
- **EAR > 0.25:** Normal open

Adjust these values based on your camera and lighting:
- Bright lighting: Use 0.20 instead of 0.25
- Poor lighting: Use 0.30 instead of 0.25

#### Gaze Ratio Asymmetry Threshold
```python
if asymmetry > 0.15:  # Significant difference between eyes
```
- **Current:** 0.15 (15% difference)
- **Lower to:** 0.10 to catch subtle strabismus
- **Raise to:** 0.20 for only obvious cases
- **What it detects:** Eyes turning in different directions (esotropia, exotropia)

#### Vertical Iris Position Thresholds
```python
if avg_iris_y < 0.35:
    direction = 'up_at_camera'
elif avg_iris_y > 0.65:
    direction = 'down_at_screen'
else:
    direction = 'straight'
```
- **< 0.35:** User looking up at camera
- **0.35-0.65:** User looking straight ahead
- **> 0.65:** User looking down at screen

Adjust based on your monitor height relative to camera:
- Monitor very low: Use 0.50 for 'down_at_screen' threshold
- Monitor very high: Use 0.75 for 'down_at_screen' threshold

#### Vertical Iris Misalignment Threshold
```python
if iris_y_diff > 0.15 and raw_label == 'lazy_eye':
```
- **Current:** 0.15 (15% difference)
- **Lower to:** 0.10 for sensitive detection
- **Raise to:** 0.20 for robust detection
- **What it detects:** One eye higher/lower than other (vertical strabismus)

#### Confidence Adjustment Factors
```python
confidence_adjustment = -0.15  # Looking at camera
confidence_adjustment = +0.1   # Vertical misalignment
confidence_adjustment = -0.2   # Eyes blinking
confidence_adjustment = -0.1   # Eyes partially closed
confidence_adjustment = -0.05  # Eye strain
```
- **Positive:** Increases confidence (supports the prediction)
- **Negative:** Decreases confidence (makes prediction uncertain)
- Adjust based on your accuracy needs

#### Screen Visibility Calculation
```python
if avg_iris_y > 0.75:
    return 0.95  # Excellent view
elif avg_iris_y > 0.65:
    return 0.8   # Good view
elif avg_iris_y > 0.55:
    return 0.6   # Moderate view
else:
    return 0.4   # Poor view
```
- Adjust iris_y thresholds based on your monitor position
- These are normalized values (0.0 = top of eye, 1.0 = bottom of eye)

### Frontend (`static/app.js`)

#### Prediction Smoothing
```python
const SMOOTH_WINDOW = 5;              # Predictions to average
const CONSISTENT_REQUIRED = 3;        # Consistent frames needed
const MIN_CONFIDENCE = 0.55;          # Minimum averaged confidence
const MIN_SEND_INTERVAL_MS = 200;     # Throttle frequency
```

**Tune for stability vs responsiveness:**
- **More stable:** CONSISTENT_REQUIRED=5, SMOOTH_WINDOW=8
- **More responsive:** CONSISTENT_REQUIRED=2, SMOOTH_WINDOW=3

**Confidence threshold:**
- **More strict:** MIN_CONFIDENCE=0.70 (avoid uncertain results)
- **More lenient:** MIN_CONFIDENCE=0.40 (catch more cases)

#### Face Cropping
```javascript
const cropFace = document.getElementById('cropFace') ? ... : true;
```
- If checked: Only sends cropped face region to server
- Saves bandwidth and focuses model on relevant area
- **Keep checked** for best performance

## Scenario-Based Configuration

### Scenario 1: Maximum Accuracy (Medical Diagnosis)
```python
LAZY_THRESHOLD = 0.95              # Very high confidence
SMOOTH_WINDOW = 10                 # Many frames averaged
'gaze_ratio_asymmetry' = 0.10      # Catch subtle misalignment
'vertical_iris_diff' = 0.10        # Strict vertical alignment check
MIN_CONFIDENCE = 0.70              # High confidence required
```

### Scenario 2: High Sensitivity (Screen Time Monitoring)
```python
LAZY_THRESHOLD = 0.70              # Lower threshold
SMOOTH_WINDOW = 3                  # Faster response
'gaze_ratio_asymmetry' = 0.20      # Only obvious misalignment
'vertical_iris_diff' = 0.20        # Allow more variation
MIN_CONFIDENCE = 0.50              # Less strict
```

### Scenario 3: Balanced (General Use)
```python
LAZY_THRESHOLD = 0.85              # Moderate threshold
SMOOTH_WINDOW = 5                  # Good balance
'gaze_ratio_asymmetry' = 0.15      # Standard asymmetry check
'vertical_iris_diff' = 0.15        # Standard vertical check
MIN_CONFIDENCE = 0.55              # Moderate confidence
```

### Scenario 4: Low-Light Environment
```python
# In _classify_eye_openness()
if avg_ear < 0.10:                 # Lower EAR threshold
    return 'closed/blinking'
elif avg_ear < 0.20:               # Lower partial-closed threshold
    return 'partially_closed'
else:
    return 'normal'

# Eyes more squinted in low light
confidence_adjustment = -0.15      # More cautious
```

### Scenario 5: Mobile Device (Higher Camera Position)
```python
analyzer = GazeAnalyzer(
    camera_position='center',      # Camera in middle of screen
    screen_height_px=667,          # iPhone size
    screen_width_px=375
)

# Adjust gaze thresholds
'up_at_camera_threshold' = 0.45    # Higher threshold for "up"
'down_at_screen_threshold' = 0.55  # Lower threshold for "down"
```

## Testing Configuration Changes

### 1. Create a test script
```python
from gaze_analysis import enhance_lazy_eye_detection

# Test case: Lazy eye with misalignment
result = enhance_lazy_eye_detection(
    raw_label='lazy_eye',
    confidence=0.75,
    left_gaze_x=0.35,      # Left eye turned inward
    right_gaze_x=0.65,     # Right eye centered
    left_ear=0.28,
    right_ear=0.26,
    ipd_px=95,
    left_iris_y=0.70,
    right_iris_y=0.55      # Vertical misalignment
)

print(result['refined_label'])
print(result['refined_confidence'])
print(result['diagnostics'])
```

### 2. Run multiple test cases
- Normal eyes with good alignment
- Lazy eye with clear misalignment
- Eyes looking at camera (false positive case)
- Eyes closing/blinking
- Eye strain conditions

### 3. Verify results match expectations
- Refine thresholds if results differ
- Re-test until satisfied
- Document your chosen values

## Database of Calibrated Values

Save your configurations for different use cases:

```python
# config_medical.py
LAZY_THRESHOLD = 0.95
SMOOTH_WINDOW = 10
ASYMMETRY_THRESHOLD = 0.10
VERTICAL_DIFF_THRESHOLD = 0.10

# config_realtime.py
LAZY_THRESHOLD = 0.70
SMOOTH_WINDOW = 3
ASYMMETRY_THRESHOLD = 0.20
VERTICAL_DIFF_THRESHOLD = 0.20

# config_mobile.py
LAZY_THRESHOLD = 0.80
SMOOTH_WINDOW = 5
CAMERA_POSITION = 'center'
...
```

Then load based on use case:
```python
from config_medical import LAZY_THRESHOLD, SMOOTH_WINDOW
# OR
from config_realtime import LAZY_THRESHOLD, SMOOTH_WINDOW
```

## Common Tuning Issues

### Problem: Too many false positives (calling normal as lazy)
**Solution:**
- Increase `LAZY_THRESHOLD` to 0.92-0.95
- Increase `gaze_ratio_asymmetry` to 0.18-0.20
- Increase `vertical_iris_diff` to 0.18-0.20
- Increase `MIN_CONFIDENCE` to 0.65-0.70

### Problem: Missing lazy eye cases (false negatives)
**Solution:**
- Decrease `LAZY_THRESHOLD` to 0.75-0.80
- Decrease `gaze_ratio_asymmetry` to 0.10-0.12
- Decrease `vertical_iris_diff` to 0.10-0.12
- Decrease `MIN_CONFIDENCE` to 0.45-0.50

### Problem: Inconsistent results (varies frame to frame)
**Solution:**
- Increase `SMOOTH_WINDOW` to 8-10
- Increase `CONSISTENT_REQUIRED` to 4-5
- Improve lighting conditions
- Ensure camera is stable

### Problem: System too slow to respond
**Solution:**
- Decrease `SMOOTH_WINDOW` to 2-3
- Decrease `CONSISTENT_REQUIRED` to 1-2
- Increase `MIN_SEND_INTERVAL_MS` to 300-400
- Note: Trade-off with accuracy

## Monitoring Performance

After configuration, monitor these metrics:

```python
# From received_samples/inference_results.json
# Calculate:
- Prediction accuracy (compare to manual diagnosis)
- False positive rate (normal classified as lazy)
- False negative rate (lazy not detected)
- Average confidence score
- Consistency (same person, repeated tests)
- Response time (milliseconds per prediction)
```

## Resetting to Defaults

If configuration breaks the system, reset to defaults:

```python
# gaze_analysis.py
analyzer = GazeAnalyzer(camera_position='top')

# flask_onnx_server.py  
LAZY_THRESHOLD = 0.9
SMOOTH_WINDOW = 5

# app.js
const SMOOTH_WINDOW = 5
const CONSISTENT_REQUIRED = 3
const MIN_CONFIDENCE = 0.55
const MIN_SEND_INTERVAL_MS = 200
```

---

**Start with defaults, then tune based on your specific needs!** 📊
