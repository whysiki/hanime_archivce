from config import *
from cellfunctions import *
from get_website_structure import get_genre_links, get_all_genres
from path_tools import ensure_file_exists


# 这是下载主类


# 对于单个分类的视频下载
class GetVideo:

    def __init__(self, save_path: str, gengre: str):
        self.save_path: str = save_path
        self.genre: str = gengre
        self.genres: set[str] = set()
        self.links_set_cache: dict[str, set[str]] = {}
        self.links_set_cache_path: str = ensure_file_exists(
            f"cache/links_set_cache_{self.genre}.pkl"
        )[-1]
        self.links_set: set[str] = set()
        self.links_set: set[str] = self.read_cache_links()  # type: ignore

    # 获取全部分类数据, 待用
    @staticmethod
    def get_all_genres():
        genres = asyncio.run(get_all_genres())
        return genres

    @staticmethod
    def clear_cache(gengre: str):
        cache_path = f"cache/links_set_cache_{gengre}.pkl"
        if os.path.exists(cache_path):
            os.remove(cache_path)
            logger.success("清除缓存成功")
        else:
            logger.error("缓存文件不存在")

    # 获取分类链接
    def get_append_genre_link(self, limit_page_number: int = 0):
        links_set = asyncio.run(get_genre_links(self.genre, limit_page_number))
        self.links_set = self.links_set.union(links_set)
        self.genres = self.genres.add(genre)  # type: ignore

        #
        # 保存缓存
        self.links_set_cache[self.genre] = self.links_set
        with open(self.links_set_cache_path, "wb") as f:
            pickle.dump(self.links_set_cache, f)

    # 读取缓存
    def read_cache_links(self):
        try:
            with open(self.links_set_cache_path, "rb") as f:
                cache: dict[str, set[str]] = pickle.load(f)

            assert (
                isinstance(cache, dict)
                and self.genre in cache
                and len(cache[self.genre]) > 0
            ), "读取缓存失败"

            logger.success("读取缓存成功")
            logger.success(
                f"分类: {self.genre}, 缓存链接数量: {len(cache[self.genre])}"
            )
            self.links_set_cache = cache
            return cache[self.genre]

        except:

            try:
                self.get_append_genre_link()
            except Exception as e:
                error_type = type(e).__name__
                logger.error(
                    f"获取分类链接失败, 错误类型: {error_type}, detail: {str(e)}"
                )
                raise e

    async def get_sources(self, number: int = -1) -> list[Dict]:
        async with asyncio.Semaphore(SEMAPHORE_SIZE):
            source_tasks = [
                get_source(url=link, headers=HEADERS, proxies=PROXIES)
                for link in list(self.links_set)[:number]
            ]
            sources_jsons = await asyncio.gather(*source_tasks)
            if not sources_jsons:
                logger.error("全部请求失败")
            return sources_jsons

    def parse_sources(self, sources_jsons) -> list[Dict]:

        with ProcessPoolExecutor(max_workers=MERGE_TS_PROCESSES) as executor:
            parse_tasks = [
                executor.submit(parse, source_json["source"])  # type: ignore
                for source_json in sources_jsons
                if isinstance(source_json, dict)
                and source_json.get("status_code") == 200
            ]

            parse_result_jsons = []
            for future in tqdm(
                parse_tasks, desc="解析进度", total=len(parse_tasks), unit="个"
            ):
                result = future.result()
                parse_result_jsons.append(result)

            if not parse_result_jsons:
                logger.error("全部解析失败")

            return parse_result_jsons

    async def download_videos(self, parse_result_jsons, number: int = -1):

        async with asyncio.Semaphore(SEMAPHORE_SIZE):

            download_tasks = [
                download_mp4_with_progress(
                    url=parse_result_json.get("contentUrl"),  # type: ignore
                    filename=ensure_file_exists(
                        os.path.join(
                            self.save_path,
                            f"{self.genre}",
                            f'{parse_result_json.get("name")}.mp4',
                        )
                    )[-1],
                    proxies=PROXIES,
                )
                for parse_result_json in parse_result_jsons[:number]
                if isinstance(parse_result_json, dict)
                and parse_result_json.get("contentUrl")
                and parse_result_json.get("name")
            ]

            result = await asyncio.gather(*download_tasks)  # type: ignore

            if not result:
                logger.error("全部下载失败")

            return result

    async def download_m3u8_videos(self, m3u8_params: list[dict]):
        download_tasks = [
            download_m3u8(
                url=m3u8_param.get("url"),  # type: ignore
                filename=m3u8_param.get("filename"),  # type: ignore
                proxies=PROXIES,
            )
            for m3u8_param in m3u8_params
        ]
        result = await asyncio.gather(*download_tasks)  # type: ignore
        if not result:
            logger.error("全部下载失败")
        return result

    async def process_links(self, number: int = -1):

        sources_jsons: list[dict] = await self.get_sources(number=number)

        parse_result_jsons: list[dict] = self.parse_sources(sources_jsons)

        download_result_dicts = await self.download_videos(
            parse_result_jsons, number=number
        )

        m3u8_params = [
            d
            for d in download_result_dicts
            if d.get("m3u8")
            and d.get("url")
            and d.get("filename")
            and not d.get("error")
            and not d.get("mp4")
        ]

        if m3u8_params:
            results = await self.download_m3u8_videos(m3u8_params)

        else:
            results = download_result_dicts

        print(results)


if __name__ == "__main__":

    get_video = GetVideo(save_path=SAVE_PATH, gengre="裏番")
    asyncio.run(get_video.process_links(number=2))
    print("下载完成")
    # get_video.get_sources(number=200)
    # number : wanna download number for this gengre

    # 获取全部分类
    # all_genres = GetVideo.get_all_genres() {'泡麵番', '裏番', 'Cosplay', '3D動畫', '同人作品', 'Motion Anime'}
    # print(
    #     all_genres
    # #)  # {'泡麵番', '裏番', 'Cosplay', '3D動畫', '同人作品', 'Motion Anime'}
    #     get_video = GetVideo(save_path="videos", gengre=genre)

    # if not get_video.links_set:
    # get_video = GetVideo(save_path="videos", gengre="裏番")
    # asyncio.run(get_video.process_links(number=20))
    # print("下载完成")

    # 清除缓存
    # GetVideo.clear_cache(gengre="泡麵番")

    # for genre in {"泡麵番", "裏番", "Cosplay", "3D動畫", "同人作品", "Motion Anime"}:
    #    get_video = GetVideo(save_path="videos", gengre=genre)
