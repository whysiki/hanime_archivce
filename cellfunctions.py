from config import *
from assert_result_function import parse_assert_result, source_assert_result  #
from retry_decorator import *
from sqlite_cache_decorator import sync_unit_cache_sqlite, async_unit_cache_sqlite
import re
import fake_useragent
from m3u8tools.download_m3u8_file import M3u8_download
from redirect_m3u8_decorator import redirect_m3u8_decorator


@retry_on_error(retries=GET_SOURSE_RETRIES)
@async_unit_cache_sqlite(
    assert_result=source_assert_result, cache_path=SOURCE_CACHE_DIR
)
async def get_source(url: str, headers: dict, proxies: dict[str, str]) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=url, headers=headers, proxy=proxies.get("https://")
            ) as response:
                assert response.status == 200, f"status_code: {response.status}"

                # 定义一个正则表达式，用于匹配 HTML 标签
                html_tag_pattern = re.compile(
                    r"<html[^>]*>.*?</html>", re.IGNORECASE | re.DOTALL
                )

                # 使用 assert 语句来检查 re.text 是否包含 <html> 标签
                assert (
                    len(re.findall(html_tag_pattern, string=await response.text()))
                ) > 0, "response.text 不是一个 HTML 文档"

                logger.success(f"Fetched source from {url}")

                return dict(
                    source=await response.text(), status_code=response.status, url=url
                )
    except Exception as e:
        error_type = type(e).__name__
        logger.error(
            f"Failed to fetch source from {url}. Error details: {str(e)}, error type: {error_type}"
        )
        return dict(error=str(e), url=url, error_type=error_type)


# 解析 JSON 数据
@sync_unit_cache_sqlite(assert_result=parse_assert_result, cache_path=PARSE_CACHE_DIR)
def parse(source: str, to_print_json: bool = False) -> Dict[str, Union[str, bool]]:  # type: ignore

    try:
        if not source:
            logger.error("Source is empty or None.")
            return dict(error="Source is empty or None.")
        soup = BeautifulSoup(source, "html.parser")
        json_scripts = soup.find_all("script", type="application/ld+json")
        for script in json_scripts:
            cleaned_json_data = (
                script.text.replace("\n", "").replace("\t", "").replace(" ", "").strip()
            )

            url_pattern = r'"contentUrl":"(https?://[^"]+)",'

            contentUrl = re.findall(url_pattern, cleaned_json_data)[0].strip()
            assert contentUrl and (".mp4" in contentUrl), "Failed to parse contentUrl"

            name_pattern = r'"name":"([^"]+)",'

            name = re.findall(name_pattern, cleaned_json_data)[0].strip()
            # 去除路径字符和空格
            name.replace(" ", "")
            invalid_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|", "'"]
            for char in invalid_chars:
                name = name.replace(char, "")

            assert name, "Failed to parse name"

            description = re.findall(r'"description":"([^"]+)",', cleaned_json_data)[
                0
            ].strip()
            assert description, "Failed to parse description"

            # "uploadDate": "2024-04-02T01:34:17+00:00",
            # "uploadDate": "2024-03-21T02:26:10+00:00",
            uploadDate = re.findall(r'"uploadDate":"([^"]+)",', cleaned_json_data)[
                0
            ].strip()

            assert uploadDate, "Failed to parse uploadDate"

            json_data = dict(
                name=name,
                contentUrl=contentUrl,
                description=description,
                uploadDate=uploadDate,
            )

            # Print JSON data
            if to_print_json:
                print(json_data)

            logger.success(f"Parsed JSON data: {json_data}")

            return json_data

            # return dict(
            #     name=json_data["name"],
            #     contentUrl=json_data["contentUrl"],
            #     description=json_data["description"],
            #     uploadDate=uploadDate,
            # )

    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Failed to parse: {str(e)},error type: {error_type}")
        return dict(error=str(e), error_type=error_type)


# Convert bytes to megabytes
def convert_bytes_to_megabytes(bytes):
    mb = bytes / (1024 * 1024)
    if mb >= 1:
        return mb, "MB"
    kb = bytes / 1024
    if kb >= 1:
        return kb, "KB"
    return bytes, "bytes"


def get_random_user_agent() -> str:
    ua = fake_useragent.UserAgent()
    return ua.random


@retry_on_error(
    retries=DOWNLOAD_VIDEO_RETRIES,
    process_last_retry_func=process_last_retry_func_mp4_to_delete_filename,
)
@redirect_m3u8_decorator
async def download_mp4_with_progress(
    url: str,
    filename: str,
    proxies: Optional[dict[str, str]] = None,
    filter_size: int = 900,
    enable_filter: bool = True,
) -> Dict[str, Union[str, bool]]:

    def other_error_process(e: Exception) -> Dict[str, Union[str, bool]]:

        logger.error(f"Download failed for {filename}, url: {url}")
        error_type = type(e).__name__
        logger.error(f"Error details: {str(e)},error type: {error_type}")

        return dict(error=str(e), url=url, error_type=error_type, download_status=False)

    # first step
    try:
        # Check if the URL and filename are valid
        assert (
            isinstance(url, str)
            and isinstance(filename, str)
            and url
            and filename
            and ".mp4" in url
            and ".mp4" in filename
            # and "m3u8" not in url
        ), f"URL or filenname un-normal, {url}, {filename}"

        # if "m3u8" in url
        if ".m3u8" in url:
            return dict(
                error="m3u8 file is not supported",
                url=url,
                download_status=False,
                filename=filename,
                m3u8=True,
                # proxies=proxies,
            )  # type: ignore

        if not To_DOWNLOAD_MP4:

            logger.debug(f"关闭mp4下载 : {filename}")

            if os.path.exists(filename):

                os.remove(filename)

                logger.debug(f"删除预生成空文件: {filename}")

            return dict()

        proxy = proxies.get("http://") if proxies else None

        if not proxy:
            logger.warning(f"download_mp4_with_progress Proxy is empty or None.")

    except Exception as e:

        return other_error_process(e=e)

    # next step
    else:
        try:

            timeout = aiohttp.ClientTimeout(total=TIME_OUT)

            # 配置TCPConnector连接

            connector = aiohttp.TCPConnector(
                verify_ssl=False,
                limit=AIOHTTP_CONNECTION_LIMIT,
                enable_cleanup_closed=True,
                ttl_dns_cache=None,
                use_dns_cache=True,
                force_close=True,
                timeout_ceil_threshold=30,
                # keepalive_timeout=30,
            )

            async with aiohttp.ClientSession(
                headers={"User-Agent": get_random_user_agent()},
                connector=connector,
                timeout=timeout,
            ) as session:

                # initialize the downloaded size
                downloaded_size: int = 0
                if (
                    os.path.exists(filename)
                    and os.path.isfile(filename)
                    and os.path.getsize(filename) > 0
                ):
                    # Get the size of the file that has already been downloaded
                    downloaded_size = os.path.getsize(filename)

                # Set the headers to resume the download from the last downloaded size
                headers = (
                    {"Range": f"bytes={downloaded_size}-"} if downloaded_size else {}
                )
                async with session.get(url, proxy=proxy, headers=headers) as response:

                    # status code 200 indicates success
                    assert (
                        response.status == 200
                        or response.status == 206  # 206 Partial Content
                        or response.status == 416  # 416 Requested Range Not Satisfiable
                    ), f"Download failed for {filename}, status code: {response.status}, url: {url}"

                    # Get the total size of the file to download
                    total_size = (
                        int(response.headers.get("content-length", 0)) + downloaded_size
                    )

                    assert total_size != 0, f"No content to download from {url}"

                    bar = tqdm(
                        total=total_size, desc=f"{filename}", unit="b", smoothing=0.5
                    )
                    # Update the progress bar with the downloaded size
                    bar.update(downloaded_size)

                    download_mode = "wb" if downloaded_size == 0 else "ab"

                    async with aiofiles.open(filename, download_mode) as file:

                        pices_size: int = 8192

                        while True:
                            chunk = await response.content.read(pices_size)
                            if not chunk:
                                break
                            await file.write(chunk)
                            bar.update(len(chunk))
                            downloaded_size += len(chunk)
                    bar.close()

                    # Check if the downloaded size is equal to the total size
                    assert downloaded_size >= total_size, "Download failed"

                    file_exist_size = os.path.getsize(filename)
                    assert file_exist_size >= total_size, "Download failed"

                    assert (
                        enable_filter
                        and downloaded_size > filter_size
                        and file_exist_size > filter_size
                    ), "Download filter failed"

        except Exception as e:

            return other_error_process(e=e)

        # finally success

        else:

            logger.success(f"Download successful for {filename}")

            # Get the size of the downloaded file
            size, unit = convert_bytes_to_megabytes(os.path.getsize(filename))
            json_data = dict(
                status_code=response.status,
                url=url,
                filename=os.path.abspath(filename),
                download_status=True,
                size=f"{size:.2f}{unit}",
            )
            logger.success(json_data)
            return json_data  # type: ignore


@retry_on_error(
    retries=TS_RETRIES,
    process_last_retry_func=process_last_retry_func_mp4_to_delete_filename,
)
async def download_m3u8(url: str, filename: str, proxies: Optional[dict[str, str]]):

    def convert_bytes_to_megabytes(bytes):
        mb = bytes / (1024 * 1024)
        if mb >= 1:
            return mb, "MB"
        kb = bytes / 1024
        if kb >= 1:
            return kb, "KB"
        return bytes, "bytes"

    def other_error_process(e: Exception) -> dict[str, str]:

        logger.error(f"Download failed for {filename}, url: {url}")
        error_type = type(e).__name__
        logger.error(f"Error details: {str(e)},error type: {error_type}")

        return dict(error=str(e), url=url, error_type=error_type, download_status=False)  # type: ignore

    try:
        ensure_file_exists(filename)
        download_class = M3u8_download(
            m3u8_link=url, proxies=proxies, out_path=filename  # type: ignore
        )
        out_path = await download_class.run(to_clear_cache=TO_CLEAR_CACHE)
        out_path = os.path.abspath(out_path)
    except Exception as e:
        return other_error_process(e=e)
    else:
        try:
            size, unit = convert_bytes_to_megabytes(os.path.getsize(filename))
            json_data = dict(
                status_code=200,
                url=url,
                filename=os.path.abspath(filename),
                download_status=True,
                size=f"{size:.2f}{unit}",
                m3u8=True,
            )
            logger.success(json_data)
            return json_data
        except Exception as e:
            return other_error_process(e=e)


# if __name__ == "__main__":
# pass

#  # delete failed file
#         if os.path.exists(filename):
#             os.remove(filename)
#             logger.debug(f"Removed {filename}")
#     ensure_file_exists("test.txt")
#     os.remove("test.txt")
#     ensure_file_exists("test__/test.txt")
#     os.remove("test__/test.txt")
#     os.rmdir("test__")
#     # test exception
#     ensure_file_exists(1)
#     ensure_file_exists(None)

#     def test_get_source():
#         with open(
#             os.path.join(os.path.dirname(__file__), "source.html"),
#             encoding="UTF-8",
#             errors="ignore",
#             mode="w",
#         ) as f:
#             url = "https://hanime1.me/search?genre=%E8%A3%8F%E7%95%AA"
#             s = asyncio.run(get_source(headers=HEADERS, proxies=PROXIES, url=url))
#             f.write(s["source"])

#     def test_parse():
#         with open(
#             os.path.join(os.path.dirname(__file__), "source.html"),
#             encoding="UTF-8",
#             errors="ignore",
#             mode="r",
#         ) as f:
#             s = f.read()
#             result = parse(s)
#             print(result)

# def test_all():
#     url = "https://hanime1.me/watch?v=91668"
#     filename = "test.mp4"
#     source = asyncio.run(get_source(url=url, headers=HEADERS, proxies=PROXIES))
#     json_data = parse(source["source"])

#     print(json_data)

#     asyncio.run(
#         download_mp4_with_progress(
#             url=json_data["contentUrl"], filename=ensure_file_exists(filename)[-1], proxies=PROXIES
#         )
#     )
#     os.remove(filename)

#     logger.success("Test Success !")

# test_all()
# test_get_source()


# from numpy import source
# from sympy import S
# import sys
# from pathlib import Path

# sys.path[0] = str(Path(sys.path[0]).parent)
# import sys

# # from sys import path
# from pathlib import Path

# sys.path.append(str(Path(__file__).parent))
# sys.path.append("..")
# from .. import config


#


# print("\n ,".join(sys.path))

# import os

# print(os.getcwd())

# from config import *
