import json
from cryptography.fernet import Fernet
import getpass
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

JSON_FILE = 'passwords.json'  # Name of the file where encrypted data will be stored

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

def change_info(key, data):
    """Option to change all information including passwords."""
    identifier = input("Enter the identifier of the password you want to change: ")
    if identifier not in data or identifier == "_master_password":
        print("No password found with this identifier or this identifier cannot be changed.")
        return

    # Get new information from the user
    new_username = input("Enter new username (leave blank if you don't want to change): ")
    new_password = getpass.getpass("Enter new password (leave blank if you don't want to change): ")
    new_description = input("Enter new description (leave blank if you don't want to change): ")

    # Update new information or keep the old one
    if new_username:
        data[identifier]["username"] = new_username
    if new_password:
        encrypted_new_password = encrypt_data(key, new_password)
        data[identifier]["password"] = encrypted_new_password
    if new_description:
        data[identifier]["description"] = new_description

    # Save the updated data
    save_data(key, data)
    print("Information updated successfully.")

def change_master_password(key, data):
    """Option to change the master password."""
    # Get the new master password
    new_master_password = getpass.getpass("Enter the new master password: ")
    new_key = generate_key(new_master_password)
    
    # Re-encrypt data with the new key
    new_data = {}
    for identifier, info in data.items():
        if identifier == "_master_password":
            # Encrypt the master password directly with the new key
            new_data["_master_password"] = encrypt_data(new_key, new_master_password)
        else:
            # Decrypt all other data with the old key and re-encrypt with the new key
            decrypted_password = decrypt_data(key, info['password'])
            new_data[identifier] = {
                "password": encrypt_data(new_key, decrypted_password),
                "description": info['description']
            }

    # Save the newly encrypted data to the file
    save_data(new_key, new_data)
    print("Master password changed successfully and all data re-encrypted.")

def main():
    # Check the existence and content of the JSON file
    if not os.path.exists(JSON_FILE) or os.path.getsize(JSON_FILE) == 0:
        # If the application is run for the first time, create a new master password
        master_password = getpass.getpass("Set the master password: ")
        key = generate_key(master_password)
        # Create an empty dictionary for the initial use and store the master password in it
        data = {"_master_password": encrypt_data(key, master_password)}
        save_data(key, data)  # Save the encrypted data to the file
        print("Master password successfully saved.")
    else:
        attempts_left = 3
        for attempt in range(3):  # Allow 3 attempts for entering the master password
            master_password = getpass.getpass("Enter the master password: ")
            key = generate_key(master_password)
            try:
                data = load_data(key)
                encrypted_master = data.get("_master_password")
                if encrypted_master and decrypt_data(key, encrypted_master) == master_password:
                    print("Master password verified.")
                    break
            except Exception as e:
                attempts_left -= 1
                print(f"Wrong password, attempts left = {attempts_left} ", e)
            if attempt == 2:  # If the last attempt is reached
                print("Three incorrect attempts made. Exiting the program.")
                return
        
    # Show the user menu after successful password verification
    while True:
        print("\n1. Add Password")
        print("2. List Passwords")
        print("3. Change Password")
        print("4. Change Master Password")
        print("5. Delete Password")
        print("6. Exit")
        choice = input("Your choice: ")

        if choice == "1":
            identifier = input("Identifier: ")
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            description = input("Description: ")
            data[identifier] = {"username": username, "password": encrypt_data(key, password), "description": description}
            save_data(key, data)
            print("Password added.")
        elif choice == "2":
            for identifier, info in data.items():
                if identifier != "_master_password":
                    print(f"Identifier: {identifier}, Username: {info['username']}, Password: {decrypt_data(key, info['password'])}, Description: {info['description']}")
        elif choice == "3":
            change_info(key, data)
        elif choice == "4":
            change_master_password(key, data)
        elif choice == "5":
            identifier = input("Identifier: ")
            if identifier in data and identifier != "_master_password":
                del data[identifier]
                save_data(key, data)
                print("Password deleted.")
            else:
                print("No password found with this identifier.")
        elif choice == "6":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()