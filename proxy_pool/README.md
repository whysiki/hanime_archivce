## cyption 使用方法

使用了 Fernet 加密，这是一种对称加密方式，它使用了 AES 在 CBC 模式下的加密以及使用 PKCS7 进行填充。
Fernet 还包括了一个时间戳在内的 HMAC 签名，以保证数据的完整性和安全性。
为了简化，当只使用密码加密解密时, 盐是由密码生成的，而不是随机生成的(除了第一种方法外)

1. **只生成密钥文件**：使用以下命令，你可以生成一个密钥文件，然后后面只能使用这个密钥文件进行加密和解密操作。密钥文件的后缀名为`.key`。

   ```shell
   python cyption/cyption.py -f your_file -a gen -k your_password -s your_key_save_path
   ```

2. **生成密钥文件并加密文件**：使用以下命令，你可以生成一个密钥文件，并使用这个密钥文件加密指定的文件。加密后的文件名会添加`_encrypted`后缀，文件类型不变。

   ```shell
   python cyption/cyption.py -f your_file -a en -k your_password -s your_key_save_path
   ```

3. **使用密码加密文件**：使用以下命令，你可以直接使用密码加密指定的文件，而不生成密钥文件。

   ```shell
   python cyption/cyption.py -f your_file -a en -k your_password
   ```

4. **使用密钥文件加密文件**：使用以下命令，你可以使用已有的密钥文件加密指定的文件。

   ```shell
   python cyption/cyption.py -f your_file -a en -kf your_key_path
   ```

5. **使用密码解密文件**：使用以下命令，你可以直接使用密码解密指定的文件。解密后的文件名会添加`_decrypted`后缀，文件类型不变。

   ```shell
   python cyption/cyption.py -f your_file -a de -k your_password
   ```

6. **使用密钥文件解密文件**：使用以下命令，你可以使用已有的密钥文件解密指定的文件。

   ```shell
   python cyption/cyption.py -f your_file -a de -kf your_key_path
   ```

7. 运行测试:`run_test.bat`

## 命令行参数

你可以使用`--help`参数查看所有的命令行参数：

```shell
python cyption/cyption.py --help
```

## 在 xray_config_generator 中使用

在生成 `config.json` 文件后，你可以使用 `cyption.py` 生成一个加密的 `config_encrypted.json` 文件。

然后，你可以启动 `run.py` 来启动代理池，并输入你用于加密的密码。

密码输入时不会显示，但是会接收到输入，输入完成后按回车键即可。

如果密码为空，程序会要求你输入密钥文件的路径。输入路径后按回车键即可。

程序会自动解密文件，并将其存放在一个临时文件夹内。当程序结束后（通过按 Control + C），临时文件夹会被自动删除。
