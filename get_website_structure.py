from config import *
from cellfunctions import *


# 下面函数用于获取网站的结构
# 1. 获取所有分类
# 2. 获取每个分类的最大页数
# 3. 获取每个分类每一页的链接集合


async def get_max_page(genre: str) -> int:
    params = {"genre": genre, "page": "1"}
    url = urljoin(HOST, "/search") + "?" + urlencode(params)
    re: dict = await get_source(url=url, headers=HEADERS, proxies=PROXIES)
    if isinstance(re, dict) and re.get("status_code") != 200:
        logger.error(f"获取最大页数失败")
        # 1 at least
        return 1

    soup = BeautifulSoup(re["source"], "html.parser")
    page_items = soup.select('ul.pagination[role="navigation"]>li.page-item')
    pages_number_list = sorted(
        [i.text for i in page_items if i.text.strip().replace("\n", "").isdigit()],
        key=lambda x: int(x),
    )
    # 1 at least
    max_page: int = max(int(pages_number_list[-1]), 1)
    logger.success(f"分类:{genre},最大页数:{max_page}")
    return max_page


async def get_single_page_links(genre: str, page: int) -> set[str]:
    params = {"genre": genre, "page": str(page)}
    url = urljoin(HOST, "/search") + "?" + urlencode(params)
    re: dict = await get_source(url=url, headers=HEADERS, proxies=PROXIES)
    if isinstance(re, dict) and re.get("status_code") != 200:
        logger.error(f"分类:{genre},第{page}页获取失败")
        return set()

    await asyncio.sleep(random.randint(RANDOM_SLEEP_RANGE[0], RANDOM_SLEEP_RANGE[1]))

    soup = BeautifulSoup(re.get("source"), "html.parser")  # type: ignore
    # 解析
    # {'泡麵番', '裏番', 'Cosplay', '3D動畫', '同人作品', 'Motion Anime'}
    locators_dict: dict[str, str] = {
        "裏番": "div.home-rows-videos-wrapper > a[style='text-decoration: none;']",
        "泡麵番": """html body div div form#hentai-form div#home-rows-wrapper.search-rows-wrapper div.home-rows-videos-wrapper a""",
        "Cosplay": """html body div div form#hentai-form div#home-rows-wrapper.search-rows-wrapper div.content-padding-new div.row.no-gutter div.col-xs-6.col-sm-4.col-md-2.search-doujin-videos.hidden-xs.hover-lighter.multiple-link-wrapper a.overlay""",
        "3D動畫": """html body div div form#hentai-form div#home-rows-wrapper.search-rows-wrapper div.content-padding-new div.row.no-gutter div.col-xs-6.col-sm-4.col-md-2.search-doujin-videos.hidden-xs.hover-lighter.multiple-link-wrapper a.overlay""",
        "同人作品": """html body div div form#hentai-form div#home-rows-wrapper.search-rows-wrapper div.content-padding-new div.row.no-gutter div.col-xs-6.col-sm-4.col-md-2.search-doujin-videos.hidden-xs.hover-lighter.multiple-link-wrapper a.overlay""",
        "Motion Anime": """html body div div form#hentai-form div#home-rows-wrapper.search-rows-wrapper div.content-padding-new div.row.no-gutter div.col-xs-6.col-sm-4.col-md-2.search-doujin-videos.hidden-xs.hover-lighter.multiple-link-wrapper a.overlay""",
    }

    a_elems = soup.select(
        # "div.home-rows-videos-wrapper > a[style='text-decoration: none;']"
        locators_dict[genre]
    )

    # 处理
    links_set = {i.get("href", "").strip() for i in a_elems}  # type: ignore
    logger.success(f"分类:{genre},第{page}页获取成功")
    logger.success(f"分类:{genre},当前页共有{len(links_set)}个链接")
    return links_set


async def get_genre_links(genre: str, limit_page_number: int = 0) -> set[str]:
    async with asyncio.Semaphore(SEMAPHORE_SIZE):
        # 如果没有限制
        if limit_page_number == 0:
            max_page: int = await get_max_page(genre)
        # 反之取最小值
        else:
            max_page: int = min(await get_max_page(genre), limit_page_number)

        tasks = [get_single_page_links(genre, page) for page in range(1, max_page + 1)]
        results = await asyncio.gather(*tasks)

        final_result = set().union(*results)

        final_result.discard("")

        return final_result


async def get_all_genres() -> set[str]:
    re: dict = await get_source(url=HOST, headers=HEADERS, proxies=PROXIES)
    if isinstance(re, dict) and re.get("status_code") != 200:
        logger.error("获取主页失败")
        return set()
    seletor = """a.nav-item.hidden-xs.nav-desktop-items[href^="https://hanime1.me/search?genre="]"""
    soup = BeautifulSoup(re.get("source"), "html.parser")  # type: ignore
    genre_ = soup.select(seletor)
    genre__set = {i.text.strip() for i in genre_}
    logger.success("获取主页成功")

    return genre__set
