import argparse
from pathlib import Path
import onnx

def convert_onnx_to_savedmodel(onnx_path, saved_model_dir):
    try:
        from onnx_tf.backend import prepare
    except Exception as e:
        print('onnx-tf backend not available:', e)
        raise

    onnx_model = onnx.load(str(onnx_path))
    tf_rep = prepare(onnx_model)
    tf_rep.export_graph(str(saved_model_dir))
    print(f'Exported SavedModel to: {saved_model_dir}')


def savedmodel_to_h5(saved_model_dir, out_h5):
    import tensorflow as tf
    # load the saved model as a keras model (may work for many models)
    model = tf.keras.models.load_model(str(saved_model_dir))
    model.save(str(out_h5), overwrite=True)
    print(f'Saved Keras .h5 model to: {out_h5}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--onnx', default='model.onnx')
    p.add_argument('--saved-model-dir', default='saved_model')
    p.add_argument('--out', default='model.h5')
    args = p.parse_args()

    onnx_path = Path(args.onnx)
    if not onnx_path.exists():
        print('ONNX file not found:', onnx_path)
        raise SystemExit(1)

    saved_dir = Path(args.saved_model_dir)
    saved_dir.mkdir(exist_ok=True)

    convert_onnx_to_savedmodel(onnx_path, saved_dir)
    savedmodel_to_h5(saved_dir, Path(args.out))


if __name__ == '__main__':
    main()
