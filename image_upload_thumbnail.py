# This script monitors, written in Python, monitors one directory. 
# When file with jpg extention is dropped in that directory, the script creates a thumbnail.

# File must can be dropped using a mouse or copy-pasted. 

# The script is useful for autoamted updates of a website. 

import os  # For operating system interactions
from PIL import Image  # Python Imaging Library for image processing
from watchdog.observers import Observer  # For monitoring filesystem events
from watchdog.events import PatternMatchingEventHandler  # For handling specific file patterns
import time  # To add delays

# Name your directories
IMAGES_DIR = r"C:\projects\templates\images"
THUMBNAILS_DIR = r"C:\projects\templates\thumbnails"
SAVE_LOGS = r"C:\projects\templates\logs"

class ImageEventHandler(PatternMatchingEventHandler):
    def __init__(self, source_dir, target_dir, save_logs_dir, patterns=None): # define all paths
        super().__init__(patterns=patterns)    #constructor of the supercalss event handler will only react to filesystem events for files that match these patterns (in this case, images)
        # list all absolute paths
        self.source_dir = os.path.abspath(source_dir) 
        self.target_dir = os.path.abspath(target_dir)
        self.save_logs_dir = os.path.abspath(save_logs_dir)
        os.makedirs(self.target_dir, exist_ok=True)  # Ensure target directory exists. If not, directory is created.
        os.makedirs(self.save_logs_dir, exist_ok=True)  # Ensure save_logs directory exists

    def on_created(self, event):
        super(ImageEventHandler, self).on_created(event) # Calls the on_created method of the superclass for code completness (code should run without this line). 
        # Process only if it's an image file in the source directory
        if os.path.dirname(os.path.abspath(event.src_path)) == self.source_dir: # safety check to make sure that created directory matches monitored directory
            self.process_new_image(event.src_path)

    def process_new_image(self, path):
        script_name = os.path.basename(__file__)  # Get the current script name
        filename = os.path.basename(path) #read file name
        thumbnail_path = os.path.join(self.target_dir, f"thmb-{filename}") #call new thumbnail with the prefix and the same name as the file
        absolute_path = os.path.abspath(path)
        file_size = os.path.getsize(path)  # Get the size of the image file in bytes**

        start_time = time.time()  # Start timing to calculate the metrix of image processing

        # Attempt to open and process the image with retries
        for attempt in range(5):  # Try up to 5 times to handle acceprable errors
            try:
                with Image.open(path) as img: # open image (with ensures that it gest closed)
                    img.thumbnail((100, 100)) # create thumbnail of the image
                    img.save(thumbnail_path) # save thumbnail
                print(f"Thumbnail created: {thumbnail_path}")
                break  # Proceed sucessful script without additional attempts
            except IOError as e:
                print(f"Attempt {attempt + 1}: Failed to create thumbnail for {filename}: {e}")
                time.sleep(1)  # Wait for 1 second before retrying
            except Exception as e:
                print(f"Unexpected error creating thumbnail for {filename}: {e}")
                break  # Exit the loop on unexpected errors
        else:
            print(f"Failed to create thumbnail for {filename} after multiple attempts.")

# Calcuate and print metrix for the speed of this script:
        end_time = time.time()
        duration = end_time - start_time
        processing_message = f"{script_name}:{absolute_path}, File size is {file_size} bytes, Processing time : {duration} seconds.\n"

        print(processing_message.strip())
        
        log_file_path = os.path.join(self.save_logs_dir, "time_log.txt")  # Path for the log file within SAVE_LOGS directory
        with open(log_file_path, "a", encoding='utf-8') as log_file:
            log_file.write(processing_message)

if __name__ == "__main__":
    patterns = ["*.jpg", "*.jpeg"]  # Only process JPEG images
    event_handler = ImageEventHandler(IMAGES_DIR, THUMBNAILS_DIR, SAVE_LOGS, patterns=patterns)
    observer = Observer()
    observer.schedule(event_handler, IMAGES_DIR, recursive=False) # Tells the observer to monitor the IMAGES_DIR directory using the event_handler, without monitoring subdirectories (recursive=False
    observer.start()
    print("Monitoring for new images...")

    # The script will continue running until manually stopped
    observer.join()