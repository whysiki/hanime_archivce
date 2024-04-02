from m3u8tools.download_m3u8_file import M3u8_download
import os
import asyncio

# from proxy_pool import ProxyPool

if __name__ == "__main__":
    test_link = r"https://abre-videos.cdn1122.com/_hls/videos/0/d/6/e/3/0d6e33445e36dadbf213772c24aa519c1636378323-1440-1080-4487-h264.mp4/master.m3u8?validfrom=1711889419&validto=1712062219&rate=861504&hdl=-1&hash=B8ehz0UX%2FsQ1JUE37bz%2BRrWI9JI%3D"

    d = M3u8_download(
        m3u8_link=test_link,
        proxies={
            "http://": "http://127.0.0.1:62333",
            "https://": "http://127.0.0.1:62333",
        },
        out_path=os.path.join(os.path.dirname(__file__), "video", "test_outpath.mp4"),
    )

    d.batch_size = 20

    asyncio.run(d.run(to_clear_cache=False))
