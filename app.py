import os
import subprocess
import threading
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

VIDEOS_DIR = ""
OUTPUT_FILE = ""

LIST_FILE = "list.txt"

def create_list_file():
    files = sorted(f for f in os.listdir(VIDEOS_DIR) if f.endswith(".mp4"))
    
    if not files:
        messagebox.showerror("Error", "❌ No MP4 files found in folder!")
        return False

    with open(LIST_FILE, "w", encoding="utf-8") as f:
        for file in files:
            path = os.path.abspath(os.path.join(VIDEOS_DIR, file)).replace("'", "\\'")
            f.write(f"file '{path}'\n")

    return True

def merge_videos():
    global OUTPUT_FILE
    if not OUTPUT_FILE:
        OUTPUT_FILE = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")],
            title="Save output as..."
        )
        if not OUTPUT_FILE:
            return

    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", LIST_FILE,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        OUTPUT_FILE
    ]


    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            if "frame=" in line or "time=" in line:
                progress_bar.step(0.5)  # تقريب التقدم لأنه بدون إعادة ترميز
                root.update_idletasks()
        process.wait()
        os.remove(LIST_FILE)
        messagebox.showinfo("Success", f"✅ Videos merged successfully!\nOutput: {OUTPUT_FILE}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "❌ Failed to merge videos.")

def start_merge_thread():
    if not VIDEOS_DIR:
        messagebox.showwarning("Warning", "Please select a folder first!")
        return
    if create_list_file():
        threading.Thread(target=merge_videos, daemon=True).start()

def select_folder():
    global VIDEOS_DIR
    VIDEOS_DIR = filedialog.askdirectory()
    if VIDEOS_DIR:
        folder_label.config(text=VIDEOS_DIR)

# ===== Tkinter GUI =====
root = Tk()
root.title("Video Merger")
root.geometry("600x300")
root.configure(bg="#2c2c2c")

Label(root, text="Video Merger Tool", font=("Arial", 18, "bold"), fg="white", bg="#2c2c2c").pack(pady=10)

folder_label = Label(root, text="No folder selected", bg="#2c2c2c", fg="white")
folder_label.pack(pady=5)

Button(root, text="Select Folder", command=select_folder, width=20, bg="#4CAF50", fg="white").pack(pady=5)
Button(root, text="Merge Videos", command=start_merge_thread, width=20, bg="#2196F3", fg="white").pack(pady=5)
Button(root, text="Exit", command=root.quit, width=20, bg="#f44336", fg="white").pack(pady=5)

Label(root, text="Progress:", bg="#2c2c2c", fg="white").pack(pady=(15,5))
progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=400, mode='indeterminate')
progress_bar.pack(pady=5)

root.mainloop()
