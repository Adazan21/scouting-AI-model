import os
import json
import re
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Function to extract GPS data from an image
def get_gps_data(image_path):
    try:
        result = subprocess.run(
            ["A:\\exiftool-13.01_64\\exiftool.exe", "-GPSLatitude", "-GPSLongitude", "-GPSLatitudeRef", "-GPSLongitudeRef", image_path],
            capture_output=True,
            text=True
        )
        output = result.stdout

        gps_data = {}
        for line in output.splitlines():
            if "GPS Latitude" in line and "Ref" not in line:
                gps_data['Latitude'] = line.split(": ")[1].strip()
            elif "GPS Longitude" in line and "Ref" not in line:
                gps_data['Longitude'] = line.split(": ")[1].strip()
            elif "GPS Latitude Ref" in line:
                lat_ref = line.split(": ")[1].strip()
                gps_data['LatitudeRef'] = "N" if "North" in lat_ref else "S" if "South" in lat_ref else lat_ref
            elif "GPS Longitude Ref" in line:
                lon_ref = line.split(": ")[1].strip()
                gps_data['LongitudeRef'] = "E" if "East" in lon_ref else "W" if "West" in lon_ref else lon_ref

        if "Latitude" in gps_data and "Longitude" in gps_data:
            cleaned_latitude = re.sub(r"[^\d. ]", "", gps_data['Latitude'])
            cleaned_longitude = re.sub(r"[^\d. ]", "", gps_data['Longitude'])
            latitude = convert_to_decimal(cleaned_latitude, gps_data.get('LatitudeRef', 'N'))
            longitude = convert_to_decimal(cleaned_longitude, gps_data.get('LongitudeRef', 'E'))
            return latitude, longitude
        else:
            print(f"No GPS data found for {image_path}")

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    return None

def convert_to_decimal(coordinate, ref):
    # Convert cleaned DMS (Degrees, Minutes, Seconds) string to decimal
    parts = coordinate.split()
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    return decimal if ref in ['N', 'E'] else -decimal

def update_locations_json(new_entry):
    output_path = r"/website\locations.json"
    try:
        # Load existing data
        if os.path.exists(output_path):
            with open(output_path, "r") as file:
                locations = json.load(file)
        else:
            locations = []

        # Append the new entry
        locations.append(new_entry)

        # Write updated data back to locations.json
        with open(output_path, "w") as file:
            json.dump(locations, file, indent=4)
        print(f"Updated {output_path} with new entry.")
    except Exception as e:
        print(f"Error updating locations.json: {e}")

# Define event handler for the folder watcher
class NewImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
            print(f"New image detected: {event.src_path}")
            coords = get_gps_data(event.src_path)
            if coords:
                new_entry = {
                    "lat": coords[0],
                    "lng": coords[1],
                    "description": f"Detected plant at {os.path.basename(event.src_path)}",
                    "imagePath": f"images/{os.path.basename(event.src_path)}"  # Adjust as needed
                }
                update_locations_json(new_entry)

# Set up folder to watch and start the observer
folder_to_watch = r"A:\python_Project\processed_images\exp"
event_handler = NewImageHandler()
observer = Observer()
observer.schedule(event_handler, folder_to_watch, recursive=False)
observer.start()

try:
    print(f"Watching folder: {folder_to_watch}")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
