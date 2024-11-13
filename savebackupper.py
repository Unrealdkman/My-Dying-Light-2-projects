import subprocess
import sys
import psutil
import shutil
import time
import os
from datetime import datetime
import pystray
from pystray import MenuItem as item
from PIL import Image
import threading
# Function to check if the script is running with admin privileges
# Function to add the script to Task Scheduler (to run with admin rights)
def add_to_task_scheduler():
    """Add the script to the Windows Task Scheduler to run at startup with admin rights."""
    # Get the script path
    script_path = os.path.abspath(sys.argv[0])

    # The task name
    task_name = "DyingLightSaveBackupper"

    # Command to run the Python script with admin rights
    python_exe = sys.executable

    # Create the task using schtasks (Windows Task Scheduler)
    command = [
        "schtasks", "/Create", "/TN", task_name, "/TR", f'"{python_exe}" "{script_path}"',
        "/SC", "ONSTART", "/RL", "HIGHEST", "/F"
    ]

    try:
        # Execute the command to create the task
        subprocess.run(command, check=True)
        print(f"Successfully added to Task Scheduler. The script will run at startup with admin rights.")
    except subprocess.CalledProcessError as e:
        print(f"Error adding to Task Scheduler: {e}")


# Ensure required packages are installed



# Export registry key to steamsession.reg
def export_steam_registry():
    """exporting the ActiveProcess registry key to steamsession.reg. thank you eric based as fuck guy"""
    try:
        subprocess.run('reg export HKCU\\Software\\Valve\\Steam\\ActiveProcess steamsession.reg /y',
                       shell=True, check=True)
        print("Registry key exported successfully to steamsession.reg.")
    except subprocess.CalledProcessError as e:
        print(f"Error exporting registry key: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Extract Steam ID from the exported registry file
def extract_steam_id_from_file():
    """extract the value after the colon"""
    try:
        with open('steamsession.reg', 'r', encoding='utf-16') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()

            if '"ActiveUser"=dword:' in line:
                steam_id_hex = line.split('dword:')[1].strip()
                print(f"Found Steam ID (hex): {steam_id_hex}")

                try:
                    steam_id_decimal = int(steam_id_hex, 16)
                    print(f"Steam ID (decimal): {steam_id_decimal}")
                    return steam_id_decimal
                except ValueError:
                    print(f"Error converting {steam_id_hex} to decimal.")
                    return None

        print("No 'ActiveUser' line found in steamsession.reg.")
        return None

    except FileNotFoundError:
        print('steamsession.reg file not found.')
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# backup files from the source folder to an incrementally named folder basically save1, save2 so on and so forth
def backup_file(source_folder, backup_folder):
    # next available backup folder name
    i = 1
    while os.path.exists(os.path.join(backup_folder, f"save{i}")):
        i += 1

    # create
    new_backup_folder = os.path.join(backup_folder, f"save{i}")
    os.makedirs(new_backup_folder)
    print(f"Created new backup folder: {new_backup_folder}")

    # copy files
    save_files = os.listdir(source_folder)
    for save_file in save_files:
        source_file = os.path.join(source_folder, save_file)
        if os.path.isfile(source_file):
            backup_file_path = os.path.join(new_backup_folder, save_file)
            shutil.copy(source_file, backup_file_path)
            print(f"Backup created for {save_file} at {backup_file_path}")


# whether the game runs (the exe)
def check_process(executable_name):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == executable_name:
            return True
    return False


def monitor_game(executable_name, source_folder, backup_folder):
    """monitoring stuff, if the game closed thus  triggering a backup on closure."""
    game_was_running = False

    while True:
        game_is_running = check_process(executable_name)

        if game_is_running:
            game_was_running = True
            print("Game has started running.")

        elif game_was_running and not game_is_running:
            print("Game has closed. Backing up files...")
            backup_file(source_folder, backup_folder)
            game_was_running = False

        time.sleep(20)


def setup_tray_icon(source_folder, backup_folder):
    """creating a system tray icon might add a hand drawn icon but I'm fucking tired"""
    icon_image = Image.new("RGB", (64, 64), "blue")
    icon = pystray.Icon("backup_monitor", icon_image, menu=pystray.Menu(
        item('Backup Now', lambda icon, item: backup_file(source_folder, backup_folder)),
        item('Exit', lambda icon, item: icon.stop())
    ))
    icon.run()


def open_save_path(userid, steam_path):
    """getting the save path using the userid got from the reg file."""
    if userid:
        save_path = os.path.join(steam_path, "userdata", str(userid), "534380", "remote", "out", "save")

        if os.path.exists(save_path):
            print(f"Save path found: {save_path}")
            subprocess.run(f'explorer "{save_path}"')
        else:
            print(f"Save path does not exist: {save_path}")
    else:
        print("No userid found, cannot open the save path.")


# registering the program to run at startup
def add_to_startup():
    script_path = sys.argv[0]
    startup_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    reg_command = f'reg add "HKCU\\{startup_key}" /v "GameBackup" /t REG_SZ /d "{script_path}" /f'

    try:
        subprocess.run(reg_command, shell=True, check=True)
        print("Added to startup successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error adding to startup: {e}")


# main program
if __name__ == "__main__":

    export_steam_registry()
    userid = extract_steam_id_from_file()

    if not userid:
        print("Failed to obtain Steam ID.")
        sys.exit(1)

    # define the paths for the source folder and Steam path using the extracted userid
    steam_path = r"C:\Program Files (x86)\Steam"
    source_folder = r"C:\Program Files (x86)\Steam\userdata\{userid}\534380\remote\out\save"

    # create a backup folder in the script directory
    backup_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Backup")
    os.makedirs(backup_folder, exist_ok=True)

    # modify source folder to include the dynamic userid
    source_folder = source_folder.format(userid=userid)

    add_to_task_scheduler()
    #self explanitory
    add_to_startup()

    # start monitoring game and tray icon
    executable_name = "DyingLightGame_x64_rwdi.exe"  # Replace with your game's executable name
    threading.Thread(target=monitor_game, args=(executable_name, source_folder, backup_folder)).start()
    setup_tray_icon(source_folder, backup_folder)

    print(f"Monitoring the game: {executable_name}")
