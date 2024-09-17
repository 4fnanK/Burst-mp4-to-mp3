import os
from moviepy.editor import VideoFileClip
from tkinter import Tk, filedialog
import concurrent.futures

def convert_single_mp4_to_mp3(mp4_file_path, mp3_file_path):
    print(f"Converting {mp4_file_path} to {mp3_file_path}...")
    video = VideoFileClip(mp4_file_path)
    audio = video.audio
    audio.write_audiofile(mp3_file_path)
    audio.close()
    video.close()
def convert_mp4_to_mp3(source_folder, target_folder, max_threads):
    if max_threads > 500:
        print(f"Max threads set too high. Limiting to 500 threads.")
        max_threads = 500
    elif max_threads > 40:
        print(f"Note: You have selected more than the recommended number of threads (20-40). Proceeding with {max_threads} threads.")
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    mp4_files = [file for file in os.listdir(source_folder) if file.endswith(".mp4")]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for file_name in mp4_files:
            mp4_file_path = os.path.join(source_folder, file_name)
            mp3_file_name = os.path.splitext(file_name)[0] + ".mp3"
            mp3_file_path = os.path.join(target_folder, mp3_file_name)
            
            futures.append(executor.submit(convert_single_mp4_to_mp3, mp4_file_path, mp3_file_path))
        
        for future in concurrent.futures.as_completed(futures):
            future.result() 
    
    print("Conversion completed!")

def select_folder(title):
    root = Tk()
    root.withdraw() 
    folder_selected = filedialog.askdirectory(title=title)
    return folder_selected

if __name__ == "__main__":
    print("Step 1: Select the folder that contains your MP4 files.")
    source_folder = select_folder("Select the folder containing MP4 files")
    if not source_folder:
        print("No folder selected. Exiting.")
        exit()

    print("Step 2: Select the target folder where the MP3 files will be saved.")
    target_folder = select_folder("Select the target folder for MP3 files")
    if not target_folder:
        print("No folder selected. Exiting.")
        exit()
    try:
        max_threads = int(input("Enter the number of threads (recommended 20-40, max 500): "))
    except ValueError:
        print("Invalid input. Using default of 20 threads.")
        max_threads = 20

    convert_mp4_to_mp3(source_folder, target_folder, max_threads=max_threads)
