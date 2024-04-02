import sqlite3
import hashlib
import time
from functools import wraps
from typing import Callable
from loguru import logger

# import aiosqlite
import json

# import asyncio
# import threading


# 由于sqlite3异步效果不好, 所以只能用同步的方式

# 下面两个函数一个对于异步单元函数的缓存, 一个对于同步单元函数的缓存
# 适用于那种输入有频繁变化的函数, 但是输出是一一映射的函数
# 也就是说, 同样的输入, 会得到同样的输出
# 使用散列对输入进行处理, 生成唯一键, 用于缓存

# 使用缓存的目的是减少重复计算获取, 提高效率

# Due to the poor performance of asynchronous sqlite3, we can only use synchronous methods.

# The following two functions are for caching asynchronous unit functions and synchronous unit functions, respectively.
# They are suitable for functions where the input frequently changes, but the output is one-to-one mapped.
# In other words, the same input will yield the same output.
# The inputs are processed using a hash function to generate a unique key for caching.

# The purpose of caching is to reduce redundant calculations and improve efficiency.

# 全局同步连接字典
# KEY: cache_path, VALUE: conn
global_conn_sync: dict[str, sqlite3.Connection] = {}


# 获取全局同步连接
def get_global_cursor_sync(cache_path: str) -> sqlite3.Connection:
    global global_conn_sync

    key = cache_path

    global_conn_sync[key] = (
        sqlite3.connect(cache_path)
        if key not in global_conn_sync  # 如果没有连接,创建连接
        else global_conn_sync[key]  # 如果有连接,返回连接
    )

    return global_conn_sync[key]


def async_unit_cache_sqlite(
    assert_result: Callable,
    cache_path: str,
    cache_expiry: float = 3600,
    filter_params: list = [
        "proxies",
        # "headers",
    ],  # 过滤参数, 核心参数参与散列,过滤参数不参与散列
):
    # 互斥锁
    # db_lock = asyncio.Lock()

    # global global_cursor_async
    # global global_conn_async

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # async with db_lock:
            # 连接数据库
            # async with aiosqlite.connect(cache_path) as conn:
            # logger.debug(f"Connected to {cache_path} for {func.__name__}")
            # conn = await get_global_cursor_async(cache_path)

            conn = get_global_cursor_sync(cache_path)

            cursor = conn.cursor()

            # async with conn.cursor() as cursor:

            # await cursor.execute("select * from cache")
            # test_result = await cursor.fetchall()
            # logger.debug(f"len of test_result: {len(test_result)}")
            # logger.debug(f"test_result: {test_result[0][0]}")

            # 初始化数据库
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS cache
                                        (key TEXT PRIMARY KEY, result TEXT NOT NULL , timestamp REAL NOT NULL)"""
            )  # (key TEXT PRIMARY KEY, result TEXT, timestamp REAL)

            # 删除 kwargs 中的 proxies 参数
            # 原参数不变,只是一个删除了过滤参数的原参数的副本
            kwargs_without_filter_params = kwargs.copy()
            for filter_param in filter_params:
                kwargs_without_filter_params.pop(filter_param, None)

            # 散列唯一键,根据参数生成,忽略了过滤参数
            key: str = hashlib.sha256(
                str((args, kwargs_without_filter_params)).encode()
            ).hexdigest()
            # print(key)

            # 提取缓存数据
            cursor.execute("SELECT result, timestamp FROM cache WHERE key=?", (key,))

            cached_data = cursor.fetchone()  # (str, float)

            # logger.debug(f"Cache data: {cached_data}")

            try:
                # 如果有,读取缓存值

                # 有效缓存判断
                assert cached_data and len(cached_data) == 2

                cached_result_str, cached_timestamp = cached_data  # (str, float)

                # 读取缓存值,json转换
                cached_result_dict: dict = json.loads(cached_result_str)

                assert_result(cached_result_dict)

                assert isinstance(cached_timestamp, float)

                assert time.time() - cached_timestamp < cache_expiry

                logger.success(f"Cache hit for {func.__name__}")

                # await conn.commit()

                # 返回有效的缓存值
                return cached_result_dict

            except AssertionError:

                # 如果没有缓存, 返回函数处理的值
                logger.info(f"Cache miss for {func.__name__}")

                result_dict: dict = await func(*args, **kwargs)

                try:
                    # 判断返回值是否合理
                    assert_result(result_dict)
                except:
                    logger.info(f"Invalid result for {func.__name__}, not caching")
                else:
                    # 如果合理, 缓存新数据或更新缓存
                    # 缓存新数据或更新缓存
                    result_str: str = json.dumps(result_dict)
                    cursor.execute(
                        "REPLACE INTO cache (key, result, timestamp) VALUES (?, ?, ?)",
                        (key, result_str, time.time()),
                    )
                    conn.commit()

                    logger.info(f"Cache updated for {func.__name__}")
                # await conn.commit()

                # 返回函数处理的值
                # await conn.commit()

                return result_dict

            except Exception as e:

                error_type = type(e).__name__

                error_message = str(e)

                logger.error(
                    f"Cache error: {error_type}, {error_message} , {func.__name__}"
                )

                # await conn.commit()

                return dict(error=error_message, error_type=error_type)

            finally:

                cursor.close()

                #     await close_global_cursor_async()

            #     await conn.commit()

        return wrapper

    # global global_cursor_async
    # global global_conn_async

    # global_cursor_async.close()
    # global_conn_async.close()

    return decorator


def sync_unit_cache_sqlite(
    assert_result: Callable,
    cache_path: str,
    cache_expiry: float = 3600,
    filter_params: list = ["to_print_json"],
):
    # 互斥锁
    # db_lock = threading.Lock()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # with db_lock:

            # 连接数据库
            # with sqlite3.connect(cache_path) as conn:
            # logger.debug(f"Connected to {cache_path} for {func.__name__}")
            conn = get_global_cursor_sync(cache_path)

            # print(global_conn_sync)

            cursor = conn.cursor()

            # with conn.cursor() as cursor:

            # 初始化数据库
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS cache
                                        (key TEXT PRIMARY KEY, result TEXT NOT NULL, timestamp REAL NOT NULL)"""
            )

            # 过滤参数
            kwargs_without_filter_params = kwargs.copy()
            for filter_param in filter_params:
                kwargs_without_filter_params.pop(filter_param, None)

            # 散列唯一键,根据参数生成
            key: str = hashlib.sha256(
                str((args, kwargs_without_filter_params)).encode()
            ).hexdigest()

            # 提取缓存数据
            cursor.execute("SELECT result, timestamp FROM cache WHERE key=?", (key,))
            cached_data = cursor.fetchone()

            try:
                # 如果有,读取缓存值

                # 有效缓存判断
                assert cached_data and len(cached_data) == 2

                cached_result, cached_timestamp = cached_data  # (str, float)

                # 读取缓存值,json转换
                cached_result = json.loads(cached_result)

                assert_result(cached_result)

                assert isinstance(cached_timestamp, float)

                assert time.time() - cached_timestamp < cache_expiry

                # conn.close()

                logger.success(f"Cache hit for {func.__name__}")

                # conn.commit()
                return cached_result

            except AssertionError:

                # 如果没有缓存, 返回函数处理的值
                logger.info(f"Cache miss for {func.__name__}")

                result: dict = func(*args, **kwargs)

                try:
                    # 判断返回值是否合理
                    assert_result(result)
                except:
                    logger.info(f"Invalid result for {func.__name__}, not caching")
                else:
                    # 如果合理, 缓存新数据或更新缓存
                    # 缓存新数据或更新缓存

                    # dict转换为str
                    result_str = json.dumps(result)

                    cursor.execute(
                        "REPLACE INTO cache (key, result, timestamp) VALUES (?, ?, ?)",
                        (key, result_str, time.time()),
                    )
                    conn.commit()
                    logger.info(f"Cache updated for {func.__name__}")
                # conn.commit()
                # conn.close()

                # 返回函数处理的值

                # conn.commit()
                return result

            except Exception as e:

                error_type = type(e).__name__

                error_message = str(e)

                logger.error(
                    f"Cache error: {error_type}, {error_message}, {func.__name__}"
                )

                # conn.close()

                # conn.commit()

                return dict(error=error_message, error_type=error_type)

            finally:

                cursor.close()

            # finally:

            #     close_global_cursor_sync()

        #     conn.commit()

        return wrapper

    # global global_cursor_sync
    # global global_conn_sync

    # global_cursor_sync.close()
    # global_conn_sync.close()

    # print(global_conn_sync)

    return decorator


# if __name__ == "__main__":
#     pass
