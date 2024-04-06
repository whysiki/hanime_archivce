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
from config import RANDOM_SLEEP_RANGE, FFMPEG_EXE_PATH
import random

# from config import *
FFMPEG_EXE_PATH = FFMPEG_EXE_PATH


def read_headers_from_json(
    headers_example: str, to_read_cookie: bool = True, cookie_json_filepath: str = ""
) -> dict:

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


def ensure_file_exists(
    file_path: str, file_encoding: str = "UTF-8"
) -> tuple[bool, str]:
    try:
        if not file_path:
            logger.error("Filepath is empty or None.")
            return (False, "")
        filepath: Path = Path(file_path)

        if filepath.exists():
            return (True, str(filepath))

        filepath.parent.mkdir(parents=True, exist_ok=True)

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


# 合并视频文件 , 使用ffmpeg接口封装
def merge_ts_files_ffmpeg_unit(
    tuple_files_output_file: tuple = tuple(),
    input_files: list[str] = [],
    output_file: str = "",
    overwrite=True,
    command_list: list[str] = [],
    temp_dir: str = "temp_ffmpeg_cache",
    ffmpeg_exe_path: str = FFMPEG_EXE_PATH,
):
    if tuple_files_output_file and len(tuple_files_output_file) == 2:
        input_files, output_file = tuple_files_output_file

    # 检查输入文件是否存在
    for input_file in input_files:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件 {input_file} 不存在")

    # 检查是否需要覆盖输出文件
    if not overwrite and os.path.exists(output_file):
        raise FileExistsError(f"输出文件 {output_file} 已存在")

    else:

        ensure_file_exists(output_file)

    if len(input_files) == 1:

        logger.debug(f"合成列表只有一个文件 {input_files[0]} , 将直接复制")

        shutil.copyfile(input_files[0], output_file)

        return True, output_file

    # 创建一个临时文件用来存放文件路径
    tem_params_file = os.path.join(temp_dir, "temp_ffmpegparam_file", str(uuid.uuid4()))
    os.makedirs(tem_params_file, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        delete=False,
        dir=tem_params_file,
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
            # "ffmpeg",
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

        os.remove(output_file)
        logger.error(f"失败删除 {output_file}")
        return False, output_file
    else:
        logger.success(f"合并到 {output_file} 成功")
        return True, output_file


def merge_files(input_files: list[str], temp_dir: str, command_list: list[str]):

    if not input_files:

        logger.debug(f"merge_files input_files is empty")

        return

    extension = os.path.splitext(input_files[0])[-1]

    out_put_file = os.path.join(
        temp_dir, "temp_merge_dir", f"{str(uuid.uuid4())}{extension}"
    )

    b, out_put_file = merge_ts_files_ffmpeg_unit(
        tuple_files_output_file=tuple(),
        input_files=input_files,
        output_file=out_put_file,
        overwrite=True,
        command_list=command_list,
        temp_dir=temp_dir,
    )

    assert b, "error in def merge_files(input_files: list[str])"

    return out_put_file


def merge_mp4_files_ffmpeg(
    input_files: list[str],
    output_file: str,
    temp_dir: str = "temp_merge_mp4_cache",
    command_list: list = [],
) -> bool:

    try:

        for file in input_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"文件 {file} 不存在")

        temp_input_files = [merge_files(input_files, temp_dir, command_list)]

        assert len(temp_input_files) == 1, "最终合成文件列表数量不为1"

        shutil.copyfile(temp_input_files[0], output_file, follow_symlinks=True)

        logger.debug(f"把 {temp_input_files[0]} 复制到 {output_file} 成功")

        logger.success(f"合并视频文件成功, 输出文件: {output_file}")

        return True

    except Exception as e:

        error_type = type(e).__name__
        logger.error(
            f"函数 merge_mp4_files_ffmpeg 合并视频文件失败：{error_type} : {str(e)}"
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
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
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
