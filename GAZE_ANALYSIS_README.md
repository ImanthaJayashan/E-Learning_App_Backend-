# Gaze-Aware Lazy Eye Detection System

## New Features

This updated system now includes **camera-position aware gaze analysis** to improve lazy eye detection accuracy. It specifically accounts for **top-mounted laptop cameras** (the most common position).

### Key Improvements

#### 1. **Camera Position Awareness**
- Assumes camera mounted at **top of display** (standard laptop position)
- User's normal gaze at screen = looking **downward** from camera perspective
- Adjusts eye condition interpretation based on gaze direction

#### 2. **Screen vs Camera Distinction**
The system now detects whether the user is:
- **Looking at screen** (eyes directed downward) ✓ Normal usage
- **Looking at camera/up** (eyes directed upward) ← Possible false positive
- **Looking straight** (neutral gaze)
- **Screen visibility** estimation (0-100% what user can see)

#### 3. **Advanced Eye Condition Analysis**

**Horizontal Alignment (Strabismus Detection):**
- `centered` - Eyes aligned, iris centered in eye
- `left_deviated` - Eyes drifting left (may indicate esotropia)
- `right_deviated` - Eyes drifting right
- `both_inward_esotropia` - Both eyes turning inward (crossing)
- `both_outward_exotropia` - Both eyes turning outward
- `asymmetric_strabismus` - Eyes misaligned relative to each other

**Vertical Alignment:**
- Detects if one eye is higher/lower than the other
- Indicates possible vertical strabismus or lazy eye
- More than 0.15 units difference = significant misalignment

**Eye Openness:**
- `normal` - Eyes wide open (EAR > 0.25)
- `partially_closed` - Eyes squinting (EAR 0.15-0.25)
- `closed/blinking` - Eyes shut or blinking (EAR < 0.15)

**Accommodation State (Eye Strain):**
- `normal` - Relaxed eyes, normal viewing
- `mild_strain` - Some indicators of fatigue
- `strain` - Significant strain from squinting + convergence

#### 4. **Refined Lazy Eye Detection**

The system automatically:
1. Checks if eyes show strabismus (misalignment)
2. Verifies if user is actually looking at camera (might be false positive)
3. Detects eye openness issues (can't diagnose if blinking)
4. Identifies accommodation strain
5. **Refines the classification** if needed

### Response Data Structure

When you enable "Show eye iris metrics", the server now returns `gaze_analysis`:

```json
{
  "gaze_analysis": {
    "looking_at_screen": true,
    "looking_at_camera": false,
    "gaze_direction": "down_at_screen",
    "horizontal_alignment": "centered",
    "eye_openness": "normal",
    "accommodation_state": "normal",
    "gaze_confidence": 0.85,
    "screen_visibility_ratio": 0.95,
    "eye_condition_notes": "✓ Eyes in normal state",
    "diagnostics": ["Any relevant observations"],
    "model_vs_refined_agreement": true
  }
}
```

## Usage

### Web Interface
1. **Enable gaze analysis:**
   - Check "Show eye iris metrics" checkbox
   - This enables iris detection and sends metrics to server

2. **View gaze panel:**
   - New blue "Gaze Analysis" panel appears below metrics
   - Shows real-time camera position awareness data

3. **Interpretation:**
   - ✓ = Good / Normal
   - ✗ = Issues detected
   - ⚠️  = Warnings
   - 🔍 = Additional diagnostics

### Understanding the Output

**Good Setup (Correct):**
```
Gaze Direction: down_at_screen
✓ Looking at screen: YES (visibility: 95%)
✗ Looking at camera: NO
👁️  Eye openness: normal
🎯 Horizontal alignment: centered
💪 Accommodation: normal
```

**Poor Setup (User looking up at camera):**
```
Gaze Direction: up_at_camera
✗ Looking at screen: NO
✓ Looking at camera: YES
⚠️  Model prediction was refined based on gaze analysis
```

**Lazy Eye Detected:**
```
Gaze Direction: down_at_screen
👁️  Eye openness: normal
🎯 Horizontal alignment: asymmetric_strabismus
💬 Notes: ⚠️ Eye misalignment detected (strabismus)
🔍 Diagnostics:
  • Significant vertical eye misalignment (diff=0.18) - consistent with lazy eye
```

## API Integration

### Server Endpoint: `/predict`

**Request:**
- Form field: `image` (image file, required)
- Form field: `iris_metrics` (JSON string with gaze data, optional)
- Query param: `debug=1` (optional, returns base64 image)

**Response:**
```json
{
  "label": "lazy_eye",
  "raw_label": "lazy_eye",
  "confidence": 0.75,
  "is_uncertain": false,
  "uncertainty_reason": null,
  "gaze_analysis": { ... },
  "iris_metrics": { ... }
}
```

### Classification Confidence Adjustments

The system automatically adjusts confidence based on:
- **+10%** if vertical misalignment detected (supports lazy eye diagnosis)
- **-15%** if user looking at camera (might be false positive)
- **-20%** if eyes closing/blinking (unreliable measurement)
- **-10%** if partial eye closure (eye strain)
- **-5%** if accommodation strain detected

## Technical Details

### Gaze Metrics Collected

From MediaPipe Face Mesh and eye region analysis:

**Iris Centers:**
- `left.center.x`, `left.center.y` - Left iris position
- `right.center.x`, `right.center.y` - Right iris position

**Gaze Ratios (0=inner, 1=outer):**
- `left.gazeX` - Horizontal gaze position of left iris in eye
- `right.gazeX` - Horizontal gaze position of right iris in eye
- Values: 0.0 (toward nose), 0.5 (centered), 1.0 (outer corner)

**Eye Aspect Ratio (EAR):**
- `left.ear`, `right.ear` - Openness of each eye
- \> 0.25 = Normal open
- 0.15-0.25 = Partially closed
- < 0.15 = Blink/Closed

**Interpupillary Distance:**
- `ipd` - Distance between left and right iris centers in pixels

### Vertical Gaze Detection

Iris Y position in image tells us vertical gaze direction:
- Y < 0.35 (upper half) → Looking **UP** at camera
- Y 0.35-0.65 (middle) → Looking **STRAIGHT**
- Y > 0.65 (lower half) → Looking **DOWN** at screen

### Strabismus Detection

Compares gaze ratios between eyes:
- **Asymmetry > 0.15** between left and right = misalignment
- **Both < 0.4** = Both turning inward (esotropia)
- **Both > 0.6** = Both turning outward (exotropia)
- **One low, one high** = Asymmetric strabismus

## Troubleshooting

### "Gaze Analysis not showing"
- Ensure "Show eye iris metrics" is **checked**
- Eyes must be clearly visible in camera
- Lighting must be adequate for iris detection

### "Looking at screen: NO" when user is at screen
- Camera might be positioned lower than top of display
- User might be tilted back/away from screen
- Check lighting (shadows can confuse iris detection)

### High uncertainty warnings
- Blink detected → Wait for eyes to stay open
- Eye strain detected → Take a break
- Low confidence → Check lighting and face distance

## Integration Example

```python
# Server detects lazy eye with gaze analysis
from gaze_analysis import enhance_lazy_eye_detection

result = enhance_lazy_eye_detection(
    raw_label='lazy_eye',
    confidence=0.65,
    left_gaze_x=0.35,
    right_gaze_x=0.65,  # Asymmetry!
    left_ear=0.28,
    right_ear=0.25,
    ipd_px=95,
    left_iris_y=0.7,
    right_iris_y=0.55   # Vertical misalignment!
)

# Returns:
# refined_label: 'lazy_eye' (confirmed by gaze analysis)
# refined_confidence: 0.75 (+0.1 adjustment)
# diagnostics: [
#   'Significant vertical eye misalignment (diff=0.15) - consistent with lazy eye',
#   'Model prediction confirmed by gaze analysis'
# ]
```

## Future Enhancements

Potential improvements to explore:
1. **Individual eye focus detection** - Detect if one eye is not tracking properly
2. **Pupil dilation tracking** - Accommodation response analysis
3. **Blink rate analysis** - Eye strain and fatigue detection
4. **Tracking consistency** - Steady vs jerky eye movements
5. **Calibration mode** - User baseline calibration for personalized accuracy
6. **Multi-distance gaze** - Detect if user is looking at phone vs laptop screen
