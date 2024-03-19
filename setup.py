import subprocess
import sys

required_packages = [
    'coloredlogs',
    'emoji',
    'colorama',
    'wikipedia',
    'pyfiglet',
    'pyjokes',
]

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == '__main__':
    for package in required_packages:
        install(package)
    print("\nAll required packages have been installed\n")