import os
from cryptography.fernet import Fernet
from pathlib import Path


class SecurityManager:
    def __init__(self, key=None):
        #Initialization of the encrypter
        #Logic to handle empty or missing ENCRYPTION_KEY
        if key and len(key.strip()) > 0:
            self.key = key.encode() if isinstance(key, str) else key
            print("Security: Using existing encryption key from .env")
        else:
            print("Security: No key found in .env. Generating and persisting a new one...")
            self.key = Fernet.generate_key()
            self._save_key_to_env(self.key.decode())

        self.cipher = Fernet(self.key)

    def _save_key_to_env(self, key_string):

        # Handles missing, empty, or filled ENCRYPTION_KEY in .env.
        env_path = Path(__file__).resolve().parent.parent / ".env"

        if not env_path.exists():
            with open(env_path, "w") as f:
                f.write(f"ENCRYPTION_KEY={key_string}\n")
            return

        with open(env_path, "r") as f:
            lines = f.readlines()

        key_found = False
        new_lines = []

        for line in lines:
            # Check if this line is the encryption key
            if line.strip().startswith("ENCRYPTION_KEY"):
                key_found = True
                parts = line.split("=", 1)
                # If there's nothing after '=' or it's just whitespace, update it
                if len(parts) == 1 or not parts[1].strip():
                    new_lines.append(f"ENCRYPTION_KEY={key_string}\n")
                else:
                    # Key already exists and is not empty, keep it
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # If the variable wasn't in the file at all, append it
        if not key_found:
            new_lines.append(f"\nENCRYPTION_KEY={key_string}\n")

        # Write the cleaned/updated content back to .env
        with open(env_path, "w") as f:
            f.writelines(new_lines)

    def _setup_directories(self, base_path):

        encrypted_dir = base_path / "encrypted"
        decrypted_dir = base_path / "decrypted"

        encrypted_dir.mkdir(exist_ok=True)
        decrypted_dir.mkdir(exist_ok=True)

        return encrypted_dir, decrypted_dir

    def encrypt_file(self, file_path):
        path = Path(file_path).resolve()
        if not path.exists():
            print(f"Security Error: File {path} not found for encryption.")
            return None

        # 1. Prepare sub-directories
        encrypted_dir, _ = self._setup_directories(path.parent)

        # 2. Read the raw CSV data
        with open(path, "rb") as f:
            file_data = f.read()

        # 3. Encrypt the data
        encrypted_data = self.cipher.encrypt(file_data)

        # 4. Save to 'encrypted' folder with .enc extension
        encrypted_file_path = encrypted_dir / f"{path.name}.enc"
        with open(encrypted_file_path, "wb") as f:
            f.write(encrypted_data)

        # 5. Remove the original plain-text CSV
        os.remove(path)
        print(f"Security: File locked at {encrypted_file_path.relative_to(path.parent.parent)}")
        return encrypted_file_path

    def decrypt_file(self, encrypted_file_path):
        """
        Restores the file and moves it to the 'decrypted' sub-directory.
        """
        path = Path(encrypted_file_path).resolve()
        if not path.exists():
            print(f"Security Error: Encrypted file {path} not found.")
            return None

        # 1. Prepare sub-directories
        _, decrypted_dir = self._setup_directories(path.parent.parent)

        # 2. Read and Decrypt
        with open(path, "rb") as f:
            encrypted_data = f.read()

        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
        except Exception as e:
            print(f"Security Error: Decryption failed. Key might be incorrect. {e}")
            return None

        # 3. Save to 'decrypted' folder
        original_filename = path.name.replace(".enc", "")
        decrypted_file_path = decrypted_dir / original_filename

        with open(decrypted_file_path, "wb") as f:
            f.write(decrypted_data)

        print(f"Security: File restored at {decrypted_file_path.relative_to(path.parent.parent.parent)}")
        return decrypted_file_path