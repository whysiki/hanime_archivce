import argparse
import logging
from cryptography.fernet import Fernet
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from os import path, urandom
import uuid

ENCRYPTION = "en"
DECRYPTION = "de"
GENRATE_KEY_FILE = "gen"

ACTION_DICT = {
    ENCRYPTION: "encyption",
    DECRYPTION: "decyption",
    GENRATE_KEY_FILE: "generate key file",
}


def ensure_file_exists(file_path: str) -> Path:
    filepath: Path = Path(file_path)
    if not filepath.exists():
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.touch(exist_ok=True)
    return filepath


def generate_unique_identifier(input_string):

    # 定义一个命名空间UUID
    namespace_uuid = uuid.UUID("1b671a64-40d5-491e-99b0-da01ff1f3341")

    # 使用uuid5()函数生成唯一标识符
    unique_identifier = uuid.uuid5(namespace_uuid, input_string)

    return str(unique_identifier)


def generate_key(password, salt_random=False):
    """
    Generate a key based on the provided password.

    Args:
        password (str): The password to generate the key from.

    Returns:
        bytes: The generated key.

    """
    if isinstance(password, str):
        password = password.encode()

    salt = bytes(f"{password}", "utf-8") if not salt_random else urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def get_key_from_file(key_file_path: str) -> bytes:
    """
    Get the key from a file.

    Args:
        key_file_path (str): The path to the key file.

    Returns:
        bytes: The key.
    """
    assert Path(
        key_file_path
    ).exists(), f"key_file_path: {key_file_path} does not exist!"
    with open(key_file_path, "rb") as f:
        key = f.read()
    assert key, "Key is empty!"
    return key


def encrypt_file(file_path, key, to_file=True, to_return=False):
    """
    Encrypts the contents of a file using the provided key.

    Args:
        file_path (str): The path to the file to be encrypted.
        key (bytes): The encryption key.
        to_file (bool, optional): Whether to save the encrypted data to a file. Defaults to True.
        to_return (bool, optional): Whether to return the encrypted data. Defaults to False.

    Returns:
        bytes or None: The encrypted data if `to_return` is True, otherwise None.
    """
    assert Path(file_path).exists(), f"file_path: {file_path} does not exist!"
    with open(file_path, "rb") as f:
        data = f.read()
    assert data, "File content is empty!"
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)
    assert encrypted_data, "Encrypted data is empty!"
    if to_return and not to_file:
        return encrypted_data
    if to_file:
        filename, extention = Path(file_path).stem, Path(file_path).suffix
        file_path_folder = path.dirname(file_path)
        encrypted_file_path = filename + "_encrypted" + extention
        encrypted_file_path = path.join(file_path_folder, encrypted_file_path)
        with open(encrypted_file_path, "wb") as f:
            f.write(encrypted_data)
        assert Path(
            encrypted_file_path
        ).exists(), f"encrypted_file_path: {encrypted_file_path} does not exist!"
    if to_return:
        return encrypted_data


def decrypt_file(file_path, key, to_file=True, to_return=False):
    """
    Decrypts a file using the provided key.

    Args:
        file_path (str): The path to the file to be decrypted.
        key (bytes): The encryption key used for decryption.
        to_file (bool, optional): Whether to save the decrypted data to a file. Defaults to True.
        to_return (bool, optional): Whether to return the decrypted data. Defaults to False.

    Returns:
        bytes or None: The decrypted data if `to_return` is True, None otherwise.
    """
    assert Path(file_path).exists(), f"file_path: {file_path} does not exist!"
    with open(file_path, "rb") as f:
        encrypted_data = f.read()
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    assert decrypted_data, "Decrypted data is empty!"
    if to_return and not to_file:
        return decrypted_data
    if to_file:
        filename, extention = Path(file_path).stem, Path(file_path).suffix
        file_path_folder = path.dirname(file_path)
        decrypted_file_path = filename + "_decrypted" + extention
        decrypted_file_path = decrypted_file_path.replace("_encrypted", "")
        decrypted_file_path = path.join(file_path_folder, decrypted_file_path)
        with open(decrypted_file_path, "wb") as f:
            f.write(decrypted_data)
        # Check if the decrypted file exists
        assert Path(
            decrypted_file_path
        ).exists(), f"decrypted_file_path: {decrypted_file_path} does not exist!"
        return decrypted_data
    if to_return:
        return decrypted_data


def main():
    parser = argparse.ArgumentParser(description="Encrypt or decrypt a file.")
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="The path of the file to encrypt or decrypt.",
    )
    parser.add_argument(
        "-a",
        "--action",
        required=True,
        choices=[ENCRYPTION, DECRYPTION, GENRATE_KEY_FILE],
        help="The action to perform. encrypt or decrypt. or generate key file. (en/de/gen)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-k", "--key", help="The key string.")
    group.add_argument(
        "-kf",
        "--keyfile",
        help="The path of the key file. if key is not provided, keyfile is required. the content of the key file should be the (function) def urlsafe_b64encode(s: ReadableBuffer) -> bytes . not a password string.",
    )

    parser.add_argument(
        "-s",
        "--save_key_path",
        required=False,
        default="",
        help="Save the key to a file.",
    )

    args = parser.parse_args()
    if args.action == GENRATE_KEY_FILE and args.save_key_path:
        key = generate_key(args.key.encode(), salt_random=True)
        ensure_file_exists(args.save_key_path)
        with open(args.save_key_path, "wb") as key_file:
            key_file.write(key)
        return
    if args.key:
        key = generate_key(args.key.encode())
        if args.save_key_path:
            ensure_file_exists(args.save_key_path)
            with open(args.save_key_path, "wb") as key_file:
                key_file.write(key)
    else:
        with open(args.keyfile, "rb") as key_file:
            key = key_file.read()
    if args.action == ENCRYPTION:
        encrypt_file(args.file, key)
        logging.info("File is encrypted!")
    elif args.action == DECRYPTION:
        decrypt_file(args.file, key)
        logging.info("File has been decrypted!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
