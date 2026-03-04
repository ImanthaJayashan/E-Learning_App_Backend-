Each branch README includes project overview, architecture details,
technologies used, and contribution-specific information.
# Eye Ball (Lazy vs Normal) Detection System

## 📋 Project Overview

This project is an AI-powered medical diagnosis system that detects lazy eye (amblyopia) versus normal eye conditions using deep learning and computer vision. The system provides a complete pipeline from model training to web-based inference, featuring:

- **Binary classification** of eye conditions (lazy eye vs normal eye)
- **Deep learning model** trained using PyTorch with MobileNetV2 architecture
- **Web interface** for easy image upload and real-time predictions
- **ONNX model deployment** for cross-platform compatibility
- **Iris metrics extraction** for detailed eye analysis

## 🏗️ Architecture Diagram

<img width="1171" height="571" alt="Untitled Diagram drawio (1)" src="https://github.com/user-attachments/assets/468168ff-3d0f-4216-9813-696dae9c87b5" />


### System Components:

- **Frontend**: Static HTML/CSS/JavaScript interface for user interaction
- **Backend**: Flask web server handling API requests and orchestration
- **AI Engine**: ONNX Runtime with MobileNetV2 for eye classification
- **Computer Vision**: OpenCV for image processing and iris analysis
- **Storage**: File-based storage for datasets, models, and results

## 🛠️ Technologies & Dependencies

### **Core Technologies**
- **Python 3.8+** - Primary programming language
- **PyTorch** - Deep learning framework for model training
- **ONNX Runtime** - Cross-platform model inference
- **Flask** - Web server and REST API framework
- **OpenCV** - Computer vision and image processing

### **Deep Learning & AI**
- `torch` - PyTorch deep learning library
- `torchvision` - Pre-trained models and image transformations
- `onnx` - Open Neural Network Exchange format
- `onnxruntime` - ONNX model inference engine

### **Computer Vision**
- `opencv-python` - Image processing and analysis
- `Pillow (PIL)` - Image manipulation
- `numpy` - Numerical computing

### **Web Framework**
- `Flask` - Lightweight web application framework
- `flask-cors` - Cross-Origin Resource Sharing support

### **Data Processing**
- `pandas` - Data manipulation and analysis
- `scikit-learn` - Machine learning utilities

### **Model Architecture**
- **MobileNetV2** - Lightweight convolutional neural network
- **Binary Classifier** - Lazy eye vs Normal eye detection

## 📁 Dataset Structure

This repository contains a minimal training and inference pipeline to train a binary classifier that distinguishes `lazy_eye` vs `normal_eye` using images organized with the following structure:

```
eye_data/
    train/
        lazy_eye/
        normal_eye/
    test/
        lazy_eye/
        normal_eye/
```

## 🚀 Quick Start Guide

### Installation

Files added:
- `train.py` — training script using a MobileNetV2 backbone (PyTorch + torchvision)
- `inference.py` — single-image prediction using a saved checkpoint
- `requirements.txt` — minimal required packages

Quick start (PowerShell):

```powershell
# create venv
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Run training (adjust args as needed)
python train.py --data-dir .\eye_data --epochs 10 --batch-size 16 --output-dir .\checkpoints

# Run inference on a single image
python inference.py .\eye_data\test\lazy_eye\some_image.jpg --ckpt .\checkpoints\best_checkpoint.pth
```

### Running the Web Interface

```powershell
# Start the Flask server
python flask_onnx_server.py

# Open browser and navigate to
# http://localhost:5000
```

### Model Export

```powershell
# Export PyTorch model to ONNX
python export_onnx.py

# Convert ONNX to SavedModel/H5 (optional)
python onnx_to_savedmodel_and_h5.py
```

### Iris Metrics Extraction

```powershell
# Extract detailed iris measurements
python extract_iris_metrics.py
```

## 📊 Project Files Overview

| File | Description |
|------|-------------|
| `train.py` | Main training script with MobileNetV2 backbone |
| `inference.py` | Single-image prediction using saved checkpoint |
| `flask_onnx_server.py` | Flask web server for ONNX model inference |
| `export_onnx.py` | Convert PyTorch model to ONNX format |
| `onnx_to_savedmodel_and_h5.py` | Convert ONNX to TensorFlow formats |
| `extract_iris_metrics.py` | Extract iris measurements from images |
| `evaluate.py` | Model evaluation and metrics |
| `requirements.txt` | Python dependencies |
| `model.onnx` | Exported ONNX model file |

## 🎯 Features

- ✅ **Binary Classification**: Detects lazy eye vs normal eye conditions
- ✅ **Transfer Learning**: Uses pre-trained MobileNetV2 for better accuracy
- ✅ **Web Interface**: User-friendly upload and prediction interface
- ✅ **ONNX Export**: Cross-platform model deployment
- ✅ **GPU Support**: Automatic CUDA acceleration if available
- ✅ **Iris Metrics**: Detailed eye feature analysis
- ✅ **REST API**: Flask-based API for integration

## ⚙️ Configuration

Notes and tips:
- If GPU (CUDA) is available PyTorch will use it automatically.
- Use `--no-pretrained` in `train.py` to train from scratch.
- If your dataset is small, consider more aggressive augmentation or transfer learning with a larger pretrained backbone.

## 🔮 Future Enhancements

Possible improvements:
- Add TensorBoard / metrics logging
- Add a script to prepare/inspect class balance
- Add a notebook demonstrating training and evaluation
- Implement multi-class classification for various eye conditions
- Add data augmentation pipeline
- Integrate with medical database systems

## 📝 License

This project is for research and educational purposes.

## 👥 Contributors

SLIIT Research Team

---

**Last Updated**: January 2026
