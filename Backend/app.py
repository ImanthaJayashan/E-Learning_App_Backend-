import io
import os
import torch
import torch.nn as nn
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from torchvision import transforms, models

# =========================
# APP SETUP
# =========================
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
CONFIDENCE_THRESHOLD = 0.8  # 80%

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =========================
# IMAGE TRANSFORM
# =========================
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# =========================
# MODEL
# =========================
letters_model = models.resnet18(weights="IMAGENET1K_V1")
letters_model.conv1 = nn.Conv2d(
    1, 64, kernel_size=7, stride=2, padding=3, bias=False
)
letters_model.fc = nn.Linear(letters_model.fc.in_features, 17)

letters_model.load_state_dict(
    torch.load("models/letters_model.pth", map_location=torch.device("cpu"))
)
letters_model.eval()

letters_class_names = [
    "A", "B", "C", "D", "E", "F", "G", "H",
    "J", "L", "N", "O", "P", "R", "S", "U", "V"
]

# =========================
# KID FRIENDLY MESSAGES
# =========================
def get_kid_message(actual, predicted, confidence):
    confidence_pct = confidence * 100

    if predicted == actual:
        if confidence >= 0.8:
            return {
                "message": f"🎉 Awesome job! You wrote the letter {actual} perfectly!",
                "emoji": "🌟",
                "confidence_level": "high"
            }
        elif confidence >= 0.5:
            return {
                "message": f"😊 Nice work! That looks like {actual}. Let’s try once more to make it even better!",
                "emoji": "✨",
                "confidence_level": "medium"
            }
        else:
            return {
                "message": f"👍 Good try! I can see {actual}. Let’s practice it again together!",
                "emoji": "💛",
                "confidence_level": "low"
            }
    else:
        return {
            "message": "💪 Good effort! Let’s try again and make the letter even clearer!",
            "emoji": "🌈",
            "confidence_level": "low"
        }

# =========================
# PREDICT ROUTE
# =========================
@app.route("/predict", methods=["POST"])
def predict_letter():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    if "actual_letter" not in request.form:
        return jsonify({"error": "Actual letter missing"}), 400

    file = request.files["image"]
    actual_letter = request.form["actual_letter"].upper()

    try:
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("L")

        # Save image (optional debugging)
        image.save(os.path.join(UPLOAD_FOLDER, file.filename))

        input_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = letters_model(input_tensor)
            probs = torch.softmax(outputs, dim=1)

            top_prob, top_idx = torch.max(probs, 1)
            predicted_letter = letters_class_names[top_idx.item()]
            confidence = top_prob.item()

        kid_feedback = get_kid_message(
            actual_letter,
            predicted_letter,
            confidence
        )

        response = {
            "actual_letter": actual_letter,
            "predicted_letter": predicted_letter,
            "confidence": f"{confidence * 100:.2f}%",
            "is_correct": predicted_letter == actual_letter,
            "confidence_level": kid_feedback["confidence_level"],
            "kid_message": kid_feedback["message"],
            "emoji": kid_feedback["emoji"],
            "all_probabilities": {
                letters_class_names[i]: f"{probs[0][i].item() * 100:.2f}%"
                for i in range(len(letters_class_names))
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
