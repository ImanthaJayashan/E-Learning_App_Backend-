import argparse
import os
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from tqdm import tqdm


def ensure_rgb(img):
    # module-level helper so it can be pickled by DataLoader workers on Windows
    return img.convert('RGB')


def get_dataloaders(data_dir, img_size=224, batch_size=32, num_workers=4):
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'test')

    train_transforms = transforms.Compose([
        transforms.Lambda(ensure_rgb),
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transforms = transforms.Compose([
        transforms.Lambda(ensure_rgb),
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transforms)
    val_dataset = datasets.ImageFolder(val_dir, transform=val_transforms)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return train_loader, val_loader, train_dataset.classes


def build_model(num_classes, pretrained=True):
    model = models.mobilenet_v2(pretrained=pretrained)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(nn.Dropout(0.2), nn.Linear(in_features, num_classes))
    return model


def train(args):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    # prepare dataloaders and datasets
    train_loader, val_loader, classes = get_dataloaders(args.data_dir, img_size=args.img_size,
                                                      batch_size=args.batch_size, num_workers=args.workers)

    # try to obtain the underlying ImageFolder to compute class distribution
    train_dataset = None
    try:
        # DataLoader.dataset may be a Subset or the dataset itself depending on sampler
        ds = train_loader.dataset
        # If it's a Subset, try to get the underlying dataset
        if hasattr(ds, 'dataset'):
            train_dataset = ds.dataset
        else:
            train_dataset = ds
    except Exception:
        train_dataset = None

    num_classes = len(classes)
    model = build_model(num_classes, pretrained=not args.no_pretrained)
    model = model.to(device)

    # Setup class weights or sampler if requested
    criterion = nn.CrossEntropyLoss()
    if args.use_class_weights and train_dataset is not None:
        try:
            import numpy as _np
            targets = _np.array(train_dataset.targets)
            counts = _np.bincount(targets, minlength=num_classes)
            weights = (targets.shape[0] / (counts + 1e-6)).astype('float32')
            # map per-class weight
            class_weights = (targets.shape[0] / (counts + 1e-6)).astype('float32')
            # normalize
            class_weights = class_weights / class_weights.sum() * num_classes
            class_weights = torch.tensor(class_weights, dtype=torch.float32).to(device)
            criterion = nn.CrossEntropyLoss(weight=class_weights)
            print('Using class weights for loss:', class_weights.cpu().numpy())
        except Exception as e:
            print('Failed to compute class weights:', e)

    # Weighted sampler
    if args.use_weighted_sampler and train_dataset is not None:
        try:
            import numpy as _np
            targets = _np.array(train_dataset.targets)
            class_sample_count = _np.bincount(targets, minlength=num_classes)
            weight_per_class = 1.0 / (class_sample_count + 1e-6)
            weights = weight_per_class[targets]
            weights = torch.DoubleTensor(weights)
            from torch.utils.data import WeightedRandomSampler
            sampler = WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)
            train_loader = DataLoader(train_dataset, batch_size=args.batch_size, sampler=sampler, num_workers=args.workers)
            print('Using WeightedRandomSampler for training loader')
        except Exception as e:
            print('Failed to create weighted sampler:', e)

    # Freeze backbone for initial epochs if requested
    if args.freeze_epochs and args.freeze_epochs > 0:
        for param in model.features.parameters():
            param.requires_grad = False
        print(f'Freezing backbone for first {args.freeze_epochs} epochs')

    # Setup optimizer with different LRs optionally
    if args.freeze_epochs and args.freeze_epochs > 0:
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=args.head_lr)
    else:
        # two-group lr: backbone and classifier
        backbone_params = [p for n, p in model.named_parameters() if 'features' in n]
        head_params = [p for n, p in model.named_parameters() if 'classifier' in n]
        optimizer = optim.Adam([
            {'params': backbone_params, 'lr': args.backbone_lr},
            {'params': head_params, 'lr': args.head_lr}
        ])

    best_acc = 0.0
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        # if freeze_epochs ended, unfreeze backbone and rebuild optimizer
        if args.freeze_epochs and epoch == args.freeze_epochs + 1:
            for param in model.features.parameters():
                param.requires_grad = True
            backbone_params = [p for n, p in model.named_parameters() if 'features' in n]
            head_params = [p for n, p in model.named_parameters() if 'classifier' in n]
            optimizer = optim.Adam([
                {'params': backbone_params, 'lr': args.backbone_lr},
                {'params': head_params, 'lr': args.head_lr}
            ])
        model.train()
        running_loss = 0.0
        running_corrects = 0
        total = 0

        loop = tqdm(train_loader, desc=f'Epoch {epoch}/{args.epochs} [train]')
        for inputs, labels in loop:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            running_corrects += torch.sum(preds == labels.data).item()
            total += inputs.size(0)
            loop.set_postfix(loss=running_loss / total, acc=running_corrects / total)

        train_loss = running_loss / total
        train_acc = running_corrects / total

        # Validation
        model.eval()
        val_loss = 0.0
        val_corrects = 0
        val_total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                val_corrects += torch.sum(preds == labels.data).item()
                val_total += inputs.size(0)

        val_loss = val_loss / val_total if val_total else 0
        val_acc = val_corrects / val_total if val_total else 0

        print(f"Epoch {epoch}: train_loss={train_loss:.4f} train_acc={train_acc:.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f}")

        # Save last
        torch.save({'epoch': epoch, 'model_state': model.state_dict(), 'classes': classes}, output_dir / 'last_checkpoint.pth')

        # Save best
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({'epoch': epoch, 'model_state': model.state_dict(), 'classes': classes}, output_dir / 'best_checkpoint.pth')

    print(f"Training complete. Best val_acc={best_acc:.4f}")


def parse_args():
    parser = argparse.ArgumentParser(description='Train eye lazy vs normal classifier')
    parser.add_argument('--data-dir', type=str, default='eye_data', help='Path to dataset root containing `train/` and `test/`')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--head-lr', type=float, default=1e-3, help='Learning rate for classifier head')
    parser.add_argument('--backbone-lr', type=float, default=1e-4, help='Learning rate for backbone when fine-tuning')
    parser.add_argument('--img-size', type=int, default=224)
    parser.add_argument('--output-dir', type=str, default='checkpoints')
    parser.add_argument('--workers', type=int, default=0, help='Number of DataLoader workers (0 for Windows safe)')
    parser.add_argument('--no-pretrained', action='store_true', help='Do not use pretrained weights')
    parser.add_argument('--use-class-weights', action='store_true', help='Use class weights in CrossEntropyLoss')
    parser.add_argument('--use-weighted-sampler', action='store_true', help='Use WeightedRandomSampler for training loader')
    parser.add_argument('--freeze-epochs', type=int, default=0, help='Number of first epochs to freeze backbone and train head only')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    train(args)
