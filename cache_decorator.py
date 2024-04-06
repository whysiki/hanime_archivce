import hashlib
import pickle
from functools import wraps
from loguru import logger
from typing import Callable, Any, Dict, Tuple


def async_unit_cache(assert_result: Callable[[Any], bool], cache_path: str) -> Callable:
    """
    异步缓存装饰器，用于缓存函数的返回值。

    参数:
    assert_result (Callable[[Any], bool]): 用于判断返回值是否合理的回调函数。
    cache_path (str): 缓存文件的路径。

    返回:
    Callable: 装饰器。
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Tuple, **kwargs: Dict) -> Any:
            try:
                with open(cache_path, "rb") as f:
                    cache: Dict[str, Any] = pickle.load(f)
            except Exception:
                cache: Dict[str, Any] = {}

            key: str = hashlib.sha256(str((args, kwargs)).encode()).hexdigest()

            try:
                result = cache[key]
                assert assert_result(result)
                logger.success(f"Cache hit for {func.__name__}")
            except KeyError:
                logger.debug(f"Cache miss for {func.__name__}")
                result = await func(*args, **kwargs)
                if assert_result(result):
                    cache[key] = result
                    with open(cache_path, "wb") as f:
                        pickle.dump(cache, f)
            except Exception:
                result = await func(*args, **kwargs)

            return result

        return wrapper

    return decorator


def sync_unit_cache(assert_result: Callable[[Any], bool], cache_path: str) -> Callable:
    """
    同步缓存装饰器，用于缓存函数的返回值。

    参数:
    assert_result (Callable[[Any], bool]): 用于判断返回值是否合理的回调函数。
    cache_path (str): 缓存文件的路径。

    返回:
    Callable: 装饰器。
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Tuple, **kwargs: Dict) -> Any:
            try:
                with open(cache_path, "rb") as f:
                    cache: Dict[str, Any] = pickle.load(f)
            except Exception:
                cache: Dict[str, Any] = {}

            key: str = hashlib.sha256(str((args, kwargs)).encode()).hexdigest()

            try:
                result = cache[key]
                assert assert_result(result)
                logger.success(f"Cache hit for {func.__name__}")
            except KeyError:
                logger.debug(f"Cache miss for {func.__name__}")
                result = func(*args, **kwargs)
                if assert_result(result):
                    cache[key] = result
                    with open(cache_path, "wb") as f:
                        pickle.dump(cache, f)
            except Exception:
                result = func(*args, **kwargs)

            return result

        return wrapper

    return decorator
