import torch
import torch.nn as nn
from torchvision import models
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

letters_model = models.resnet18(weights='IMAGENET1K_V1')
letters_model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
letters_model.fc = nn.Linear(letters_model.fc.in_features, 17)

letters_model.eval()

@app.route('/')
def home():
    return {"message": "Model architecture initialized"}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
