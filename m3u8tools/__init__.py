from asyncio import futures
from doctest import debug
import requests
from rich import print
import hashlib
import re
import os
import tqdm
import asyncio
import aiohttp
import aiofiles
from functools import wraps
from loguru import logger
from pathlib import Path
import json
from typing import Callable
import subprocess
import datetime
import shutil
from functools import partial
import math
import multiprocessing
import uuid
import concurrent.futures
import fake_useragent
import tempfile
import random

# # Configuration file
from config import (
    TS_RETRIES,
    TIME_OUT,
    TS_SEMAPHORE_SIZE,
    PROXIES_POOL,
    RANDOM_SLEEP_RANGE,
    FFMPEG_EXE_PATH,
)

FFMPEG_EXE_PATH = FFMPEG_EXE_PATH


def read_headers_from_json(
    headers_example: str, to_read_cookie: bool = True, cookie_json_filepath: str = ""
) -> dict:
    """
    从JSON文件中读取HTTP头信息。

    参数:
    headers_example (str): 包含头信息示例的JSON文件路径。
    to_read_cookie (bool): 是否需要读取cookie信息，默认为True。
    cookie_json_filepath (str): 包含cookie信息的JSON文件路径，默认为空字符串。

    返回:
    headers (dict): 从JSON文件中读取的头信息。
    """

    with open(cookie_json_filepath, encoding="utf-8") as f:

        with open(headers_example, encoding="utf-8") as h:
            headers__fierfox_original = dict(json.load(h))
            middle_: dict = headers__fierfox_original[
                list(headers__fierfox_original.keys())[0]
            ]
            d_list_headers = middle_["headers"]

            headers = {d["name"]: d["value"] for d in d_list_headers}

            if to_read_cookie and not cookie_json_filepath:
                d_list: list = json.load(f)

                headers_cookie = "; ".join(
                    [f'{d["name"]}={d["value"]}' for d in d_list]
                )

                headers["Cookie"] = headers_cookie

        return headers


def ensure_file_exists(file_path: str) -> tuple[bool, str]:
    """
    确保给定的文件路径存在。如果文件不存在，此函数将创建它。

    参数:
    file_path (str): 需要检查的文件路径。

    返回:
    tuple: 包含两个元素的元组。第一个元素是布尔值，表示文件是否成功创建或已存在。第二个元素是实际的文件路径，如果创建失败则为空字符串。
    """
    try:
        if not file_path:
            logger.error("文件路径为空。")
            return (False, "")

        filepath = Path(file_path)

        if not filepath.parent.exists():
            filepath.parent.mkdir(parents=True, exist_ok=True)

        if not filepath.exists():
            filepath.touch()

        return (True, str(filepath))
    except PermissionError:
        logger.error(f"没有权限创建文件: {file_path}")
        return (False, "")
    except Exception as e:
        logger.error(f"在创建文件时发生未知错误: {file_path}, 错误详情: {str(e)}")
        return (False, "")


def merge_ts_files_ffmpeg_unit(
    tuple_files_output_file: tuple = tuple(),
    input_files: list[str] = [],
    output_file: str = "",
    overwrite=True,
    command_list: list[str] = [],
    temp_dir: str = "temp_ffmpeg_cache",
    ffmpeg_exe_path: str = FFMPEG_EXE_PATH,  # type: ignore
):
    """
    使用ffmpeg接口封装合并视频文件。

    参数:
    tuple_files_output_file (tuple): 包含输入文件和输出文件路径的元组。
    input_files (list[str]): 输入文件路径列表。
    output_file (str): 输出文件路径。
    overwrite (bool): 是否覆盖已存在的输出文件，默认为True。
    command_list (list[str]): 需要传递给ffmpeg的额外命令列表。
    temp_dir (str): 临时文件夹路径，默认为"temp_ffmpeg_cache"。
    ffmpeg_exe_path (str): ffmpeg可执行文件的路径。

    返回:
    tuple: 包含两个元素的元组。第一个元素是布尔值，表示文件是否成功创建或已存在。第二个元素是实际的文件路径，如果创建失败则为空字符串。
    """
    if tuple_files_output_file and len(tuple_files_output_file) == 2:
        input_files, output_file = tuple_files_output_file

    # 检查输入文件是否存在
    for input_file in input_files:
        if not Path(input_file).exists():
            raise FileNotFoundError(f"输入文件 {input_file} 不存在")

    # 检查是否需要覆盖输出文件
    if not overwrite and Path(output_file).exists():
        raise FileExistsError(f"输出文件 {output_file} 已存在")

    else:
        ensure_file_exists(output_file)

    if len(input_files) == 1:
        logger.debug(f"合成列表只有一个文件 {input_files[0]} , 将直接复制")
        shutil.copyfile(input_files[0], output_file)
        return True, output_file

    # 创建一个临时文件用来存放文件路径
    temp_params_file = Path(temp_dir) / "temp_ffmpegparam_file" / str(uuid.uuid4())
    temp_params_file.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        delete=False,
        dir=str(temp_params_file),
        suffix=".txt",
    ) as temp_file:
        # 写入文件路径到临时文件中
        input_files.sort(key=lambda x: int(x.split("seg")[1].split(".")[0]))

        for order, input_file in enumerate(input_files):
            if order == len(input_files) - 1:
                temp_file.write(f"file '{input_file}'".encode())
            else:
                temp_file.write(f"file '{input_file}'\n".encode())

        # 刷新缓冲区
        temp_file.flush()

        ffmpeg_command = [
            ffmpeg_exe_path,
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            temp_file.name,
            "-c",
            "copy",
            "-loglevel",
            "fatal",
            output_file,
        ]

    if overwrite:
        ffmpeg_command.insert(1, "-y")

    if command_list and len(command_list) > 1:
        ffmpeg_command.extend(command_list)

    try:
        subprocess.run(ffmpeg_command, check=True)
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        logger.error(f"合并 to {output_file} 失败：{error_type} {error_msg}")
        Path(output_file).unlink(missing_ok=True)
        logger.error(f"失败删除 {output_file}")
        return False, output_file
    else:
        logger.success(f"合并到 {output_file} 成功")
        return True, output_file


def merge_files(input_files: list[str], temp_dir: str, command_list: list[str]) -> str:
    """
    合并多个文件。

    参数:
    input_files (list[str]): 需要合并的输入文件路径列表。
    temp_dir (str): 临时文件夹路径。
    command_list (list[str]): 需要传递给ffmpeg的额外命令列表。

    返回:
    str: 合并后的文件路径。如果合并失败，返回空字符串。
    """
    if not input_files:
        logger.debug(f"merge_files input_files is empty")
        return ""

    extension = Path(input_files[0]).suffix
    output_file = Path(temp_dir) / "temp_merge_dir" / f"{uuid.uuid4()}{extension}"

    is_successful, output_file = merge_ts_files_ffmpeg_unit(
        tuple_files_output_file=tuple(),
        input_files=input_files,
        output_file=str(output_file),
        overwrite=True,
        command_list=command_list,
        temp_dir=temp_dir,
    )

    return str(output_file) if is_successful else ""


def merge_mp4_files_ffmpeg(
    input_files: list[str],
    output_file: str,
    temp_dir: str = "temp_merge_mp4_cache",
    command_list: list = [],
) -> bool:
    """
    使用ffmpeg合并多个MP4文件。

    参数:
    input_files (list[str]): 需要合并的输入文件路径列表。
    output_file (str): 合并后的输出文件路径。
    temp_dir (str): 临时文件夹路径，默认为"temp_merge_mp4_cache"。
    command_list (list): 需要传递给ffmpeg的额外命令列表。

    返回:
    bool: 如果合并成功，返回True，否则返回False。
    """
    try:
        # 检查输入文件是否存在
        for file in input_files:
            if not Path(file).exists():
                logger.error(f"文件 {file} 不存在")
                return False

        temp_out_file = merge_files(input_files, temp_dir, command_list)

        if not temp_out_file:
            logger.error("没有得到合并后的文件路径, 合并失败")
            return False

        shutil.copyfile(temp_out_file, output_file, follow_symlinks=True)

        logger.debug(f"把 {temp_out_file} 复制到 {output_file} 成功")
        logger.success(f"合并视频文件成功, 输出文件: {output_file}")

        return True

    except Exception as e:
        logger.error(
            f"函数 merge_mp4_files_ffmpeg 合并视频文件失败：{type(e).__name__} : {str(e)}"
        )
        return False


# 错误随机等待函数
async def randowm_sleep():
    await asyncio.sleep(random.randint(RANDOM_SLEEP_RANGE[0], RANDOM_SLEEP_RANGE[1]))


def retry_on_error_defalut_no_raise_error(
    retries: int = 4,
    callbackfunc: Callable = lambda x: x,
    process_error: Callable = lambda x: x,
):
    """
    一个装饰器，用于在函数出错时进行重试。

    参数:
    retries (int): 重试次数，默认为4次。
    callbackfunc (Callable): 在每次重试之前调用的回调函数，用于可能的错误处理或更新参数，默认为一个恒等函数。
    process_error (Callable): 在所有重试都失败后调用的函数，用于处理错误，默认为一个恒等函数。

    返回:
    wrapper: 装饰后的函数。
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            """
            装饰器的内部函数，用于包装原函数。

            参数:
            *args: 原函数的位置参数。
            **kwargs: 原函数的关键字参数。

            返回:
            result: 原函数的返回值。
            """
            for attempt in range(retries):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    error_msg = str(e)
                    error_type = type(e).__name__
                    logger.debug(
                        f"{func.__name__} raise an Error {error_type} occurred on attempt {attempt + 1}/{retries}: {error_msg}"
                    )

                    await randowm_sleep()

                    if attempt == retries - 1:
                        logger.error(
                            f"Function {func.__name__} failed after {retries} attempts"
                        )
                        process_error(e)
                    kwargs = callbackfunc(kwargs)

        return wrapper

    return decorator
