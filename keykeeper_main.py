"""
Arayüz tarafından kullanılabilmesi için orijinal uygulama metodlara ayrıldı.
generate_key'den save_data'ya kadar olan metodları hiçbir değişiklik yapmadan orijinal uygulamadan aldım. Düzenleme yaptığım ve eklediğim yeni yerler çift yorumla (##) belirtilecektir.
"""

import json
from cryptography.fernet import Fernet
# import getpass
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

JSON_FILE = 'passwords.json'  # Name of the file where encrypted data will be stored
MASTER_PASSWORD = None #Mevcut anahtar şifre uygulama çalıştığı esnada bir global değişkende tutulur

def return_key(): ##Arayüzde kullanılması için mevcut master şifre ile oluşturulan anahtarı döner
    return generate_key(MASTER_PASSWORD)

def generate_key(password_provided):
    password = password_provided.encode()  # Convert the password to bytes
    salt = b'salt_'  # Salt value, ideally should be random for security
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),  # Using SHA256 as the hashing algorithm
        length=32,  # Length of the derived key in bytes
        salt=salt,  # Salt value
        iterations=100000,  # Number of iterations used for key derivation
        backend=default_backend()  # Backend used for cryptographic operations
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))  # Derive the key and encode it using base64
    return key

def encrypt_data(key, data):
    """Encrypts the data."""
    fernet = Fernet(key)  # Create an instance of the Fernet class for encryption
    encrypted_data = fernet.encrypt(data.encode())  # Encrypt the data
    return encrypted_data.decode()  # Convert the encrypted data to a decryptable format

def decrypt_data(key, encrypted_data):
    """Decrypts the encrypted data."""
    fernet = Fernet(key)  # Create an instance of the Fernet class for decryption
    decrypted_data = fernet.decrypt(encrypted_data.encode())  # Decrypt the encrypted data
    return decrypted_data.decode()  # Convert the decrypted data to string format

def load_data(key):
    """Loads and decrypts data from the JSON file."""
    if os.path.exists(JSON_FILE):  # Check if the file exists
        with open(JSON_FILE, 'r') as file:  # Open the file in read mode
            encrypted_data = file.read()  # Read the encrypted data
        data = decrypt_data(key, encrypted_data)  # Decrypt the encrypted data
        return json.loads(data)  # Convert from JSON format to Python object
    else:
        return {}  # Return an empty dictionary if the file doesn't exist

def save_data(key, data):
    """Encrypts and saves the data to the JSON file."""
    encrypted_data = encrypt_data(key, json.dumps(data))  # Encrypt the data and convert to JSON format
    with open(JSON_FILE, 'w') as file:  # Open the file in write mode
        file.write(encrypted_data)  # Write the encrypted data to the file

def save_master_password(master_password): ##Kodu genel olarak orijinal uygulamadan alınan yeni master şifre kaydetme kodu
    global MASTER_PASSWORD
    key = generate_key(master_password)
    data = {"_master_password": encrypt_data(key, master_password)}
    MASTER_PASSWORD = master_password
    save_data(key, data)
    pass

def verify_master_password(master_password): ##Kodu genel olarak orijinal uygulamadan alınan yeni master şifre doğrulama kodu
    global MASTER_PASSWORD
    key = generate_key(master_password)
    data = load_data(key)
    encrypted_master = data.get("_master_password")
    MASTER_PASSWORD = master_password
    if encrypted_master and decrypt_data(key, encrypted_master) == master_password:
        return True
    else:
        return False

def add_password(identifier,username,password,description): ##Şifre bilgilerine kullanıcı adı da ekleyerek şifreyi veritabanına kaydeden yeni kayıt metodu
    key = generate_key(MASTER_PASSWORD)
    data = load_data(key)
    encrypted_password = encrypt_data(key, password)
    data[identifier] = {
        "username": username,
        "password": encrypted_password,
        "description": description
    }
    save_data(key, data)

def get_passwords(): ##Bütün şifre bilgilerini dönen metod (şifre listelemede kullanılır)
    key = generate_key(MASTER_PASSWORD)
    data = load_data(key)
    return data

def change_password(identifier,username,password,description): ##Şifre bilgileri değiştirme kodu
    key = generate_key(MASTER_PASSWORD)
    data = load_data(key)
    if username and len(username) > 3:
        data[identifier]["username"] = username
    if password and len(password) > 3:
        encrypted_password = encrypt_data(key, password)
        data[identifier]["password"] = encrypted_password
    if description and len(description) > 3:
        data[identifier]["description"] = description
    save_data(key, data)

def change_master_password(new_master_password): ##Master şifre değiştirme ve mevcut şifreleri yeniden şifreleme kodu
    global MASTER_PASSWORD
    old_key = generate_key(MASTER_PASSWORD)
    new_key = generate_key(new_master_password)
    data = load_data(old_key)
    new_data = {}
    for identifier, info in data.items():
        if identifier == "_master_password":
            # Encrypt the master password directly with the new key
            new_data["_master_password"] = encrypt_data(new_key, new_master_password)
        else:
            # Decrypt all other data with the old key and re-encrypt with the new key
            decrypted_password = decrypt_data(old_key, info['password'])
            new_data[identifier] = {
                "username": info['username'], ##Bir önceki uygulamanın kayıtlarında mevcut olmayan username (kullanıcı adı) değişkeni de eklendi
                "password": encrypt_data(new_key, decrypted_password),
                "description": info['description']
            }

    # Save the newly encrypted data to the file
    save_data(new_key, new_data)
    MASTER_PASSWORD = new_master_password

def delete_password(identifier): ##Şifre silme komutu
    key = generate_key(MASTER_PASSWORD)
    data = load_data(key)
    if identifier in data:
        del data[identifier] ##Python'daki yerleşik "del" obje silme komutu kullanıldı
        save_data(key, data)