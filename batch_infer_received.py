import os
import glob
import json
import argparse
from pathlib import Path

def main(received_dir='received_samples', ckpt='checkpoints/best_checkpoint.pth', img_size=224):
    received = Path(received_dir)
    if not received.exists():
        print(f'No directory: {received_dir}')
        return 1

    # local import of project's inference.predict
    try:
        from inference import predict
    except Exception as e:
        print('Failed to import predict from inference.py:', e)
        return 2

    patterns = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    files = []
    for p in patterns:
        files.extend(sorted(received.glob(p)))

    if not files:
        print('No images found in', received_dir)
        return 0

    results = []
    for f in files:
        path = str(f)
        print('Processing', path)
        try:
            label, conf = predict(path, ckpt, img_size=img_size)
        except Exception as e:
            print('  Error running inference:', e)
            label, conf = None, None
        results.append({'file': path, 'label': label, 'confidence': conf})

    out_path = received / 'inference_results.json'
    with open(out_path, 'w', encoding='utf8') as fh:
        json.dump(results, fh, indent=2)

    # Print summary
    counts = {}
    for r in results:
        lab = r['label'] or 'ERROR'
        counts[lab] = counts.get(lab, 0) + 1

    print('\nSummary:')
    for k, v in counts.items():
        print(f'  {k}: {v}')

    print('\nSaved results to', out_path)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='received_samples', help='Directory with received images')
    parser.add_argument('--ckpt', default='checkpoints/best_checkpoint.pth')
    parser.add_argument('--img-size', type=int, default=224)
    args = parser.parse_args()
    raise SystemExit(main(received_dir=args.dir, ckpt=args.ckpt, img_size=args.img_size))
