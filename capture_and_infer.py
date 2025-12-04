import cv2
import os
from datetime import datetime
import subprocess


def capture_one_frame(camera_id=0, out_dir='received_samples'):
    os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError(f'Unable to open camera (id={camera_id})')

    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        raise RuntimeError('Failed to capture frame from camera')

    fname = datetime.utcnow().strftime('recv_%Y%m%dT%H%M%S.jpg')
    path = os.path.join(out_dir, fname)
    # write as jpeg
    cv2.imwrite(path, frame)
    return path


if __name__ == '__main__':
    print('Capturing one frame from the default camera...')
    try:
        img_path = capture_one_frame()
        print(f'Captured image: {img_path}')
        # Run inference.py on the captured image
        cmd = ['python', 'inference.py', img_path]
        print('Running inference on captured image...')
        subprocess.run(cmd)
    except Exception as e:
        print('Error:', e)
        raise
