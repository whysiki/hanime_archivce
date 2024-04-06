import os


def get_file_extension(file_path):
    """
    获取文件的扩展名
    """
    root, extension = os.path.splitext(file_path)
    return root, extension


file_path = "example_file.txt"
root, extension = get_file_extension(file_path)
print(root, extension)


print(bool(tuple()))
