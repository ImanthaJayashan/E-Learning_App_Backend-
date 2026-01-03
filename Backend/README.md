# Handwritten Letter Prediction (Backend)

This repository contains a simple Flask backend and a sample frontend for predicting handwritten letters using a PyTorch ResNet18-based model adapted for grayscale images.

## Features
- Flask API endpoint `/predict` that accepts an image and returns a predicted letter, confidence, kid-friendly feedback, and per-class probabilities.
- Frontend `index.html` provides a canvas UI to draw a letter and send it to the backend for prediction.
- Uses a modified `resnet18` model (single-channel input, 17 output classes) with a pre-trained weights file at `models/letters_model.pth`.

## Repository structure

- `app.py` — Flask application implementing the `/predict` endpoint.
- `index.html` — Simple client UI (canvas) to draw letters and call the API.
- `models/letters_model.pth` — Trained PyTorch model weights (binary file).
- `uploads/` — Folder where uploaded images are saved (created automatically).

## Requirements
- Python 3.8+
- Packages:
  - flask
  - flask-cors
  - torch
  - torchvision
  - pillow

You can install the main dependencies with pip (example):

```bash
pip install flask flask-cors pillow torch torchvision
```

Note: Installing `torch` and `torchvision` is platform- and CUDA-dependent. For CPU-only usage, follow the official instructions at https://pytorch.org/ to install the correct wheel for your environment.

## Running the backend

1. Ensure `models/letters_model.pth` exists in the `models/` directory.
2. From the repository root, run:

```bash
python app.py
```

The Flask server will start on `http://127.0.0.1:5000` by default.

## Using the API

Endpoint: `POST /predict`

Form data parameters:
- `image` — image file (PNG/JPEG) of the drawn letter.
- `actual_letter` — (optional for testing) single character of the expected letter.

Successful response includes:
- `predicted_letter`, `confidence` (percentage), `is_correct`, `kid_message`, `emoji`, and `all_probabilities`.

Example curl (replace `letter.png` with your image):

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -F "image=@letter.png" \
  -F "actual_letter=A"
```

## Frontend

Open `index.html` in your browser (or serve it via a static server). The page draws a letter on a canvas and sends the drawing to the backend endpoint at `http://127.0.0.1:5000/predict`.

Note: The frontend expects the backend to run locally on port 5000. If you run the backend elsewhere, update the fetch URL in `index.html`.

## Notes and caveats
- The model expects grayscale images transformed to a single channel and normalized in `app.py`.
- `uploads/` will store the received images; remove or rotate this folder if storing many uploads.
- The letters class set inside `app.py` contains 17 classes: A, B, C, D, E, F, G, H, J, L, N, O, P, R, S, U, V.

## Development
- To change the model architecture or classes, update `app.py` accordingly and re-train/export a new `letters_model.pth`.

## License
This README and the code are provided as-is. Add a proper license file if you intend to redistribute.
