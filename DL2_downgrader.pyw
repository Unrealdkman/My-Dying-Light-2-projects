import subprocess
import sys
import os
import platform
import shutil
import tempfile

# Function to install required packages
def install_requirements():
    required_packages = [
        "tkinterdnd2",
        "steamctl",
        "pyunpack",
        "patool",
        "rarfile",
        "Tk"
    ]
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Error installing package: {package}")
            sys.exit(1)
# Install required packages before running the main script
install_requirements()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import zipfile
import pyunpack
import patoolib
import rarfile
import threading
import webbrowser
from distutils.dir_util import copy_tree
from pathlib import Path



# Get the current directory of the Python script
script_dir = os.path.dirname(os.path.realpath(__file__))
# Construct the full path to xdelta.exe in the same directory as the script
xdelta_path = os.path.join(script_dir, "xdelta.exe")
print(xdelta_path)

# Constants for file path storage
DOWNLOAD_PATH_FILE = "download_path.txt"




def apply_patch():
    # Ask the user to select a ZIP file
    zip_file = filedialog.askopenfilename(filetypes=[("ZIP Files", "*.zip")])

    if not zip_file:
        messagebox.showerror("Error", "No ZIP file selected.")
        return

    # Create a temporary directory to extract files
    extract_dir = os.path.join(os.path.dirname(zip_file), "extracted")
    os.makedirs(extract_dir, exist_ok=True)

    try:
        # Extract the ZIP file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Locate the text file with parameters (assuming the text file is inside the ZIP)
        txt_file = None
        for file in os.listdir(extract_dir):
            if file.endswith(".txt"):
                txt_file = os.path.join(extract_dir, file)
                break

        if not txt_file:
            messagebox.showerror("Error", "No text file found inside the ZIP.")
            return

        # Read the text file to get the paths
        with open(txt_file, 'r') as file:
            lines = file.readlines()

        if len(lines) % 3 != 0:
            messagebox.showerror("Error", "The text file is not formatted correctly. It should have multiples of 3 lines.")
            return

        # Loop through the lines in chunks of 3
        for i in range(0, len(lines), 3):
            block = [lines[i].strip(), lines[i+1].strip(), lines[i+2].strip()]

            # Extract and clean up the paths
            original_file = Path(download_path.get()) / block[0].split("=")[1].strip().lstrip('\\')
            patch_file = Path(txt_file).parent / block[1].split("=")[1].strip().lstrip('\\')
            output_file = Path(download_path.get()) / block[2].split("=")[1].strip().lstrip('\\')

            # Check if the necessary files exist if not then don't die just error msg
            if not os.path.isfile(original_file):
                messagebox.showerror("Error", f"Original file not found: {original_file}")
                return
            if not os.path.isfile(patch_file):
                messagebox.showerror("Error", f"Patch file not found: {patch_file}")
                return

            # Path to xdelta.exe
            xdelta_path = "xdelta.exe"

            # Run the xdelta patching process should work(does work)
            subprocess.run(
                [str(xdelta_path), "-d", "-f", "-s", str(original_file), str(patch_file), str(output_file)],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            messagebox.showinfo("Success", f"Patch applied successfully. Output saved to {output_file}")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to apply patch. Error: {e.stderr.decode()}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    finally:
        # Cleanup extracted files
        for root, dirs, files in os.walk(extract_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(extract_dir)


def open_nexus():
    webbrowser.open("https://www.nexusmods.com/dyinglight2/mods/1573")

def discord_link():
    webbrowser.open("https://discord.gg/R3DZMcpN8r")

# Function to detect Steam common folder
def find_steam_common_directory():
    steam_path = os.getenv('ProgramFiles(x86)', 'C:\\Program Files (x86)')
    default_common_path = os.path.join(steam_path, "Steam", "steamapps", "common")
    return default_common_path if os.path.exists(default_common_path) else ""

# Load saved download path from file
def load_download_path():
    if os.path.exists(DOWNLOAD_PATH_FILE):
        with open(DOWNLOAD_PATH_FILE, 'r') as file:
            return file.read().strip()
    return ""

# Save download path to file
def save_download_path(path):
    with open(DOWNLOAD_PATH_FILE, 'w') as file:
        file.write(path)

# GUI to select source folder
def select_folder(variable, title):
    selected_path = filedialog.askdirectory(title=title)
    if selected_path:
        variable.set(selected_path)
        if variable == download_path:
            save_download_path(selected_path)

def perform_link_creation():
    source_dir = download_path.get()  # Use the download path as the source directory
    link_dir = link_var.get()

    if source_dir and link_dir:
        common_folder = os.path.join(link_dir, os.path.basename(source_dir))
        create_junction_link(source_dir, common_folder)
        messagebox.showinfo("Junction Link Created", f"Link created at {common_folder}")
    else:
        messagebox.showerror("Error", "Please select both source(download) directory and link directory.")

def download_depot(command):
    if not download_path.get():
        messagebox.showerror("Error", "Download path is not set. Please set a valid download path.")
        return
    subprocess.Popen(['cmd.exe', '/K', command])

# Download depot functions
def download_depot1():
    command = f'steamctl depot download --app 534380 --depot 534381 --manifest 8397059556255747146 -o {download_path.get()}'
    download_depot(command)

def download_depot2():
    command = f'steamctl depot download --app 534380 --depot 534382 --manifest 2610088083322243488 -o {download_path.get()}'
    download_depot(command)

def download_depot3():
    command = f'steamctl depot download --app 534380 --depot 534383 --manifest 6553645018477200440 -o {download_path.get()}'
    download_depot(command)

def download_depot4():
    command = f'steamctl depot download --app 534380 --depot 534384 --manifest 3809152703080297962 -o {download_path.get()}'
    download_depot(command)

def download_depot5():
    command = f'steamctl depot download --app 534380 --depot 534385 --manifest 8328607143729447236 -o {download_path.get()}'
    download_depot(command)

def apply_patch1():
    target_path = os.path.join(download_path.get(), 'ph', 'work', 'bin', 'x64')
    os.makedirs(target_path, exist_ok=True)  # Ensure the directory exists
    steam_appid_path = os.path.join(target_path, 'steam_appid.txt')
    try:
        with open(steam_appid_path, 'w') as file:
            file.write("534380")
        messagebox.showinfo("Patch Applied", f"'steam_appid.txt' created at: {steam_appid_path}")
        print(f"'steam_appid.txt' successfully created at: {steam_appid_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create 'steam_appid.txt': {e}")
        print(f"Error creating 'steam_appid.txt': {e}")


def rename_nvngx_dlss():
    # Define the directory where the search will occur
    x64_dir = os.path.join(download_path.get(), "ph", "work", "bin", "x64")
    print(x64_dir)
    # Define the filename you're looking for
    target_file = "nvngx_dlss.dll"

    # Search for the file in the directory
    file_path = os.path.join(x64_dir, target_file)

    # Check if the file exists and is indeed a file (not a directory)
    if os.path.isfile(file_path):
        # Create the new file name
        new_file_path = file_path + "1"

        # Rename the file
        os.rename(file_path, new_file_path)
        print(f"File renamed to: {new_file_path}")
    else:
        print(f"File '{target_file}' not found in {x64_dir} or it's not a file.")

def select_temp_folder():
    selected_path = filedialog.askdirectory(title="Select Temporary Archive Folder")
    if selected_path:
        temp_archive_path.set(selected_path)

# Function to get ZIP or RAR file size before extraction
def get_archive_size(archive_file):
    try:
        if archive_file.lower().endswith(".zip"):
            with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                size = sum(zinfo.file_size for zinfo in zip_ref.infolist())
        elif archive_file.lower().endswith(".rar"):
            with rarfile.RarFile(archive_file) as rar_ref:
                size = sum(info.file_size for info in rar_ref.infolist())
        else:
            raise ValueError("Unsupported file type")
        return size
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get archive size: {e}")
        return 0

# Function to display the initial information window
def show_initial_message():
    messagebox.showinfo("Extraction in Progress", "Extraction may take several minutes. You will receive a confirmation window when it is done.\nPlease be patient much love from: Idkman")


def extract_and_move(archive_file):
    # Show the initial information message box
    show_initial_message()

    # Disable the extract button to prevent multiple clicks during extraction
    extract_button.config(state=tk.DISABLED)

    def move_and_copy(src, dest):
        # Print out the source and destination paths directly after assignment
        for item in os.listdir(src):
            s_item = os.path.join(src, item)
            d_item = os.path.join(dest, item)

            # Print the source and destination paths
            print(f"Source: {s_item}")
            print(f"Destination: {d_item}")

            if os.path.isdir(s_item):
                print(f"Folder: {s_item} to {d_item}")
                shutil.copytree(s_item, d_item, dirs_exist_ok=True)  # Copy and overwrite folders
            else:
                file_size = os.path.getsize(s_item)  # Get the file size
                print(f"File: {s_item} to {d_item} | Size: {file_size} bytes")
                shutil.copy2(s_item, d_item)  # Copy and overwrite files

    def run_extraction():
        temp_folder = temp_archive_path.get()  # Use the selected temporary folder
        if not temp_folder:
            messagebox.showerror("Error", "Please select a temporary folder to extract the archive.")
            return

        os.makedirs(temp_folder, exist_ok=True)

        try:
            # Extract the archive into the temp folder
            patoolib.extract_archive(archive_file, outdir=temp_folder)

            target_folders = {"ph", "engine", "games"}
            for root, dirs, files in os.walk(temp_folder):
                for folder_name in dirs:
                    if folder_name in target_folders:
                        src_folder = os.path.join(root, folder_name)
                        dst_folder = os.path.join(download_path.get(), folder_name)

                        # If the destination folder doesn't exist, create it
                        if not os.path.exists(dst_folder):
                            os.makedirs(dst_folder)

                        # Move and copy the contents
                        move_and_copy(src_folder, dst_folder)
                        print(f"Moved and copied contents from {src_folder} to {dst_folder}")

            messagebox.showinfo("Extraction Complete", "The archive has been successfully extracted and moved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract and move: {e}")
        finally:
            if os.path.exists(temp_folder):
                print(f"Temporary folder kept at: {temp_folder}")

    # Start the extraction in a separate thread
    extraction_thread = threading.Thread(target=run_extraction, daemon=True)
    extraction_thread.start()

# Function to select the archive file
def select_archive():
    archive_file = filedialog.askopenfilename(title="Select Archive File", filetypes=[("Archive files", "*.zip;*.rar")])
    if archive_file:
        archive_name_label.config(text=f"Selected File: {os.path.basename(archive_file)}")
        size = get_archive_size(archive_file)
        size_label.config(text=f"Archive Size: {size / (1024 * 1024):.2f} MB")
        extract_button.config(state=tk.NORMAL, command=lambda: extract_and_move(archive_file))


# Function to show console output
def show_console_window():
    messagebox.showinfo("Developer only", "To use this function, rename the file extension to .py")
    console_window = tk.Toplevel(root)
    console_window.title("Console Output")
    console_window.geometry("700x300")

    # Create a scrollable text widget for console output
    console_text = tk.Text(console_window, wrap=tk.WORD, height=15, width=80)
    console_text.pack(padx=10, pady=10)
    # Redirect print statements to the console text widget
    def write_console_output(text):
        console_text.insert(tk.END, text + '\n')
        console_text.yview(tk.END)  # Scroll to the end

    # Redirect standard output to our console window
    sys.stdout.write = write_console_output
    sys.stderr.write = write_console_output

    # Example usage: print some debug information
    print("Console window for debugging.")
    print("This is where logs will appear.")

# Function to show citation of dependencies
def show_cite():
    dependencies = """Dependencies Used:
- tkinterdnd2: https://github.com/ParthJadhav/TkinterDnD2
- steamctl: https://github.com/burakkaygusuz/steamctl
- pyunpack: https://github.com/mik3y/pyunpack
- patool: https://github.com/wummel/patool
- rarfile: https://github.com/techtonik/rarfile"""

    messagebox.showinfo("Cite", dependencies)


# Function to show "Made By" information
def show_made_by():
    made_by_text = """Made by:Idkman
For more information or support contact me on discord
or email me at dev.idkman@gmail.com
"""
    messagebox.showinfo("Made By", made_by_text)


def show_tutorial():
    tutorial_text = """
 1. Set a download path where you want your game to be located

 2. Download the depots, in order, a command line window will open up, it will ask for your steam credentials
 (You have to own Dying Light 2 to download the depots)

 3. Download the E3 Definitive mod here (https://www.nexusmods.com/dyinglight2/mods/1573)
 Download both the base 20GB zip, and the patch

 4. Click on "Select Archive File", first select the 20GB zip, wait a few minutes as this
 will extract the zip to a temporary folder, and will overwrite some files

 5. Do the same but now with the patch, again wait a few minutes
    
 YOU WILL GET A CONFIRMATION WINDOW WHEN THE EXTRACTION AND MOVING HAS COMPLETED
    
 Steam is required to run the game:
 1. Run the "Steam appid fix"
 2. Add the game to steam

 If you have an RTX card:
 1. Run the "Nvidia RTX card fix"
 
    """

    # Create a custom message box with larger width
    tutorial_window = tk.Toplevel(root)
    tutorial_window.title("Tutorial")
    # Set a custom size for the message box (width and height)
    label = ttk.Label(tutorial_window, text=tutorial_text, wraplength=750)
    link_label.pack(padx=5, pady=5)
    label.pack(padx=5, pady=5)

    # Center the message box
    tutorial_window.grab_set()  # Make the window modal (focus is on the new window)
    tutorial_window.update_idletasks()  # Update the window size based on the content
    tutorial_window.geometry(f"{tutorial_window.winfo_width()}x{tutorial_window.winfo_height()}")
    tutorial_window.resizable(False, False)

    tutorial_window.mainloop()


# Function to create the toolbar
def create_toolbar():
    toolbar = ttk.Frame(root)
    toolbar.pack(side=tk.TOP, fill=tk.X, padx=(1,5), pady=5)

    help_button = ttk.Button(toolbar, text="Help", command=lambda: show_console_window(), width=21)
    help_button.grid(row=0, column=0, padx=5)

    cite_button = ttk.Button(toolbar, text="Cite", command=show_cite, width=21)
    cite_button.grid(row=0, column=1, padx=5)

    made_by_button = ttk.Button(toolbar, text="Made By", command=show_made_by, width=21)
    made_by_button.grid(row=0, column=2, padx=5)

    tutorial_button = ttk.Button(toolbar, text="How to downgrade", command=show_tutorial, width=21)
    tutorial_button.grid(row=0, column=3, padx=5)

    open_nexus_button = ttk.Button(toolbar, text="Nexus Mods Page", command=open_nexus, width=21)
    open_nexus_button.grid(row=0, column=4, padx=5)

    discord_link_button = ttk.Button(toolbar, text="Discord Server", command=discord_link, width=21)
    discord_link_button.grid(row=0, column=5, padx=5)



# Main GUI setup
root = TkinterDnD.Tk()
root.title('Dying Light 2 Downgrader')
root.geometry('1050x760')
root.configure(bg="#f5f5f5")
root.resizable(False, False)
# Create the toolbar
create_toolbar()
temp_archive_path = tk.StringVar(value="")
style = ttk.Style()
style.theme_use('clam')
style.configure("TLabel", font=("Arial", 11), anchor="w")
style.configure("TButton", font=("Arial", 10), padding=6, relief="flat", background="#333333", foreground="white", width=25)
style.configure("TEntry", padding=4, relief="flat")

# Simulate transparent button background using background color with 20% opacity effect (RGBA)
style.map("TButton", background=[('active', '#555555'), ('!active', '#444444')])

link_var = tk.StringVar(value=find_steam_common_directory())
download_path = tk.StringVar(value=load_download_path())

# Main frame to hold all sections (Steam Common Directory at top, others side by side)
main_frame = ttk.Frame(root, padding=20, relief="solid", borderwidth=1)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Steam Common Directory and Download Path Section
frame1 = ttk.Frame(main_frame, padding=20)
frame1.pack(fill="x", padx=10, pady=5)

# Left Frame for Steam Common Directory
left_frame = ttk.Frame(frame1)
left_frame.pack(side="left", padx=10, pady=5, fill="y")

link_label = ttk.Label(left_frame, text="Steam Common Directory: ", font=("Arial", 15, "bold"), width=22)
link_label.pack(anchor="center", pady=5)

link_entry = ttk.Entry(left_frame, textvariable=link_var, width=50, foreground="black")
link_entry.pack(pady=5)

link_button = ttk.Button(left_frame, text="Browse:", command=lambda: select_folder(link_var, "Select Steam Common Directory"))
link_button.pack(pady=5)

create_link_button = ttk.Button(left_frame, text="Create Junction Link: ", command=perform_link_creation)
create_link_button.pack(pady=20)

# Right Frame for Download Path
right_frame = ttk.Frame(frame1)
right_frame.pack(side="right", padx=10, pady=5, fill="y")

download_path_label = ttk.Label(right_frame, text="Download Path: ", font=("Arial", 15, "bold"), width=15)
download_path_label.pack(anchor="center", pady=5)

download_path_entry = ttk.Entry(right_frame, textvariable=download_path, width=50, foreground="black")
download_path_entry.pack(anchor="center",pady=5)

download_path_button = ttk.Button(right_frame, text="Set Download Path:", command=lambda: select_folder(download_path, "Select Download Path"))
download_path_button.pack(anchor="center", pady=5)

# Depot Downloading Buttons
depot_buttons = [
    ("Download Depot 1", download_depot1),
    ("Download Depot 2", download_depot2),
    ("Download Depot 3", download_depot3),
    ("Download Depot 4", download_depot4),
    ("Download Depot 5", download_depot5)
]

# Create a new frame to hold depot buttons on the left
frame_depot = ttk.Frame(main_frame, padding=20)
frame_depot.pack(side="left", fill="y", padx=20)

# Title for Download Depot Section (centered at the top of the left frame)
download_depot_label = ttk.Label(frame_depot, text="Download Depots: ", font=("Arial", 15, "bold"), foreground="black")
download_depot_label.pack(anchor="center", pady=5)

# Add the Download Depot buttons to the left frame
for button_text, command in depot_buttons:
    ttk.Button(frame_depot, text=button_text, command=command).pack(pady=5)

# Middle frame for Apply Patches Section (frame2)
frame2 = ttk.Frame(main_frame, padding=20)
frame2.pack(side="left", fill="y", expand=True, padx=40)  # Adjusted to shift it more to the center

# Title for Apply Patches Section (centered at the top of the middle frame)
apply_patches_label = ttk.Label(frame2, text="Apply Fixes: ", font=("Arial", 15 ,"bold"), foreground="black")
apply_patches_label.pack(anchor="center", pady=5)

# Buttons for Apply Patches
apply_patch_buttons = [
    ("Steam appid fix", apply_patch1),
    ("Nvidia RTX card fix", rename_nvngx_dlss)
]

for button_text, command in apply_patch_buttons:
    ttk.Button(frame2, text=button_text, command=command).pack(pady=5)

# Right frame for Extract Archive Section (frame3)
frame3 = ttk.Frame(main_frame, padding=20)
frame3.pack(side="left", fill="y", padx=60)  # Adjusted to push this section more to the right

# Title for Extract Archive Section (centered at the top of the right frame)
extract_label = ttk.Label(frame3, text="Extract Archive: ", font=("Arial", 15, "bold"), foreground="black")
extract_label.pack(anchor="center", pady=5)

# Archive section buttons
archive_name_label = ttk.Label(frame3, text="Selected File: ")
archive_name_label.pack(pady=5)

size_label = ttk.Label(frame3, text="Archive Size: ")
size_label.pack(anchor="center",pady=5)

select_zip_button = ttk.Button(frame3, text="Select Archive File", command=select_archive)
select_zip_button.pack(anchor="center",pady=10)

temp_folder_label = ttk.Label(frame3, text="Temporary Folder:", font=("Arial", 15, "bold"))
temp_folder_label.pack(anchor="center", pady = 10)

# Entry to display the selected folder path
temp_folder_entry = ttk.Entry(frame3, textvariable=temp_archive_path, width=50, foreground="black")
temp_folder_entry.pack(pady=5)

# Button to select temporary folder
temp_folder_button = ttk.Button(frame3, text="Set Temporary Archive Folder", command=select_temp_folder)
temp_folder_button.pack(pady=5)

# Button for the patch button crazy right? yeah I lost all my common sense
patch_button = ttk.Button(frame2, text="Apply Patch", command=apply_patch)
patch_button.pack(pady=20)

extract_button = ttk.Button(frame3, text="Extract Archive File", state=tk.DISABLED)
extract_button.pack(anchor="center",pady=20)
root.mainloop()
