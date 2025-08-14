import subprocess

def check_package(package_name):
    try:
        subprocess.check_output(["pip","show",package_name])
        print(f"Package {package_name} is already installed.")
    except subprocess.CalledProcessError:
        print(f"Package {package_name} not found. Currently installing...")
        install_package(package_name)

def install_package(package_name):
    subprocess.check_output(["pip","install",package_name])
