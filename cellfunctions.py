from config import *
from assert_result_function import parse_assert_result, source_assert_result  #
from retry_decorator import *
from sqlite_cache_decorator import sync_unit_cache_sqlite, async_unit_cache_sqlite
import re
import fake_useragent
from m3u8tools.download_m3u8_file import M3u8_download
from redirect_m3u8_decorator import redirect_m3u8_decorator
from aiohttp import ClientSession, ClientTimeout, TCPConnector

# from aiohttp.client_exceptions import (
# ClientConnectorError,
# ServerDisconnectedError,
# ClientResponseError,
# )


@retry_on_error(retries=GET_SOURSE_RETRIES)
@async_unit_cache_sqlite(
    assert_result=source_assert_result, cache_path=SOURCE_CACHE_DIR
)
async def get_source(url: str, headers: dict, proxies: dict[str, str]) -> dict:
    """
    异步获取网页源代码。

    参数:
    url (str): 需要获取源代码的网页URL。
    headers (dict): HTTP请求头。
    proxies (dict[str, str]): 代理服务器的信息。

    返回:
    dict: 包含源代码、状态码和URL的字典。如果获取失败，返回包含错误信息和URL的字典。
    """
    try:
        if not url:
            raise ValueError("URL不能为空。")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=url, headers=headers, proxy=next(iter(proxies.values()), None)
            ) as response:
                if response.status != 200:
                    raise ValueError(f"状态码: {response.status}")

                # 定义一个正则表达式，用于匹配 HTML 标签
                html_tag_pattern = re.compile(
                    r"<html[^>]*>.*?</html>", re.IGNORECASE | re.DOTALL
                )

                # 使用 assert 语句来检查 re.text 是否包含 <html> 标签
                response_text = await response.text()
                if len(re.findall(html_tag_pattern, string=response_text)) == 0:
                    raise ValueError("response.text 不是一个 HTML 文档")

                logger.success(f"成功获取 {url} 的源代码")

                return dict(source=response_text, status_code=response.status, url=url)
    except (
        # ClientConnectorError,
        # ServerDisconnectedError,
        # ClientResponseError,
        # ValueError,
        Exception
    ) as e:
        error_type = type(e).__name__
        logger.error(
            f"获取 {url} 的源代码失败。错误详情: {str(e)}, 错误类型: {error_type}"
        )
        return dict(error=str(e), url=url, error_type=error_type)


@sync_unit_cache_sqlite(assert_result=parse_assert_result, cache_path=PARSE_CACHE_DIR)
def parse(source: str, to_print_json: bool = False) -> Dict[str, Union[str, bool]]:
    """
    解析 JSON 数据。

    参数:
    source (str): 需要解析的源代码。
    to_print_json (bool): 是否打印解析后的 JSON 数据。

    返回:
    dict: 包含解析后的数据的字典。如果解析失败，返回包含错误信息的字典。
    """
    try:
        if not source:
            raise ValueError("源代码为空。")

        soup = BeautifulSoup(source, "html.parser")
        json_scripts = soup.find_all("script", type="application/ld+json")

        for script in json_scripts:
            cleaned_json_data = (
                script.text.replace("\n", "").replace("\t", "").replace(" ", "").strip()
            )

            url_pattern = r'"contentUrl":"(https?://[^"]+)",'
            contentUrl = re.findall(url_pattern, cleaned_json_data)[0].strip()
            if not contentUrl or ".mp4" not in contentUrl:
                raise ValueError("解析 contentUrl 失败")

            name_pattern = r'"name":"([^"]+)",'
            name = re.findall(name_pattern, cleaned_json_data)[0].strip()
            # 去除路径字符和空格
            name.replace(" ", "")
            invalid_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|", "'"]
            for char in invalid_chars:
                name = name.replace(char, "")
            if not name:
                raise ValueError("解析 name 失败")

            description = re.findall(r'"description":"([^"]+)",', cleaned_json_data)[
                0
            ].strip()
            if not description:
                raise ValueError("解析 description 失败")

            uploadDate = re.findall(r'"uploadDate":"([^"]+)",', cleaned_json_data)[
                0
            ].strip()
            if not uploadDate:
                raise ValueError("解析 uploadDate 失败")

            json_data = dict(
                name=name,
                contentUrl=contentUrl,
                description=description,
                uploadDate=uploadDate,
            )

            # 打印 JSON 数据
            if to_print_json:
                print(json_data)

            logger.success(f"解析 JSON 数据成功: {json_data}")

            return json_data

    # except (IndexError, ValueError) as e:
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"解析失败: {str(e)}, 错误类型: {error_type}")
        return dict(error=str(e), error_type=error_type)
    return dict(error="Unknown error")


# 将字节转换为兆字节
def convert_bytes_to_megabytes(bytes: int) -> Tuple[float, str]:
    """
    将字节转换为兆字节或千字节。

    参数:
    bytes (int): 需要转换的字节数。

    返回:
    tuple: 包含转换后的数值和单位的元组。
    """
    mb = bytes / (1024 * 1024)
    if mb >= 1:
        return mb, "MB"
    kb = bytes / 1024
    if kb >= 1:
        return kb, "KB"
    return bytes, "bytes"


def get_random_user_agent() -> str:
    """
    获取随机的用户代理字符串。

    返回:
    str: 随机的用户代理字符串。
    """
    ua: fake_useragent.UserAgent = fake_useragent.UserAgent()
    return ua.random  # type: ignore


def handle_down_other_error(
    e: Exception, filename: str, url: str
) -> Dict[str, Union[str, bool]]:
    """
    处理下载过程中的异常。

    参数:
    e (Exception): 异常实例。
    filename (str): 文件名。
    url (str): URL。

    返回:
    dict: 包含错误信息、URL、错误类型和下载状态的字典。
    """
    logger.error(f"下载失败，文件名：{filename}，URL：{url}")
    error_type = type(e).__name__
    logger.error(f"错误详情：{str(e)}，错误类型：{error_type}")

    return dict(error=str(e), url=url, error_type=error_type, download_status=False)  # type: ignore


def create_session() -> ClientSession:
    """
    创建一个 aiohttp.ClientSession 实例。

    返回:
    aiohttp.ClientSession: 一个配置好的 aiohttp.ClientSession 实例。
    """
    timeout: ClientTimeout = ClientTimeout(total=TIME_OUT)
    connector: TCPConnector = TCPConnector(
        verify_ssl=False,
        limit=AIOHTTP_CONNECTION_LIMIT,
        enable_cleanup_closed=True,
        ttl_dns_cache=None,
        use_dns_cache=True,
        force_close=True,
        timeout_ceil_threshold=30,
    )
    return ClientSession(
        headers={"User-Agent": get_random_user_agent()},
        connector=connector,
        timeout=timeout,
    )


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
    """
    异步下载 MP4 文件并显示进度。

    参数:
    url (str): MP4 文件的 URL。
    filename (str): 保存 MP4 文件的文件名。
    proxies (Optional[dict[str, str]]): 代理服务器的信息。
    filter_size (int): 过滤器的大小。
    enable_filter (bool): 是否启用过滤器。

    返回:
    dict: 包含下载状态和文件信息的字典。如果下载失败，返回包含错误信息的字典。
    """
    try:
        if not url or not filename or ".mp4" not in url or ".mp4" not in filename:
            raise ValueError(f"URL 或文件名不正常，{url}, {filename}")

        if ".m3u8" in url:
            return dict(
                error="不支持 m3u8 文件",
                url=url,
                download_status=False,
                filename=filename,
                m3u8=True,
            )

        if not To_DOWNLOAD_MP4:
            logger.debug(f"关闭 MP4 下载 : {filename}")
            file_path: Path = Path(filename)
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"删除预生成空文件: {filename}")
            return dict()

        proxy: Optional[str] = next(iter(proxies.values()), None) if proxies else None

        if not proxy:
            logger.warning(f"download_mp4_with_progress 代理为空或 None.")

    except Exception as e:
        return handle_down_other_error(e, filename, url)

    else:
        try:
            session: ClientSession = create_session()
            file_path: Path = Path(filename)
            downloaded_size: int = file_path.stat().st_size if file_path.exists() else 0
            headers: dict[str, str] = (
                {"Range": f"bytes={downloaded_size}-"} if downloaded_size else {}
            )
            async with session.get(url, proxy=proxy, headers=headers) as response:
                if response.status not in [200, 206, 416]:
                    raise ValueError(
                        f"下载失败，文件名：{filename}，状态码：{response.status}，URL：{url}"
                    )
                total_size: int = (
                    int(response.headers.get("content-length", 0)) + downloaded_size
                )
                if total_size == 0:
                    raise ValueError(f"URL {url} 没有内容可以下载")
                bar = tqdm(
                    total=total_size, desc=f"{filename}", unit="b", smoothing=0.5
                )
                bar.update(downloaded_size)
                download_mode: str = "wb" if downloaded_size == 0 else "ab"
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
                if (
                    downloaded_size < total_size
                    or file_path.stat().st_size < total_size
                ):
                    raise ValueError("下载失败")
                if enable_filter and (
                    downloaded_size <= filter_size
                    or file_path.stat().st_size <= filter_size
                ):
                    raise ValueError("下载过滤失败")

        except Exception as e:
            return handle_down_other_error(e, filename, url)

        else:
            logger.success(f"下载成功，文件名：{filename}")
            size, unit = convert_bytes_to_megabytes(file_path.stat().st_size)
            json_data: Dict[str, Union[str, bool]] = dict(
                status_code=response.status,
                url=url,
                filename=str(file_path.resolve()),
                download_status=True,
                size=f"{size:.2f}{unit}",
            )  # type: ignore
            logger.success(json_data)
            return json_data


@retry_on_error(
    retries=TS_RETRIES,
    process_last_retry_func=process_last_retry_func_mp4_to_delete_filename,
)
async def download_m3u8(
    url: str, filename: str, proxies: Optional[dict[str, str]]
) -> Dict[str, Union[str, bool]]:
    """
    异步下载 m3u8 文件。

    参数:
    url (str): m3u8 文件的 URL。
    filename (str): 保存 m3u8 文件的文件名。
    proxies (Optional[dict[str, str]]): 代理服务器的信息。

    返回:
    dict: 包含下载状态和文件信息的字典。如果下载失败，返回包含错误信息的字典。
    """
    try:
        ensure_file_exists(filename)
        download_class = M3u8_download(
            m3u8_link=url, proxies=proxies, out_path=filename  # type: ignore
        )
        out_path = await download_class.run(to_clear_cache=TO_CLEAR_CACHE)
        out_path = os.path.abspath(out_path)
    except Exception as e:
        return handle_down_other_error(e, filename, url)

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
        return json_data  # type: ignore
    except Exception as e:
        return handle_down_other_error(e, filename, url)
