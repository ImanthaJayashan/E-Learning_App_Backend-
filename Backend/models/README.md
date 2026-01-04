# Backend/models

This folder stores model weights used by the Flask API (`Backend/app.py`).

Expected files

- `letters_model.pth` — ResNet-18 weights adapted to a single grayscale input and outputting 17 classes. The Flask app loads this with `torch.load("models/letters_model.pth", map_location=torch.device("cpu"))`.

Notes

- If you train a model in `Train/` and get `digits_model.pth`, rename or copy it to `Backend/models/letters_model.pth` (or update `Backend/app.py` to load the different filename).
- Ensure file permissions allow the Flask app to read the file.
