from read_head_cookie import read_headers_from_json
import asyncio
import os
import pathlib
from bs4 import BeautifulSoup
import json
import aiohttp
from rich import print
from tqdm import tqdm
import aiofiles
from loguru import logger
import pickle
import string
from typing import Optional, Set, Dict, Callable, Union
from pathlib import Path
from functools import cached_property
from urllib.parse import urlencode, urljoin
from functools import wraps
import hashlib
from path_tools import ensure_file_exists
from proxy_pool import ProxyPool
import random
import multiprocessing
import math
from concurrent.futures import ProcessPoolExecutor
import datetime

# 大部分配置都在这里

# 网站配置
HOST = "https://hanime1.me"  # 网站主页
HEADERS = read_headers_from_json()  # 读取请求头

# 起始代理配置
PROXIES = {
    "http://": r"http://127.0.0.1:62333",
    "https://": r"http://127.0.0.1:62333",
}  # 代理配置,最好是http的
PROXIES_POOL = ProxyPool()  # 代理池
TO_USE_PROXY_POOL = True  # 是否使用代理池

# 并发和连接配置
SEMAPHORE_SIZE = 20  # 默认并发数
TS_SEMAPHORE_SIZE = 20  # m3u8下载ts并发数
AIOHTTP_CONNECTION_LIMIT = 700  # aiohttp最大连接数

# 下载和缓存配置
TO_DOWNLOAD_M3U8 = True  # 是否下载m3u8视频,默认不下载,因为可能堵塞mp4下载
To_DOWNLOAD_MP4 = True  # 是否下载mp4视频
SAVE_PATH = "videos"  # 下载视频保存路径
SOURCE_CACHE_DIR = "cache/source/sql/source_cache.db"  # 源码缓存目录
BATCH_SIZE = 20  # 分批合成
PARSE_CACHE_DIR = "cache/parse/sql/parse_cache.db"  # 解析缓存目录
TO_CLEAR_CACHE = True  # 是否清理m3u8缓存
MERGE_TS_PROCESSES = math.floor(
    multiprocessing.cpu_count() / 3
)  # 合并ts进程数 和解析进程数

# 转换配置
# # 不要动 弃用
# CONVERT_TS_TO_MP4 = False  # 是否转换ts为mp4, 对于m3u8视频,需要转换,但是因为调用的是ffmpeg,可能会出现堵塞,所以默认不转换,这里是同步
# CONVERT_TS_TO_MP4_ASYNC = True  # 异步转换

# 重试和超时配置
RANDOM_SLEEP_RANGE = (1, 2)  # 随机等待范围
GET_SOURSE_RETRIES = 20  # 源码获取错误重试次数
RETRIES = 60  # 默认重试次数
TS_RETRIES = 60  # ts下载重试次数
DOWNLOAD_VIDEO_RETRIES = 20  # 下载mp4视频重试次数
TIME_OUT = 200  # 下载ts超时时间，单位：秒


assert len(PROXIES) > 0, "请配置代理"
assert len(HEADERS) > 0, "请配置请求头"
assert len(HOST) > 0, "请配置HOST"
assert SEMAPHORE_SIZE > 0, "请配置SEMAPHORE_SIZE"
assert (
    len(RANDOM_SLEEP_RANGE) == 2 and RANDOM_SLEEP_RANGE[0] < RANDOM_SLEEP_RANGE[1]
), "请正确配置RANDOM_SLEEP_RANGE"

assert ensure_file_exists(SOURCE_CACHE_DIR)[0], "请配置SOURCE_CACHE_DIR"

assert ensure_file_exists(PARSE_CACHE_DIR)[0], "请配置PARSE_CACHE_DIR"


assert isinstance(RETRIES, int), "请配置RETRIES"

assert isinstance(GET_SOURSE_RETRIES, int), "请配置GET_SOURSE_RETRIES"

assert isinstance(DOWNLOAD_VIDEO_RETRIES, int), "请配置DOWNLOAD_VIDEO_RETRIES"

assert isinstance(TIME_OUT, int), "请配置TIME_OUT"


assert isinstance(TO_USE_PROXY_POOL, bool), "请配置TO_USE_PROXY_POOL"

assert isinstance(PROXIES_POOL, ProxyPool), "请配置PROXIES_POOL"

assert isinstance(TS_SEMAPHORE_SIZE, int), "请配置TS_SEMAPHORE_SIZE"

assert isinstance(AIOHTTP_CONNECTION_LIMIT, int), "请配置AIOHTTP_CONNECTION_LIMIT"

assert isinstance(MERGE_TS_PROCESSES, int), "请配置MERGE_TS_PROCESSES"


time_now_day = datetime.datetime.now().strftime("%Y-%m-%d")
log_path = os.path.join(os.path.dirname(__file__), "log", f"{time_now_day}.log")
logger.add(log_path, rotation="1 week", retention="5 days", level="INFO")