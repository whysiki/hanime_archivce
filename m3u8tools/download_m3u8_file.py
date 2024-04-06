from m3u8tools.__init__ import *

# # Configuration file
from config import (
    TS_RETRIES,
    TIME_OUT,
    TS_SEMAPHORE_SIZE,
    PROXIES_POOL,
)


class M3u8_download:

    PROXY_POOL = PROXIES_POOL  # 至少有一个(method) def next_proxies() -> dict[str, str]

    TS_RETRY: int = TS_RETRIES

    TS_DOWNLOAD_TIMEOUT: int = TIME_OUT

    SEM: int = TS_SEMAPHORE_SIZE

    def __init__(
        self, m3u8_link: str, proxies: dict, out_path: str, headers: dict = {}
    ) -> None:

        self.headers = self.read_dafault_headers() if not headers else headers

        self.proxies: dict = proxies

        self.m3u8_link = m3u8_link

        self.base_link: str = self.get_base_link()

        self.temp_dowload_directory = os.path.join(
            os.path.dirname(__file__),
            "temp_ts_cache",
            hashlib.md5(self.m3u8_link.encode()).hexdigest(),
        )

        os.makedirs(self.temp_dowload_directory, exist_ok=True)

        self.initial_text: str = ""

        self.index_link: str = ""

        self.seg_link_list: list[tuple[int, str]] = []

        self.seg_index_url_path_list: list[tuple[int, str, str]] = []

        self.result_dict: dict = {}

        self.resolutions: list[str] = []

        self.codecs: list[str] = []

        self.frame_rate: str = ""

        self.command_list: list[str] = []

        self.out_path = out_path

        logger.success("初始化m3u8下载类完成")

    def read_dafault_headers(self, to_read_cookie: bool = True):

        headers = read_headers_from_json(
            headers_example=os.path.join(
                os.path.dirname(__file__), "m3u8ch", "headers.json"
            ),
            to_read_cookie=to_read_cookie,
            cookie_json_filepath=os.path.join(
                os.path.dirname(__file__), "m3u8ch", "cookie.json"
            ),
        )
        return headers

    def get_base_link(self):
        # 匹配以 ".mp4/" 结尾的部分
        pattern = r"(https://.*\.mp4/)master.m3u8?"
        match = re.findall(pattern, self.m3u8_link.strip())  # type: ignore

        assert (
            match and isinstance(match[0], str) and "videos" in match[0]
        ), "匹配base_link错误"

        base_link = match[0]

        logger.success("基础链接获取完成")

        return base_link

    def get_index(self):
        response = requests.get(
            url=self.m3u8_link, headers=self.headers, proxies=self.proxies
        )
        assert response.status_code == 200, "response.status_code != 200"

        text = response.text

        assert text and isinstance(text, str) and "#EXTM3U" in text, "文本内容错误"

        self.initial_text = text

        pattern = r"(index-.*?m3u8.*?\n)"

        match = re.findall(pattern=pattern, string=text)

        assert match and isinstance(match[0], str)

        index_url = match[0].strip()

        self.index_link = self.base_link + index_url

        logger.success("索引链接获取完成")

        return self.index_link

    def get_resolutions(self):

        if not self.resolutions:

            self.get_index()

        pattern = r"RESOLUTION=(\d+)x(\d+)"

        match = re.findall(pattern=pattern, string=self.initial_text)

        assert match, "分辨率匹配失败"

        match = match[0]

        self.resolutions = [match[0], "x", match[1]]

        logger.success(f"分辨率获取完成,分辨率为:{self.resolutions}")

        return self.resolutions

    def get_frame_rate(self):

        if not self.frame_rate:

            self.get_index()

        pattern = r"FRAME-RATE=(\d+\.\d+)"

        match = re.findall(pattern=pattern, string=self.initial_text)

        if not match:

            pattern = r"FRAME-RATE=(\d+),"

            match = re.findall(pattern=pattern, string=self.initial_text)

        assert match, "帧率匹配失败"

        match = match[0]

        self.frame_rate = match

        logger.success(f"帧率获取完成,帧率为:{self.frame_rate}")

        return self.frame_rate

    def get_command_lsit(self) -> list[str]:

        command_list: list[str] = []

        if self.resolutions and len(self.resolutions) == 3:

            command_list.extend(["-s", f"{self.resolutions[0]}x{self.resolutions[2]}"])

        if self.frame_rate:

            command_list.extend(["-r", self.frame_rate])

        self.command_list = command_list

        return self.command_list

    def get_seg_link_list(self) -> list[tuple[int, str]]:

        response = requests.get(
            url=self.index_link, headers=self.headers, proxies=self.proxies
        )
        assert response.status_code == 200, "response.status_code != 200"

        text = response.text

        # 定义正则表达式模式
        # pattern = r"seg-(\d+-v1)-a1\.ts\?validfrom=\d+&validto=\d+&rate=\d+&hdl=-\d+&hash=[\w%]+"

        pattern = r"(seg-)(.*?)(-v1-a1\.ts\?validfrom=\d+&validto=\d+&rate=\d+&hdl=-\d+&hash=[\w%]+)\n"

        # 使用正则表达式匹配所有的ts文件链接
        match = re.findall(pattern=pattern, string=text)

        # print(match.__len__())
        for i in match:
            # print(i)
            seg_link = self.base_link + i[0] + i[1] + i[2]
            self.seg_link_list.append((int(i[1]), seg_link))

        logger.success("所有分片链接获取完成")

        return self.seg_link_list

    @staticmethod  # type: ignore
    def download_seg_callback(kargs, proxy_pool=PROXY_POOL):

        next_proxies = proxy_pool.next_proxies()

        kargs["proxies_download_seg"] = next_proxies

        logger.debug(f"下载分片失败, 重新下载, 下一个代理地址:{next_proxies}")

        return kargs

    @retry_on_error_defalut_no_raise_error(
        retries=TS_RETRY, callbackfunc=download_seg_callback
    )
    async def download_seg(
        self, seg_url: str, seg_index: int, proxies_download_seg: dict[str, str] = {}
    ) -> tuple[int, str, str]:

        timeoutaio = aiohttp.ClientTimeout(total=self.TS_DOWNLOAD_TIMEOUT)

        # 配置TCPConnector连接

        connector = aiohttp.TCPConnector(
            verify_ssl=False,
            limit=700,
            enable_cleanup_closed=True,
            ttl_dns_cache=None,
            use_dns_cache=True,
            force_close=True,
            timeout_ceil_threshold=30,
            # keepalive_timeout=30,
        )

        proxies: dict[str, str] = (
            proxies_download_seg
            if proxies_download_seg
            and isinstance(proxies_download_seg, dict)
            and len(proxies_download_seg) == 2
            else self.proxies
        )

        async with aiohttp.ClientSession(
            timeout=timeoutaio, connector=connector  # type: ignore
        ) as session:

            seg_path = os.path.join(self.temp_dowload_directory, f"seg{seg_index}.ts")

            # 初始化下载大小
            downloaded_size = 0
            if (
                os.path.exists(seg_path)
                and os.path.isfile(seg_path)
                and os.path.getsize(seg_path) > 0
            ):
                # 获取已下载的文件大小
                downloaded_size = os.path.getsize(seg_path)

            headers = self.headers
            # 如果已下载的文件大小大于0，则添加Range字段
            if downloaded_size > 0:
                headers["Range"] = f"bytes={downloaded_size}-"

            async with session.get(
                seg_url, headers=headers, proxy=next(iter(proxies.values()), None)
            ) as response:

                # logger.debug(f"下载分片{seg_index}.ts, 状态码:{response.status}")

                assert (
                    response.status == 200
                    or response.status == 206  # 206 Partial Content
                    or response.status == 416
                ), f"response.status != 200 or 206 or 416"

                # 获取待下载文件总大小
                total_size = (
                    int(response.headers.get("Content-Length", 0)) + downloaded_size
                )

                assert total_size > 0, "total_size <= 0"
                bar = tqdm.tqdm(
                    total=total_size,  # type: ignore
                    initial=downloaded_size,
                    unit="B",
                    unit_scale=True,
                    desc=f"seg{seg_index}.ts",
                )
                downloaded_mode = "ab" if downloaded_size > 0 else "wb"

                ensure_file_exists(seg_path)

                async with aiofiles.open(seg_path, downloaded_mode) as f:
                    pices: int = 1024
                    while True:
                        chunk = await response.content.read(pices)
                        if not chunk:
                            break
                        await f.write(chunk)
                        bar.update(len(chunk))
                        downloaded_size += len(chunk)
                bar.close()

                assert downloaded_size == total_size, "下载文件大小不一致"

                file_exist_size = os.path.getsize(seg_path)

                assert file_exist_size == total_size, "下载文件大小不一致"

                if file_exist_size > 200:

                    logger.success(
                        f"下载分片{seg_index}.ts完成,大小:{file_exist_size}, link: {seg_url}"
                    )
                else:
                    logger.warning(
                        f"下载分片{seg_index}.ts完成,大小:{file_exist_size}, link: {seg_url}"
                    )

                return seg_index, seg_url, seg_path  # 返回三元组 , 用于后续转换

    async def download_all_seg(self) -> list[tuple[int, str, str]]:

        sem = asyncio.Semaphore(self.SEM)

        async with sem:

            tasks = []
            for seg_index, seg_url in self.seg_link_list:
                task = asyncio.create_task(self.download_seg(seg_url, seg_index))
                tasks.append(task)

            seg_index_url_path_list: list[tuple[int, str, str]] = await asyncio.gather(
                *tasks
            )

            seg_index_url_path_list_remove_none = [
                i for i in seg_index_url_path_list if i
            ]  # 去除None

            assert len(seg_index_url_path_list_remove_none) == len(
                self.seg_link_list
            ), "下载文件与ts链接数量不一致"

            self.seg_index_url_path_list = seg_index_url_path_list

            logger.success("所有分片下载完成")

            return self.seg_index_url_path_list

    def merge_mp4_files(self) -> str:

        assert self.count_ts_mp4_files()[1] == len(
            self.seg_link_list
        ), "ts文件数量与分片数量不一致"

        ts_files = [path for index, url, path in self.seg_index_url_path_list]

        ts_files.sort(key=lambda x: int(x.split("seg")[1].split(".")[0]))

        ensure_file_exists(self.out_path)

        logger.debug(f"开始合并, 输出路径:{self.out_path},数量:{len(ts_files)}")

        command_list = self.get_command_lsit()

        # logger.debug(f"合并参数:{self.command_list}")

        # logger.debug(f"合并文件列表:{ts_files}")

        issuccess = merge_mp4_files_ffmpeg(
            input_files=ts_files,
            output_file=self.out_path,
            temp_dir=os.path.join(self.temp_dowload_directory, "temp_merge_mp4_cache"),
            command_list=command_list,
        )

        assert issuccess, "合并失败"

        logger.success("合并完成")

        return self.out_path

    def info(self) -> None:

        # 打印属性相关信息
        print(f"base_link: {self.base_link}")
        print(f"index_link: {self.index_link}")
        print(f"temp_dowload_directory: {self.temp_dowload_directory}")
        print(f"seg_link_list: {self.seg_link_list}")

        print(f"resolutions: {self.resolutions}")

        print(f"frame_rate: {self.frame_rate}")

        print(f"initial_text: {self.initial_text}")

        print(f"command_list: {self.command_list}")

    def count_ts_mp4_files(self) -> tuple[bool, int, int]:

        def count_files_with_extension(directory, extension):
            return len(list(Path(directory).glob(f"*.{extension}")))

        def ts_mp4_file_count_equal(directory):
            ts_count = count_files_with_extension(directory, "ts")
            mp4_count = count_files_with_extension(directory, "mp4")
            return (ts_count == mp4_count, ts_count, mp4_count)

        return ts_mp4_file_count_equal(self.temp_dowload_directory)

    def clear_cache(self):
        # list_cache = os.walk()
        shutil.rmtree(self.temp_dowload_directory)  # type: ignore

        logger.success(f"清空缓存文件夹:{self.temp_dowload_directory}")

    async def run(self, to_clear_cache: bool = True):

        self.get_index()
        self.get_seg_link_list()
        self.get_resolutions()
        self.get_frame_rate()
        logger.info(f"ts链接数量: {len(self.seg_link_list)}")
        await self.download_all_seg()
        logger.info(f"已下载ts文件数量: {len(self.seg_index_url_path_list)}")
        self.merge_mp4_files()

        if to_clear_cache:

            self.clear_cache()

        else:

            logger.info(f"未清空缓存{self.temp_dowload_directory}")

        return self.out_path
