# Eye Ball (Lazy vs Normal) Training

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

Notes and tips:
- If GPU (CUDA) is available PyTorch will use it automatically.
- Use `--no-pretrained` in `train.py` to train from scratch.
- If your dataset is small, consider more aggressive augmentation or transfer learning with a larger pretrained backbone.

If you want, I can:
- add TensorBoard / metrics logging
- add a small script to prepare/inspect class balance
- add a notebook demonstrating training and evaluation
