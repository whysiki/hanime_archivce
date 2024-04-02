from loguru import logger
from pathlib import Path
import os

# 处理文件路径的自定义工具函数


def ensure_file_exists(
    file_path: str, file_encoding: str = "UTF-8"
) -> tuple[bool, str]:
    try:
        if not file_path:
            logger.error("Filepath is empty or None.")
            return (False, "")
        filepath: Path = Path(file_path)
        # Check if the file exists
        if filepath.exists():
            return (True, str(filepath))
        # Create parent directories if they don't exist(is a directory)
        # exist_ok=True prevents FileExistsError
        filepath.parent.mkdir(parents=True, exist_ok=True)
        # Create the file
        filepath.touch(exist_ok=True)
        return (True, str(filepath))
    except PermissionError as e:
        logger.error(f"Permission denied while creating file at {file_path}.")
        logger.error(f"Error details: {str(e)}")
        return (False, "")
    except Exception as e:
        error_type = type(e).__name__
        logger.error(
            f"An unknown error occurred in ensure_file_exists function. Error details: {str(e)},error type: {error_type}"
        )
        return (False, "")


def count_rechange_files_directory(
    path: str,
    recursion_count_begin: int = 1,  # begin
    mix_recursion_count: int = 100,  # max recursion times
    mix_capacity: int = 100,  # the max files number in a directory
) -> str:

    # save original path
    origin_path: str = path

    # recursion lawer
    def recursion(
        path: str = path, recursion_count_begin: int = recursion_count_begin - 1
    ) -> str:
        # create directory
        if not os.path.exists(path):
            try:
                os.mkdir(path)
                assert os.path.isdir(path)
            except FileNotFoundError:
                os.makedirs(path)
                assert os.path.isdir(path)
            except Exception as e:
                raise e
        # counter files number in new path
        files_number: int = os.listdir(path=path).__len__()

        # recursion condition
        if files_number > mix_capacity and recursion_count_begin < mix_recursion_count:
            return recursion(
                f"{origin_path}{recursion_count_begin+1}",
                recursion_count_begin + 1,
            )

        # border condition
        # files_number size ok
        # surpass or equal max
        else:
            logger.success(f"Finally Path : {path}")
            return path

    out_path: str = recursion()

    return out_path
