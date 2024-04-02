from config import *
import random
from network_tools import is_internet_available


# 错误随机等待函数
async def randowm_sleep():
    await asyncio.sleep(random.randint(RANDOM_SLEEP_RANGE[0], RANDOM_SLEEP_RANGE[1]))


# 重试装饰器
def retry_on_error(
    retries: int = RETRIES, process_last_retry_func: Callable = lambda x: x
):

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                result = await func(*args, **kwargs)

                # error key in result indicates an error occurred
                if isinstance(result, dict) and "error" in result:

                    logger.debug(
                        f"Attempt {attempt + 1}/{retries} failed for function {func.__name__}, retrying..."
                    )

                    if TO_USE_PROXY_POOL:
                        kwargs["proxies"] = PROXIES_POOL.next_proxies()
                    await randowm_sleep()
                # status_code key in result indicates a successful request
                else:
                    return result

            logger.error(f"All attempts failed for function {func.__name__}")

            process_last_retry_func(kwargs)

            return result

        return wrapper

    return decorator


# 最后一次重试结束后的处理函数, 删除文件
def process_last_retry_func_mp4_to_delete_filename(kwargs):

    filename = kwargs["filename"]

    if os.path.exists(filename):

        os.remove(filename)

        logger.critical(f"\nDeleted {filename} after all attempts failed\n")
