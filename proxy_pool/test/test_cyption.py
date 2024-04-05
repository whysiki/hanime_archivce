import os
import subprocess
import pytest
import shutil
import tempfile
import uuid
from pathlib import Path

# from cyption import cyption

current_path = os.path.dirname(__file__)


@pytest.fixture
def password():
    return str(uuid.uuid4())


@pytest.fixture
def data_path():
    return os.path.join(current_path, "config.json")


@pytest.fixture
def script_path():
    current_path_parent = Path(current_path).parent
    return str(current_path_parent / "cyption" / "cyption.py")


# 测试加密和解密通过密码的方式, 不保存key
def test_encrypt_decrypt(password, data_path, script_path):
    root, extension = os.path.splitext(data_path)
    file_name = os.path.basename(data_path)  # config.json

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_data_path = os.path.join(temp_dir, file_name)
        temp_encrypted_path = os.path.join(
            temp_dir, file_name.replace(extension, "_encrypted" + extension)
        )
        temp_decrypted_path = os.path.join(
            temp_dir, file_name.replace(extension, "_decrypted" + extension)
        )

        # Copy the original data file to the temporary directory
        shutil.copy(data_path, temp_data_path)

        # Encrypt the file
        subprocess.run(
            ["python", script_path, "-f", temp_data_path, "-a", "en", "-k", password],
            check=True,
        )

        # Decrypt the file
        subprocess.run(
            [
                "python",
                script_path,
                "-f",
                temp_encrypted_path,
                "-a",
                "de",
                "-k",
                password,
            ],
            check=True,
        )

        # Read the original file
        with open(temp_data_path, "rb") as f:
            original_data = f.read()

        # Read the decrypted file
        with open(temp_decrypted_path, "rb") as f:
            decrypted_data = f.read()

        assert original_data == decrypted_data, "Encryption and decryption failed!"


# 测试加密和解密通过文件的方式
def test_encrypt_decrypt_file(data_path, script_path, password):
    root, extension = os.path.splitext(data_path)
    file_name = os.path.basename(data_path)  # config.json

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_data_path = os.path.join(temp_dir, file_name)
        temp_encrypted_path = os.path.join(
            temp_dir, file_name.replace(extension, "_encrypted" + extension)
        )
        temp_decrypted_path = os.path.join(
            temp_dir, file_name.replace(extension, "_decrypted" + extension)
        )

        key_path = os.path.join(temp_dir, "key.key")

        # print("key_path:", key_path)

        # Copy the original data file to the temporary directory
        shutil.copy(data_path, temp_data_path)

        # 通过密码生成key,保存到文件, 同时加密文件
        subprocess.run(
            [
                "python",
                script_path,
                "-f",
                temp_data_path,
                "-a",
                "en",
                "-k",
                password,
                "-s",
                key_path,
            ],
            check=True,
        )

        # Decrypt the file
        subprocess.run(
            [
                "python",
                script_path,
                "-f",
                temp_encrypted_path,
                "-a",
                "de",
                "-kf",
                key_path,
            ],
            check=True,
        )

        # Read the original file
        with open(temp_data_path, "rb") as f:
            original_data = f.read()

        # Read the decrypted file
        with open(temp_decrypted_path, "rb") as f:
            decrypted_data = f.read()

        assert original_data == decrypted_data, "Encryption and decryption failed!"


# 测试加密和解密通过生成密匙文件, 然后再, 加密文件, 解密文件
def test_encrypt_decrypt_generate_key_file(data_path, script_path, password):
    root, extension = os.path.splitext(data_path)
    file_name = os.path.basename(data_path)  # config.json

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_data_path = os.path.join(temp_dir, file_name)
        temp_encrypted_path = os.path.join(
            temp_dir, file_name.replace(extension, "_encrypted" + extension)
        )
        temp_decrypted_path = os.path.join(
            temp_dir, file_name.replace(extension, "_decrypted" + extension)
        )

        key_path = os.path.join(temp_dir, "key.key")

        # print("key_path:", key_path)

        # Copy the original data file to the temporary directory
        shutil.copy(data_path, temp_data_path)

        # 通过密码生成key,保存到文件,不加密文件
        subprocess.run(
            [
                "python",
                script_path,
                "-f",
                temp_data_path,
                "-a",
                "gen",
                "-k",
                password,
                "-s",
                key_path,
            ],
            check=True,
        )

        # 使用生成的key加密文件
        subprocess.run(
            ["python", script_path, "-f", temp_data_path, "-a", "en", "-kf", key_path],
            check=True,
        )

        # 使用生成的key解密文件
        subprocess.run(
            [
                "python",
                script_path,
                "-f",
                temp_encrypted_path,
                "-a",
                "de",
                "-kf",
                key_path,
            ],
            check=True,
        )

        # Read the original file
        with open(temp_data_path, "rb") as f:
            original_data = f.read()

        # Read the decrypted file
        with open(temp_decrypted_path, "rb") as f:
            decrypted_data = f.read()

        assert original_data == decrypted_data, "Encryption and decryption failed!"

        # 测试只能通过key文件解密, 不能再通过密码解密
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(
                [
                    "python",
                    script_path,
                    "-f",
                    temp_encrypted_path,
                    "-a",
                    "de",
                    "-k",
                    password,
                ],
                check=True,
            )
