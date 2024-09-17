import os
from tkinter import Tk, Label, Button, filedialog, messagebox, ttk, IntVar, Spinbox, StringVar, Frame, Text, Scrollbar, RIGHT, Y, LEFT, BOTH, DISABLED, NORMAL
from moviepy.editor import VideoFileClip
import concurrent.futures
import threading
import time

is_paused = False
is_stopped = False

def convert_single_mp4_to_mp3(mp4_file_path, mp3_file_path, progress_var, total_files, status_var, log_text, progress_label):
    global is_paused, is_stopped
    while is_paused:
        time.sleep(0.5) 
    
    if is_stopped:
        return 
    
    video = VideoFileClip(mp4_file_path)
    audio = video.audio
    audio.write_audiofile(mp3_file_path)
    audio.close()
    video.close()
    
    video_size = os.path.getsize(mp4_file_path) / (1024 * 1024)  
    audio_size = os.path.getsize(mp3_file_path) / (1024 * 1024)  
    
    status_var.set(f"Converted {os.path.basename(mp4_file_path)}: {video_size:.2f} MB -> {audio_size:.2f} MB")
   
    log_text.config(state='normal')
    log_text.insert('end', f"{os.path.basename(mp4_file_path)}: {video_size:.2f} MB -> {audio_size:.2f} MB\n")
    log_text.yview('end')  
    log_text.config(state='disabled')

    progress_var.set(progress_var.get() + 1)

    percent_done = (progress_var.get() / total_files) * 100
    progress_bar['value'] = percent_done
    progress_label.config(text=f"{percent_done:.2f}% completed")

def convert_mp4_to_mp3(source_folder, target_folder, max_threads, status_var, log_text, progress_label):
    global is_paused, is_stopped

    mp4_files = [file for file in os.listdir(source_folder) if file.endswith(".mp4")]

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    total_files = len(mp4_files)
    progress_var.set(0)

    log_text.config(state='normal')
    log_text.delete(1.0, "end")
    log_text.config(state='disabled')
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for file_name in mp4_files:
            if is_stopped:
                break
            mp4_file_path = os.path.join(source_folder, file_name)
            mp3_file_name = os.path.splitext(file_name)[0] + ".mp3"
            mp3_file_path = os.path.join(target_folder, mp3_file_name)
            
            futures.append(executor.submit(convert_single_mp4_to_mp3, mp4_file_path, mp3_file_path, progress_var, total_files, status_var, log_text, progress_label))

        for future in concurrent.futures.as_completed(futures):
            future.result()

    if not is_stopped:
        messagebox.showinfo("Conversion Complete", "All MP4 files have been converted to MP3!")
    
    start_button.config(state=DISABLED)
    pause_button.config(state=DISABLED)
    stop_button.config(state=DISABLED)

def pause_conversion():
    global is_paused
    is_paused = not is_paused
    if is_paused:
        pause_button.config(text="Resume")
    else:
        pause_button.config(text="Pause")

def stop_conversion():
    global is_stopped
    is_stopped = True

def select_source_folder():
    folder_selected = filedialog.askdirectory(title="Select the folder containing MP4 files")
    source_folder_label.config(text=folder_selected if folder_selected else "No folder selected")

def select_target_folder():
    folder_selected = filedialog.askdirectory(title="Select the target folder for MP3 files")
    target_folder_label.config(text=folder_selected if folder_selected else "No folder selected")

def start_conversion():
    global is_paused, is_stopped
    source_folder = source_folder_label.cget("text")
    target_folder = target_folder_label.cget("text")
    max_threads = int(thread_spinbox.get())

    if not source_folder or not target_folder:
        messagebox.showwarning("Folder Selection Error", "Please select both source and target folders.")
        return

    if max_threads <= 0 or max_threads > 500:
        messagebox.showwarning("Thread Error", "Please select between 1 and 500 threads.")
        return
    is_paused = False
    is_stopped = False
    start_button.config(state=NORMAL)
    pause_button.config(state=NORMAL)
    stop_button.config(state=NORMAL)
    pause_button.config(text="Pause") 
    
    conversion_thread = threading.Thread(target=convert_mp4_to_mp3, args=(source_folder, target_folder, max_threads, status_var, log_text, progress_label))
    conversion_thread.start()

root = Tk()
root.title("MP4 to MP3 Converter")
root.geometry("1070x500")
root.configure(bg="#202124")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", foreground="white", background="#202124", font=("Helvetica", 10))
style.configure("TButton", background="#00796B", foreground="white", font=("Helvetica", 10), relief="flat")
style.configure("TProgressbar", thickness=15)

main_frame = Frame(root, bg="#202124")
main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

Label(main_frame, text="Step 1: Select the folder containing MP4 files", font=("Helvetica", 12), fg="#42A5F5", bg="#202124").grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky='w')
source_folder_label = Label(main_frame, text="No folder selected", bg="#202124", fg="white", font=("Helvetica", 10))
source_folder_label.grid(row=1, column=0, columnspan=2, sticky='w')

Button(main_frame, text="Select Source Folder", command=select_source_folder, bg="#42A5F5", fg="white").grid(row=1, column=1, padx=10, pady=5)

Label(main_frame, text="Step 2: Select the target folder for MP3 files", font=("Helvetica", 12), fg="#42A5F5", bg="#202124").grid(row=2, column=0, columnspan=2, pady=(20, 5), sticky='w')
target_folder_label = Label(main_frame, text="No folder selected", bg="#202124", fg="white", font=("Helvetica", 10))
target_folder_label.grid(row=3, column=0, columnspan=2, sticky='w')

Button(main_frame, text="Select Target Folder", command=select_target_folder, bg="#42A5F5", fg="white").grid(row=3, column=1, padx=10, pady=5)

Label(main_frame, text="Recommended: 25-50 threads. More threads = more CPU power!", font=("Helvetica", 12), fg="#66BB6A", bg="#202124").grid(row=4, column=0, columnspan=2, pady=(20, 5), sticky='w')
thread_spinbox = Spinbox(main_frame, from_=1, to=500, width=10, font=("Helvetica", 10), fg="black", bg="white", relief="flat", highlightbackground="#42A5F5", highlightthickness=2)
thread_spinbox.grid(row=5, column=0, sticky='w')
thread_spinbox.delete(0, "end")
thread_spinbox.insert(0, "25") 

progress_var = IntVar()
progress_bar = ttk.Progressbar(main_frame, maximum=100, variable=progress_var, style="TProgressbar")
progress_bar.grid(row=6, column=0, columnspan=2, pady=20, sticky="ew")

progress_label = Label(main_frame, text="0% completed", font=("Helvetica", 10), bg="#202124", fg="white")
progress_label.grid(row=6, column=2, padx=10)

status_var = StringVar()
status_label = Label(main_frame, textvariable=status_var, font=("Helvetica", 10), bg="#202124", fg="#BBDEFB", wraplength=500, justify="left")
status_label.grid(row=7, column=0, columnspan=2, pady=10)

start_button = Button(main_frame, text="Start Conversion", command=start_conversion, bg="#00796B", fg="white", font=("Helvetica", 12))
start_button.grid(row=8, column=0, pady=10, sticky='ew')

pause_button = Button(main_frame, text="Pause", command=pause_conversion, bg="#FFA000", fg="white", font=("Helvetica", 12))
pause_button.grid(row=8, column=1, pady=10, padx=5, sticky='ew')

stop_button = Button(main_frame, text="Stop", command=stop_conversion, bg="#D32F2F", fg="white", font=("Helvetica", 12))
stop_button.grid(row=9, column=0, columnspan=2, pady=10, sticky='ew')

log_frame = Frame(root, bg="#2C2C2C", width=200)
log_frame.grid(row=0, column=1, sticky="ns")
log_text = Text(log_frame, wrap="word", font=("Helvetica", 10), bg="#2C2C2C", fg="white", height=25, state="disabled", bd=0)
log_text.pack(side=LEFT, fill=BOTH, expand=True)
log_scrollbar = Scrollbar(log_frame, command=log_text.yview)
log_scrollbar.pack(side=RIGHT, fill=Y)
log_text.config(yscrollcommand=log_scrollbar.set)
log_text.config(state='normal')
log_text.delete(1.0, "end")
log_text.tag_config('centered', justify='center', font=("Helvetica", 14, "bold"))
log_text.insert('end', "\n\n\nNothing Here, Start Convert...\n", 'centered')
log_text.config(state='disabled')
credit_label = Label(root, text="Github: @4fnanK", bg="#202124", fg="#42A5F5", font=("Helvetica", 9, "italic"))
credit_label.place(relx=1.0, rely=1.0, anchor='se', x=-20, y=-10)
root.mainloop()