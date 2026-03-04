import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path
import argparse


def build_model(num_classes, pretrained=False):
    model = models.mobilenet_v2(pretrained=pretrained)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(nn.Dropout(0.2), nn.Linear(in_features, num_classes))
    return model


def export(checkpoint_path, out_path='model.onnx', img_size=224):
    device = torch.device('cpu')
    ckpt = torch.load(checkpoint_path, map_location=device)
    classes = ckpt.get('classes')
    if classes is None:
        raise RuntimeError('Checkpoint does not contain `classes` list')

    model = build_model(len(classes), pretrained=False)
    model.load_state_dict(ckpt['model_state'])
    model.eval()

    dummy = torch.randn(1, 3, img_size, img_size, device=device)
    out_path = Path(out_path)
    torch.onnx.export(
        model,
        dummy,
        str(out_path),
        opset_version=13,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f'Exported ONNX model to: {out_path.resolve()}')
    return out_path.resolve()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ckpt', default='checkpoints/best_checkpoint.pth')
    parser.add_argument('--out', default='model.onnx')
    parser.add_argument('--img-size', type=int, default=224)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    ckpt = Path(args.ckpt)
    if not ckpt.exists():
        print(f'Checkpoint not found: {ckpt}')
        raise SystemExit(1)
    export(str(ckpt), out_path=args.out, img_size=args.img_size)
