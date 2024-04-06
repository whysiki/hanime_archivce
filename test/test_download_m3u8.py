from main import GetVideo, asyncio, SAVE_PATH, os
import unittest


class TestMergeFiles(unittest.TestCase):
    def test_merge_files(self):
        get_video = GetVideo(save_path=SAVE_PATH, gengre="裏番")
        output_file = "test.mp4"
        test_m3u8_params = [
            dict(
                url=r"https://abre-videos.cdn1122.com/_hls/videos/a/e/d/1/c/aed1c468900a065a4c2149ac4ebe76371634067843-1440-1080-1131-h264.mp4/master.m3u8?validfrom=1712255163&validto=1712427963&rate=217152&hdl=-1&hash=ugYpGXoMaeLtGUEKd6X6IfioHF4%3D",
                filename=output_file,
            )
        ]
        result = asyncio.run(get_video.download_m3u8_videos(test_m3u8_params))
        self.assertIsNotNone(result)
        os.remove(output_file)


if __name__ == "__main__":
    unittest.main()
