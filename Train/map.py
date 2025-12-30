import os
import shutil
import pandas as pd

# CSV file path
CSV_FILE = "english.csv"

# Output base folder
OUTPUT_DIR = "data"

# Allowed capital letters
ALLOWED_LETTERS = [
    "A", "B", "C", "D", "E", "F", "G", "H",
    "J", "L", "N", "O", "P", "R", "S", "U", "V"
]

# Read CSV
df = pd.read_csv(CSV_FILE)

# Create main data folder
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create subfolders for each letter
for letter in ALLOWED_LETTERS:
    os.makedirs(os.path.join(OUTPUT_DIR, letter), exist_ok=True)

# Process each row
for _, row in df.iterrows():
    label = str(row["label"]).strip()
    image_path = row["image"]

    # Filter only required capital letters
    if label in ALLOWED_LETTERS and os.path.exists(image_path):
        destination = os.path.join(
            OUTPUT_DIR,
            label,
            os.path.basename(image_path)
        )

        shutil.copy(image_path, destination)

print("✅ Images copied successfully into letter-wise folders.")
