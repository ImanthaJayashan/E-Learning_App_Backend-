import argparse
import cv2
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np

try:
    import mediapipe as mp
except Exception:
    mp = None


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


def face_mesh_eyes_present(results, threshold=0.3):
    """
    Determine if eyes are present using MediaPipe Face Mesh landmarks.
    We'll check that a sufficient number of eye landmarks are visible.
    """
    if not results or not results.multi_face_landmarks:
        return False

    # landmarks indices for left and right eyes (approximate sets)
    left_eye_idx = [33, 7, 163, 144, 145, 153, 154, 155, 133]
    right_eye_idx = [263, 249, 390, 373, 374, 380, 381, 382, 362]

    for face_landmarks in results.multi_face_landmarks:
        vis_count = 0
        total = len(left_eye_idx) + len(right_eye_idx)
        for idx in left_eye_idx + right_eye_idx:
            lm = face_landmarks.landmark[idx]
            # mediapipe landmarks have visibility/presence for some versions; treat presence by z and x/y bounds
            if 0.0 <= lm.x <= 1.0 and 0.0 <= lm.y <= 1.0:
                vis_count += 1

        if vis_count / float(total) >= threshold:
            return True

    return False


def build_transform(img_size=224):
    return transforms.Compose([
        transforms.Lambda(lambda img: img.convert('RGB')),
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])


def run_camera(ckpt, img_size=224, camera_id=0, show_fps=False, image_path=None, require_eyes=True):
    """
    If `image_path` is provided, run single-image inference (doesn't require MediaPipe).
    Otherwise try to use MediaPipe FaceMesh for camera-based eye detection; if MediaPipe
    is not available, fall back to camera-only classification (no eye gating) with a warning.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model, classes = load_checkpoint(ckpt, device)
    transform = build_transform(img_size=img_size)

    # Single image mode: skip MediaPipe entirely
    if image_path:
        img = Image.open(image_path)
        x = transform(img).unsqueeze(0).to(device)
        with torch.no_grad():
            out = model(x)
            probs = torch.nn.functional.softmax(out, dim=1)[0]
            conf, idx = torch.max(probs, 0)
            label = classes[idx]
        print(f'Image prediction: {label} ({conf:.4f})')
        return

    # Camera mode
    use_mediapipe = mp is not None
    if use_mediapipe:
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1,
                                          refine_landmarks=True, min_detection_confidence=0.5,
                                          min_tracking_confidence=0.5)
    else:
        face_mesh = None
        if require_eyes:
            print('Warning: MediaPipe not available; --require-eyes enabled but will be ignored. Install mediapipe to enable eye detection.')

    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError(f'Unable to open camera (id={camera_id})')

    prev_time = cv2.getTickCount()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert to RGB for mediapipe if available
            results = None
            if face_mesh is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb)

            eyes_present = True
            if require_eyes and face_mesh is not None:
                eyes_present = face_mesh_eyes_present(results)

            display_text = ''
            if eyes_present:
                # Crop face bounding box from landmarks if available; otherwise use whole frame center crop
                h, w, _ = frame.shape
                if results and results.multi_face_landmarks:
                    lm = results.multi_face_landmarks[0]
                    xs = [int(p.x * w) for p in lm.landmark]
                    ys = [int(p.y * h) for p in lm.landmark]
                    x1, x2 = max(min(xs) - 10, 0), min(max(xs) + 10, w)
                    y1, y2 = max(min(ys) - 10, 0), min(max(ys) + 10, h)
                    face_img = frame[y1:y2, x1:x2]
                else:
                    face_img = frame

                if face_img.size == 0:
                    display_text = 'No face crop'
                else:
                    pil = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
                    x = transform(pil).unsqueeze(0).to(device)
                    with torch.no_grad():
                        out = model(x)
                        probs = torch.nn.functional.softmax(out, dim=1)[0]
                        conf, idx = torch.max(probs, 0)
                        label = classes[idx]
                        display_text = f'{label} ({conf:.2f})'
            else:
                display_text = 'Eyes not detected — no result'

            # Overlay text
            cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 255, 0) if eyes_present else (0, 0, 255), 2)

            # Draw face landmarks if available
            if results and results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    for lm in face_landmarks.landmark:
                        x = int(lm.x * frame.shape[1])
                        y = int(lm.y * frame.shape[0])
                        cv2.circle(frame, (x, y), 1, (255, 0, 0), -1)

            # FPS
            if show_fps:
                cur_time = cv2.getTickCount()
                fps = cv2.getTickFrequency() / (cur_time - prev_time) if cur_time != prev_time else 0.0
                prev_time = cur_time
                cv2.putText(frame, f'FPS: {fps:.1f}', (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 0), 2)

            cv2.imshow('Camera (press q to quit)', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        if face_mesh is not None:
            face_mesh.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ckpt', default='checkpoints/best_checkpoint.pth')
    parser.add_argument('--img-size', type=int, default=224)
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--fps', action='store_true', help='Show FPS overlay')
    parser.add_argument('--image', type=str, default=None, help='Path to single image for inference')
    parser.add_argument('--require-eyes', action='store_true', help='Only run classifier when eyes are detected (ignored if MediaPipe unavailable)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    run_camera(args.ckpt, img_size=args.img_size, camera_id=args.camera, show_fps=args.fps)
