import hashlib
import pickle
from functools import wraps
from loguru import logger
from typing import Callable


# 以下缓存装饰器不适用于频繁变化参数的函数, 而且只能是一一映射的函数


# assert_result作为回调函数,判断是否是个合理,正确的返回值
# 只有是合理的才被缓存,或者被读取缓存
def async_unit_cache(assert_result: Callable, cache_path: str):

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            try:
                with open(cache_path, "rb") as f:
                    cache: dict = pickle.load(f)
            except Exception:
                cache: dict = dict()

            # 散列唯一键,根据参数生成
            # 同样的参数同样的键
            key: str = hashlib.sha256(str((args, kwargs)).encode()).hexdigest()

            try:
                # 如果有,读取缓存值
                result = cache[key]

                assert_result(result)

                logger.success(f"Cache hit for {func.__name__}")
            except KeyError:

                logger.debug(f"Cache miss for {func.__name__}")

                # 如果没有缓存, 返回函数处理的值
                result = await func(*args, **kwargs)

                assert_result(result)

                cache[key] = result

                with open(cache_path, "wb") as f:
                    pickle.dump(cache, f)

            except Exception:

                # 错误也返回函数处理的值

                result = await func(*args, **kwargs)

            finally:
                return result

        return wrapper

    return decorator


# assert_result作为回调函数,判断是否是个合理,正确的返回值
# 只有是合理的才被缓存,或者被读取缓存
def sync_unit_cache(assert_result: Callable, cache_path: str):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            try:
                with open(cache_path, "rb") as f:
                    cache: dict = pickle.load(f)
            except Exception:
                cache: dict = dict()

            # 散列唯一键,根据参数生成
            # 同样的参数同样的键
            key: str = hashlib.sha256(str((args, kwargs)).encode()).hexdigest()

            try:
                # 如果有,读取缓存值
                result = cache[key]

                assert_result(result)

                logger.success(f"Cache hit for {func.__name__}")
            except KeyError:

                logger.debug(f"Cache miss for {func.__name__}")

                # 如果没有缓存, 返回函数处理的值
                result = func(*args, **kwargs)

                assert_result(result)

                cache[key] = result

                with open(cache_path, "wb") as f:
                    pickle.dump(cache, f)

            except Exception:

                # 错误也返回函数处理的值

                result = func(*args, **kwargs)

            finally:
                return result

        return wrapper

    return decorator
