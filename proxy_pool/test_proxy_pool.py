import aiohttp  # type: ignore
import asyncio
from proxy_pool import ProxyPool

# from proxy_pool.proxy_pool import ProxyPool

from rich import print

proxy_pool = ProxyPool()


async def fetch(url):
    try:
        proxy = next(iter(proxy_pool.next_proxies().values()))
        async with aiohttp.ClientSession() as session:

            print(f"Using proxy: {proxy}")
            async with session.get(url, proxy=proxy, timeout=10) as response:
                html = await response.text()
                print(html)
                await asyncio.sleep(2)
    except:
        print(f"Error:{proxy}")  # type: ignore


async def main():
    url = "https://httpbin.org/ip"
    tasks = [fetch(url) for _ in range(90)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":

    asyncio.run(main())
