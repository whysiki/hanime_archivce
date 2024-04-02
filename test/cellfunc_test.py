import asyncio
import os
import unittest
from cellfunctions import (
    get_source,
    download_mp4_with_progress,
    parse,
    ensure_file_exists,
    HEADERS,
    PROXIES,
)


class TestYourModule(unittest.TestCase):
    def test_get_source(self):
        url = "https://hanime1.me/watch?v=91668"
        source = asyncio.run(get_source(url=url, headers=HEADERS, proxies=PROXIES))

        self.assertTrue("source" in source)
        self.assertTrue("status_code" in source)
        self.assertTrue("url" in source)

    def test_download_mp4_with_progress(self):
        url = "https://hanime1.me/watch?v=91668"
        filename = "test.mp4"
        source = asyncio.run(get_source(url=url, headers=HEADERS, proxies=PROXIES))
        json_data = parse(source["source"])

        asyncio.run(
            download_mp4_with_progress(
                url=json_data["contentUrl"],  # type: ignore
                filename=ensure_file_exists(filename)[-1],
                proxies=PROXIES,
            )
        )

        self.assertTrue(os.path.exists(filename))
        os.remove(filename)


if __name__ == "__main__":
    unittest.main()
