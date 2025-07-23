import sys
import os

# Add yolov5 directory to system path
sys.path.append(os.path.abspath('A:/python_Project/yolov5'))

# Import YOLOv5's run function from detect.py
from detect import run

# Define the input and output folders
input_folder = 'A:/python_Project/my_images'  # Folder for input images
output_folder = 'A:/python_Project/processed_images'  # Folder for processed output images

# Ensure output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Run YOLOv5 on the images in the input folder
run(
    source=input_folder,                # Path to input images
    weights='A:/python_Project/yolov5/yolov5s.pt',  # Path to YOLOv5 model weights
    project=output_folder,              # Output folder for processed images
    name='exp',                         # Experiment name (can be changed)
    exist_ok=True                       # Do not overwrite existing results
)

print(f"Images processed and saved to {output_folder}")
