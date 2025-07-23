from roboflow import Roboflow
import os
import shutil

# Initialize Roboflow with your API key
rf = Roboflow(api_key="sjLBs9H2aOiaqaFRRPGm")
project = rf.workspace("calyx-wmudo").project("gender2-jfgly")
version = project.version(58)

# Download the dataset as a ZIP file and extract it
dataset = version.download("yolov5")

# Set the path to move data to the desired project structure
source_folder = f"{dataset.location}/train"
dest_train_images = "A:/python_Project/data/train/images"
dest_train_labels = "A:/python_Project/data/train/labels"
dest_valid_images = "A:/python_Project/data/valid/images"
dest_valid_labels = "A:/python_Project/data/valid/labels"

# Ensure the directories exist
os.makedirs(dest_train_images, exist_ok=True)
os.makedirs(dest_train_labels, exist_ok=True)
os.makedirs(dest_valid_images, exist_ok=True)
os.makedirs(dest_valid_labels, exist_ok=True)

# Move the images and labels to the train and valid directories
for split in ["train", "valid"]:
    images_source = f"{dataset.location}/{split}/images"
    labels_source = f"{dataset.location}/{split}/labels"

    if split == "train":
        images_dest = dest_train_images
        labels_dest = dest_train_labels
    else:
        images_dest = dest_valid_images
        labels_dest = dest_valid_labels

    for file_name in os.listdir(images_source):
        shutil.move(os.path.join(images_source, file_name), os.path.join(images_dest, file_name))

    for file_name in os.listdir(labels_source):
        shutil.move(os.path.join(labels_source, file_name), os.path.join(labels_dest, file_name))

print("Dataset moved successfully!")
