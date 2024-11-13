def install_package(package):
    """using pip I install a shit ton of dependency cause I can't code for shit"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def install_dependencies():
    """if installed then don't bother, I still have to upgrade this cause pillow upgrades every time"""
    packages = ["psutil", "pystray", "pillow"]
    for package in packages:
        try:
            __import__(package)
            print(f"{package} is already installed.")
        except ImportError:
            print(f"Installing {package}...")
            install_package(package)

if __name__ == "__main__":
    install_dependencies()