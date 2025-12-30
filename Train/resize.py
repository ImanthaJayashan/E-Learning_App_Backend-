import os
from PIL import Image

# Define the directory containing the folders
data_directory = 'data'

# Loop through each folder in the data directory
for foldername in os.listdir(data_directory):
    folder_path = os.path.join(data_directory, foldername)
    
    # Check if it's a directory
    if os.path.isdir(folder_path):
        # Loop through each file in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # Check if the file is an image
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Open the image
                with Image.open(file_path) as img:
                    # Resize the image
                    img = img.resize((450, 450))
                    # Save the resized image, optionally you can overwrite or save to a new location
                    img.save(file_path)

print("All images resized to 450x450 pixels.")