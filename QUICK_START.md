# Quick Start Guide - Camera-Aware Lazy Eye System

## What's New

Your lazy eye detection system now understands:
- ✓ **Camera position** (top of laptop display assumed)
- ✓ **Where user is looking** (at screen vs camera)
- ✓ **Eye alignment** (strabismus/crossing detection)
- ✓ **Eye strain** detection
- ✓ **Confidence adjustments** based on gaze context

## Setup (< 2 minutes)

### 1. Install dependency (if needed)
The gaze analysis module uses only standard Python (numpy) - no new dependencies!

### 2. Run Flask server
```bash
python flask_onnx_server.py
```

### 3. Open browser
```
http://localhost:5000
```

## Using the System

### Basic Usage
1. **Click "Start"** - Camera opens
2. **Check "Show eye iris metrics"** - Enables gaze detection
3. **Look at screen** - Position face centered, looking at screen
4. **View results**:
   - Prediction label (lazy_eye / normal_eye)
   - Eye iris metrics (left/right iris position, gaze ratio)
   - **NEW:** Gaze Analysis panel (blue box below metrics)

### Reading the Gaze Analysis Panel

```
📸 Gaze Direction: down_at_screen          ← User looking down at screen
✓ Looking at screen: YES (visibility: 95%) ← Good engagement
✗ Looking at camera: NO                    ← Not distracted
👁️  Eye openness: normal                   ← Eyes fully open
🎯 Horizontal alignment: centered           ← Eyes aligned
💪 Accommodation: normal                   ← No eye strain
💬 Notes: ✓ Eyes in normal state           ← All good!
📊 Confidence: 85%                         ← High confidence
```

## Common Scenarios

### Scenario 1: Normal Eye (Expected Output)
```
Gaze Direction: down_at_screen
✓ Looking at screen: YES (visibility: 95%)
✗ Looking at camera: NO
👁️  Eye openness: normal
🎯 Horizontal alignment: centered
💪 Accommodation: normal
Label: normal_eye ✓
```

### Scenario 2: Lazy Eye (Eye Misalignment)
```
Gaze Direction: down_at_screen
✓ Looking at screen: YES (visibility: 80%)
👁️  Eye openness: normal
🎯 Horizontal alignment: asymmetric_strabismus ⚠️
💬 Notes: ⚠️ Eye misalignment detected (strabismus)
🔍 Diagnostics:
  • Significant vertical eye misalignment
  • Consistent with lazy eye diagnosis
Label: lazy_eye ✓
```

### Scenario 3: False Positive (Looking at Camera)
```
Gaze Direction: up_at_camera
✗ Looking at screen: NO
✓ Looking at camera: YES
Label might be refined from lazy_eye → uncertain_lazy_eye
⚠️ Model prediction was refined based on gaze analysis
```

## Key Metrics Explained

### Gaze Direction
- `down_at_screen` - Eyes looking at screen (ideal for diagnosis)
- `straight` - Eyes looking ahead
- `up_at_camera` - Eyes looking up at camera (may affect results)

### Screen Visibility
- **95-100%** - Perfect view of screen
- **80-95%** - Good view
- **60-80%** - Moderate view
- **< 60%** - Poor viewing angle

### Horizontal Alignment
- `centered` - Eyes aligned properly
- `left_deviated` / `right_deviated` - Slight deviation
- `both_inward_esotropia` - Eyes crossing inward (sign of lazy eye)
- `both_outward_exotropia` - Eyes drifting outward
- `asymmetric_strabismus` - Eyes not aligned with each other

### Eye Openness
- `normal` - Eyes wide open (best for diagnosis)
- `partially_closed` - Squinting (may indicate strain)
- `closed/blinking` - Can't analyze during blink

### Accommodation State
- `normal` - Relaxed viewing
- `mild_strain` - Possible fatigue
- `strain` - Eye fatigue/discomfort

## Tips for Best Results

### Positioning
- **Distance:** 30-60 cm from camera (typical desk distance)
- **Lighting:** Good even lighting, avoid harsh shadows on face
- **Angle:** Face camera directly, not tilted
- **Background:** Plain background works best

### Testing
1. **Keep eyes on screen** - Don't look up or away
2. **Interval:** 600-1000ms works well for stable results
3. **Duration:** 20-30 predictions per test (session voting)
4. **Consistency:** Repeat test 3-5 times for validation

### What to Watch For
- ⚠️ **Blinking** - Wait for full cycle, avoid during blinks
- ⚠️ **Looking up** - System warns you if looking at camera
- ⚠️ **Fatigue** - Eye strain reduces accuracy
- ⚠️ **Partial closure** - Squinting detected and noted

## Understanding Confidence Adjustments

The system **automatically adjusts confidence** based on:

| Condition | Adjustment | Reason |
|-----------|-----------|--------|
| Vertical eye misalignment | +10% | Supports lazy eye diagnosis |
| User looking at camera | -15% | Possible false positive |
| Eyes closing/blinking | -20% | Unreliable measurement |
| Partial eye closure | -10% | Eye strain present |
| Accommodation strain | -5% | Fatigue affects diagnosis |

## Troubleshooting

### No gaze analysis panel appears
- [ ] Is "Show eye iris metrics" **checked**?
- [ ] Can the camera see your eyes clearly?
- [ ] Is lighting adequate?

### "Looking at screen: NO" but you ARE looking at screen
- Check your camera position (might be below screen)
- Try tilting screen toward you slightly
- Improve lighting on face

### Low confidence or "uncertain" labels
- Ensure eyes are **fully open** (no squinting)
- Keep good **lighting**
- Maintain proper **distance** from camera
- Test multiple times

### High blink rate detected
- This is normal! System notes it automatically
- Just keep running - will get stable results

## Data Saved

Predictions are automatically saved to:
```
received_samples/inference_results.json
```

Each record includes:
- Prediction (label, confidence)
- Iris metrics (centers, EAR, gaze ratios)
- Gaze analysis (direction, alignment, notes)
- Timestamp

### Export to CSV
```bash
python extract_iris_metrics.py --json received_samples/inference_results.json
```

Creates `iris_metrics.csv` with all metrics for analysis.

## Contact & Support

For detailed technical documentation, see:
- `GAZE_ANALYSIS_README.md` - Full technical details
- `iris_metrics_guide.md` - Iris metrics documentation
- Python module: `gaze_analysis.py` - Source code

---

**That's it!** You're ready to use the gaze-aware lazy eye detection system. 🎉
