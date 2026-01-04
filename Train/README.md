# Train - Data Preparation & Training

This folder contains scripts and data used to prepare the dataset and train the letter-classification model.

Files

- `map.py` — Reads `english.csv` and copies images into `data/<LETTER>/` folders for allowed letters.
- `train.py` — Uses a ResNet-18 (single-channel) to train a classifier on the images inside `data/`. The script saves model weights to `digits_model.pth`.
- `data/` — Organized dataset where subfolders are class labels (A, B, C, ...). Use `map.py` to regenerate this structure from `english.csv`.

How to prepare data

1. Place `english.csv` next to `map.py`. The CSV should have columns at least `label` and `image`.
2. Run:

```bash
python map.py
```

This creates `data/<LETTER>/` folders and copies images for the allowed letters.

Training

1. Ensure PyTorch and required packages are installed.
2. Run training:

```bash
python train.py
```

This will train for the configured number of epochs (default 10) and save `digits_model.pth` on completion.

Notes

- `train.py` uses grayscale transforms and normalizes images; adjust augmentation as needed.
- Class names and `num_classes` must match the folders under `data/`.
- After training, move or rename the saved model into `Backend/models/` if you want the Flask API to load it.