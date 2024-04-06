# 动态合并.py
from tempfile import tempdir
from m3u8tools import merge_mp4_files_ffmpeg, ensure_file_exists
import os
import shutil
import asyncio
import unittest


def merge_files(test_data):
    current = os.path.dirname(__file__)
    out_file = os.path.join(current, "test.mp4")
    ensure_file_exists(out_file)

    list_dir = [i for i in os.listdir(test_data) if os.path.splitext(i)[-1] == ".ts"]

    tempdir = os.path.join(current, "tem_ts")

    input_files = []

    for i in list_dir:

        in_ = os.path.join(test_data, i)
        out = os.path.join(tempdir, i)

        ensure_file_exists(out)

        shutil.copyfile(in_, out)

        input_files.append(out)

    a = merge_mp4_files_ffmpeg(
        temp_dir=os.path.join(current, "tem_merge"),
        input_files=input_files,
        output_file=out_file,
    )
    os.remove(out_file)
    shutil.rmtree(tempdir)
    shutil.rmtree(os.path.join(current, "tem_merge"))

    return a


class TestMergeFiles(unittest.TestCase):
    def test_merge_files(self):
        test_data = r"D:\3DS\test\hanime_archivce\m3u8tools\temp_ts_cache\0926dc0889cb9824bea5fdd63bebbcea"
        result = merge_files(test_data)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
