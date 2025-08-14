"""
Ana Arayüz Modülü
Uygulama, saf arayüz olarak kullanılabilsin ve siyah ekran (komut istemi) görünmesin diye .pyw uzantısıyla kaydedildi
"""

from tkinter import *
import os

from keykeeper_windows import *

JSON_FILE = "passwords.json" #şifre dosyasının ismi

def checkJSON(): #passwords.json dosyasının varlığını ve boş olup olmadığını kontrol eder, yok ise veya boş ise False, aksi takdirde True döndürür
    if not os.path.exists(JSON_FILE) or os.path.getsize(JSON_FILE) == 0:
        return False
    else:
        return True

root = Tk()
root.title("Keykeeper 2.0") #Orijinal uygulamanın ismi 'Keykeeper' olduğu için Keykeeper 2.0 koydum😁
root.pack_propagate(False) #Arayüzün eklenen widget'lara göre boyut almasını önler
root.resizable(0,0) #Arayüzün kullanıcı tarafından mouse ile boyutlandırılmasını önler
root.geometry("250x450") #Arayüzun genişliği ve yüksekliği, yeterli olduğu için 250 pixele 450 pixel olarak ayarladım
root.configure(bg="#F5F5F5")
root.attributes('-alpha',0) #Ana uygulamanın en başta görünmemesi için uygulamanın opaklığını sıfır (0) yapar

MasterPasswordWindow(root,checkJSON()) #master passwordu oluşturup kontrol edecek modüllerimizin kullanacağı arayüz, bu arayüz burada uygulama ilk açıldığında çalışır
InterfaceTitle(root,"Keykeeper 2.0") #Ana uygulamanın başlığı
MainInterface(root) #Uygulamanın ana arayüzü

root.mainloop()