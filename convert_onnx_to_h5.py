import argparse
import onnx
from onnx2keras import onnx_to_keras
from tensorflow.keras.models import save_model
from pathlib import Path


def convert(onnx_path, out_path):
    onnx_path = Path(onnx_path)
    if not onnx_path.exists():
        print(f"ONNX file not found: {onnx_path}")
        raise SystemExit(1)

    print(f"Loading ONNX model from: {onnx_path}")
    onnx_model = onnx.load(str(onnx_path))

    # input names should match the names used when exporting; we used 'input'
    input_names = ['input']
    print("Converting ONNX -> Keras (this may take a while)...")
    try:
        k_model = onnx_to_keras(onnx_model, input_names, change_ordering=True)
    except Exception as e:
        print("Conversion failed:", e)
        raise

    out_path = Path(out_path)
    print(f"Saving Keras model to: {out_path}")
    save_model(k_model, str(out_path), overwrite=True)
    print("Saved model.h5 successfully")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--onnx', default='model.onnx')
    p.add_argument('--out', default='model.h5')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    convert(args.onnx, args.out)
