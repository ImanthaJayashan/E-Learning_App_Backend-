import argparse
import torch
from torchvision import transforms, models
from PIL import Image
import torch.nn as nn


def load_checkpoint(path, device):
    ckpt = torch.load(path, map_location=device)
    classes = ckpt.get('classes')
    # build model matching train.py
    model = models.mobilenet_v2(pretrained=False)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(nn.Dropout(0.2), nn.Linear(in_features, len(classes)))
    model.load_state_dict(ckpt['model_state'])
    model.to(device)
    model.eval()
    return model, classes


def predict(image_path, ckpt_path, img_size=224):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model, classes = load_checkpoint(ckpt_path, device)

    transform = transforms.Compose([
        transforms.Lambda(lambda img: img.convert('RGB')),
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    img = Image.open(image_path)
    x = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        out = model(x)
        probs = torch.nn.functional.softmax(out, dim=1)[0]
        conf, idx = torch.max(probs, 0)

    label = classes[idx]
    return label, float(conf)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('image', help='Path to image to classify')
    parser.add_argument('--ckpt', default='checkpoints/best_checkpoint.pth', help='Path to checkpoint')
    parser.add_argument('--img-size', type=int, default=224)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    label, conf = predict(args.image, args.ckpt, img_size=args.img_size)
    print(f"Prediction: {label} (confidence: {conf:.4f})")
