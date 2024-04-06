from os import path, system
import sys
from cyption import cyption
import subprocess
import tempfile
import getpass
import shutil
import atexit
import signal
from functools import partial

config_encrypted_path = path.join(
    path.dirname(__file__), "xray_config_generator", "config_encrypted.json"
)

xray_exe_path = path.join(path.dirname(__file__), "Xray-windows-64", "xray.exe")

password: str = getpass.getpass("Enter your password: ")
if password:
    key: bytes = cyption.generate_key(password)
else:
    key_path: str = getpass.getpass("Enter your key path: ")
    assert key_path, "Key path is empty!"
    key: bytes = cyption.get_key_from_file(key_path)

assert key, "Key is empty!"


assert path.exists(
    config_encrypted_path
), f"config_encrypted_path: {config_encrypted_path} does not exist!"


decrypted: bytes = cyption.decrypt_file(
    config_encrypted_path, key, to_file=False, to_return=True
)  # type: ignore


def clear_temp_dir(temp_dir):
    if temp_dir and path.exists(temp_dir):
        shutil.rmtree(temp_dir)


try:
    # 创建临时文件夹
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建临时 JSON 文件
        with tempfile.NamedTemporaryFile(
            dir=temp_dir, suffix=".json", delete=False
        ) as temp_file:
            # 将解密的配置数据写入临时 JSON 文件
            temp_file.write(decrypted)
            temp_file.flush()

            # 拼接命令
            command = f"{xray_exe_path} run -c {temp_file.name}"

            def cleanup(signum, frame):
                # 删除临时文件夹及其内容
                clear_temp_dir(temp_dir)
                exit(1)

            # 执行命令
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # 注册信号处理函数，在收到终止信号时执行清理操作
            signal.signal(signal.SIGINT, cleanup)
            signal.signal(signal.SIGTERM, cleanup)

            # 等待子进程结束
            process.wait()
finally:

    # 清理临时文件夹
    clear_temp_dir(temp_dir)  # type: ignore

atexit.register(clear_temp_dir, temp_dir)  # type: ignore

# command = f'start cmd /k "{xray_exe_path} run -c {temp_file.name}"'
