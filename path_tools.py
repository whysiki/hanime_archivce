from loguru import logger
from pathlib import Path
import os


def ensure_file_exists(
    file_path: str, file_encoding: str = "UTF-8"
) -> tuple[bool, str]:
    """
    确保文件存在，如果不存在则创建。

    参数:
    file_path (str): 文件路径。
    file_encoding (str): 文件编码，默认为"UTF-8"。

    返回:
    tuple: 包含一个布尔值和一个字符串。布尔值表示文件是否存在或是否创建成功，字符串表示文件的绝对路径。
    """
    try:
        if not file_path:
            logger.error("文件路径为空或None。")
            return (False, "")
        filepath: Path = Path(file_path)
        if filepath.exists():
            return (True, str(filepath))
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.touch(exist_ok=True)
        return (True, str(filepath))
    except PermissionError as e:
        logger.error(f"在创建文件 {file_path} 时被拒绝访问。")
        logger.error(f"错误详情: {str(e)}")
        return (False, "")
    except Exception as e:
        error_type = type(e).__name__
        logger.error(
            f"在ensure_file_exists函数中发生未知错误。错误详情: {str(e)},错误类型: {error_type}"
        )
        return (False, "")


def count_rechange_files_directory(
    path: str,
    recursion_count_begin: int = 1,
    mix_recursion_count: int = 100,
    mix_capacity: int = 100,
) -> str:
    """
    计算并更改文件目录。

    参数:
    path (str): 文件路径。
    recursion_count_begin (int): 递归开始的计数，默认为1。
    mix_recursion_count (int): 最大递归次数，默认为100。
    mix_capacity (int): 目录中的最大文件数量，默认为100。

    返回:
    str: 最终的文件路径。
    """
    origin_path: str = path

    def recursion(
        path: str = path, recursion_count_begin: int = recursion_count_begin - 1
    ) -> str:
        if not os.path.exists(path):
            try:
                os.mkdir(path)
                assert os.path.isdir(path)
            except FileNotFoundError:
                os.makedirs(path)
                assert os.path.isdir(path)
            except Exception as e:
                raise e
        files_number: int = len(os.listdir(path=path))

        if files_number > mix_capacity and recursion_count_begin < mix_recursion_count:
            return recursion(
                f"{origin_path}{recursion_count_begin+1}",
                recursion_count_begin + 1,
            )
        else:
            logger.success(f"最终路径 : {path}")
            return path

    out_path: str = recursion()

    return out_path
