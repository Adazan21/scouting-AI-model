import cv2
import torch
import numpy as np
from pathlib import Path
import time
from PIL import Image
import imagehash
import os

# Load YOLOv5 model with the absolute path (no spaces in path)
model_path = Path(r'A:\python_project\yolov5\runs\train\exp5\weights\best.pt')
yolov5_path = Path(r'A:\python_project\yolov5')

# Check if hubconf.py exists
if not (yolov5_path / 'hubconf.py').exists():
    print('Error: hubconf.py not found in YOLOv5 directory.')
    exit()

# Load the model using torch.hub
model = torch.hub.load(
    str(yolov5_path),
    'custom',
    path=str(model_path),
    source='local'
)


# Initialize the webcam
cap = cv2.VideoCapture(0)

# Set to store unique plant image hashes and keypoint descriptors
saved_hashes = set()
saved_descriptors = []

# Initialize ORB detector for feature-based matching
orb = cv2.ORB_create()
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Define allowed class IDs (e.g., only pollen sacs or specific plant classes)
allowed_classes = [0]  # Update this list with the actual class IDs for pollen sacs

# Define the directory to save images
save_directory = 'C:/python_project/saved_images'
os.makedirs(save_directory, exist_ok=True)

try:
    while True:
        # Read frame from the webcam
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        # Convert frame to RGB format for YOLOv5
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run YOLOv5 model on the frame
        results = model(frame_rgb)

        for detection in results.pred[0]:
            x1, y1, x2, y2, confidence, class_id = detection[:6]
            if confidence < 0.6 or int(class_id) not in allowed_classes:
                continue
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f'{model.names[int(class_id)]}: {confidence:.2f}'
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Feature matching to avoid duplicate images
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            keypoints, descriptors = orb.detectAndCompute(gray_frame, None)
            unique = True

            for saved_desc in saved_descriptors:
                matches = bf.match(descriptors, saved_desc)
                if len(matches) > 50:  # Threshold to determine if image is a duplicate
                    unique = False
                    break

            # If the frame is unique, save the image
            if unique:
                saved_descriptors.append(descriptors)
                pil_image = Image.fromarray(frame_rgb)
                image_hash = imagehash.phash(pil_image)
                if image_hash not in saved_hashes:
                    saved_hashes.add(image_hash)
                    image_path = os.path.join(save_directory, f'plant_{time.time()}.png')
                    cv2.imwrite(image_path, frame)
                    print(f'Image saved: {image_path}')

        cv2.imshow('YOLOv5 Live Detections', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user")

cap.release()
cv2.destroyAllWindows()
