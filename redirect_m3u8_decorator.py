from math import log

from config import *

# from cellfunctions import convert_bytes_to_megabytes


def redirect_m3u8_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kargs):

        try:
            result = await func(*args, **kargs)
            if TO_DOWNLOAD_M3U8 and "m3u8" in result and "error" in result:
                logger.debug(f"重定向到m3u8下载任务, {kargs}")
                result = dict(
                    url=kargs["url"], filename=kargs["filename"], m3u8=True, mp4=False
                )
            return result
        except Exception:
            return result  # type: ignore

    return wrapper
