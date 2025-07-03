import shutil
import os
import time

def move(name):
    try:
        time.sleep(6)
        source = f"/home/zeglexa/Downloads/{name} 4.mp3"
        destination_folder = "./Songs"

        shutil.move(source, os.path.join(destination_folder, os.path.basename(source)))
    except FileNotFoundError:
        print("File not found :(")