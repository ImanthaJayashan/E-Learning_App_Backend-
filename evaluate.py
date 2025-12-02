import argparse
import os
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import numpy as np


def ensure_rgb(img):
    return img.convert('RGB')


def load_checkpoint(path, device):
    ckpt = torch.load(path, map_location=device)
    classes = ckpt.get('classes')
    model = models.mobilenet_v2(pretrained=False)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(nn.Dropout(0.2), nn.Linear(in_features, len(classes)))
    model.load_state_dict(ckpt['model_state'])
    model.to(device)
    model.eval()
    return model, classes


def evaluate(data_dir, ckpt_path, img_size=224, batch_size=32):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model, classes = load_checkpoint(ckpt_path, device)

    test_dir = os.path.join(data_dir, 'test')
    transform = transforms.Compose([
        transforms.Lambda(ensure_rgb),
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    dataset = datasets.ImageFolder(test_dir, transform=transform)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for imgs, labels in loader:
            imgs = imgs.to(device)
            out = model(imgs)
            preds = torch.argmax(out, dim=1).cpu().numpy()
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.numpy().tolist())

    all_preds = np.array(all_preds, dtype=int)
    all_labels = np.array(all_labels, dtype=int)

    acc = (all_preds == all_labels).mean() if len(all_labels) > 0 else 0.0

    # confusion matrix
    n = len(classes)
    cm = np.zeros((n, n), dtype=int)
    for t, p in zip(all_labels, all_preds):
        cm[t, p] += 1

    print(f"Evaluated {len(all_labels)} images")
    print(f"Overall accuracy: {acc:.4f}")
    print("Classes:", classes)
    print("Confusion matrix (rows=true, cols=pred):")
    print(cm)

    # per-class precision/recall/f1
    for i, cls in enumerate(classes):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        print(f"{cls}: precision={precision:.3f} recall={recall:.3f} f1={f1:.3f} support={cm[i,:].sum()}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default='eye_data')
    parser.add_argument('--ckpt', default='checkpoints/best_checkpoint.pth')
    parser.add_argument('--img-size', type=int, default=224)
    parser.add_argument('--batch-size', type=int, default=32)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    ckpt_path = Path(args.ckpt)
    if not ckpt_path.exists():
        print(f"Checkpoint not found: {ckpt_path}")
        raise SystemExit(1)
    evaluate(args.data_dir, str(ckpt_path), img_size=args.img_size, batch_size=args.batch_size)
