import winreg
import os
import zipfile
import wget
import sys
import subprocess

def check_chromedriver():
    key_path = r"Software\Google\Chrome\BLBeacon"
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
    chromeVersion = winreg.QueryValueEx(key, "version")[0]
    print(f"Bilgisayarınızdaki güncel Chrome sürümü: {chromeVersion}...")
    print("Chrome Driver kontrol ediliyor...")
    try:
        result = subprocess.check_output(["driver/chromedriver.exe", "--version"], stderr=subprocess.STDOUT, text=True)
        version = result.split()[1]
        if version == chromeVersion:
            print("Chrome Driver güncel.")
        else:
            print("Chrome Driver güncel değil...")
            install_chromedriver(chromeVersion)
    except subprocess.CalledProcessError as e:
        print("Chrome Driver bulunamadı...")
        install_chromedriver(chromeVersion)
    except FileNotFoundError:
        print("Chrome Driver bulunamadı... Yükleniyor...")
        install_chromedriver(chromeVersion)

def install_chromedriver(chromeVersion):
    print(f'Chrome Driver sürüm {chromeVersion} indiriliyor...')

    scriptPath = os.path.dirname(__file__)
    driverPath = f'https://storage.googleapis.com/chrome-for-testing-public/{chromeVersion}/win64/chromedriver-win64.zip'
    wget.download(driverPath, out="driver.zip")
    print("\nArşiv çıkarılıyor..\n")
    with zipfile.ZipFile('driver.zip', 'r') as archive:
        archive.extract("chromedriver-win64/chromedriver.exe", scriptPath + "\\driver")
        os.rename(os.path.join("driver", "chromedriver-win64", "chromedriver.exe"), os.path.join("driver", "chromedriver.exe"))
        os.rmdir(os.path.join("driver", "chromedriver-win64"))
    os.remove('driver.zip')
    print("Sürücü başarıyla indirilip çıkarıldı!")