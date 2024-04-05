from tempfile import tempdir
from m3u8tools import merge_mp4_files_ffmpeg, ensure_file_exists
import os
import shutil
import asyncio

current = os.path.dirname(__file__)


test_data = r"D:\3DS\test\hanime_archivce\m3u8tools\temp_ts_cache\58ebfc77c2688becd77d5ec1788cf264"

list_dir = [
    # os.path.join(test_data, i)
    i
    for i in os.listdir(test_data)
    if os.path.splitext(i)[-1] == ".ts"
]


tempdir = os.path.join(current, "tem_ts")

input_files = []

for i in list_dir:

    in_ = os.path.join(test_data, i)
    out = os.path.join(tempdir, i)

    ensure_file_exists(out)

    shutil.copyfile(in_, out)

    input_files.append(out)


out_file = os.path.join(current, "test.mp4")
ensure_file_exists(out_file)

if __name__ == "__main__":

    a = merge_mp4_files_ffmpeg(
        temp_dir=os.path.join(current, "tem_merge"),
        input_files=input_files,
        output_file=out_file,
        max_processes=2,
        batch_size=10,
        # overwrite=True,
    )

    assert a

    os.remove(out_file)

    shutil.rmtree(tempdir, ignore_errors=True)
    shutil.rmtree(os.path.join(current, "tem_merge"), ignore_errors=True)
    shutil.rmtree(os.path.join(current, "test_download"), ignore_errors=True)

    # asyncio.run(
    #     seg_to_mp4_async(
    #         input_file=out_file,
    #         output_file=out_file.replace(".ts", ".mp4"),
    #         overwrite=True,
    #     )
    # )

    # assert a
