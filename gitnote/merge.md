D:\3DS\test\hanime_videos_spider>git checkout --orphan new-branch
Switched to a new branch 'new-branch'

D:\3DS\test\hanime_videos_spider>git add -A     #-A 选项表示添加所有更改，包括被 Git 管理的文件和未被 Git 管理的文件。

D:\3DS\test\hanime_videos_spider>git commit -m "Merge all commits into one"
[new-branch (root-commit) bccd90a] Merge all commits into one
 28 files changed, 3179 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 .vscode/settings.json
 create mode 100644 README.md
 create mode 100644 _cookies_.json
 create mode 100644 _headers_example.json
 create mode 100644 assert_result_function.py
 create mode 100644 cache_decorator.py
 create mode 100644 cellfunctions.py
 create mode 100644 config.py
 create mode 100644 get_website_structure.py
 create mode 100644 git_deleted_track.bat
 create mode 100644 m3u8tools/__init__.py
 create mode 100644 m3u8tools/download_m3u8_file.py
 create mode 100644 m3u8tools/m3u8ch/cookie.json
 create mode 100644 m3u8tools/m3u8ch/headers.json
 create mode 100644 m3u8tools/test/test.ts
 create mode 100644 "m3u8tools/test/\345\212\250\346\200\201\345\220\210\345\271\266.py"
 create mode 100644 "m3u8tools/test/\346\213\223\345\261\225\350\216\267\345\217\226.py"
 create mode 100644 main.py
 create mode 100644 path_tools.py
 create mode 100644 proxy_pool.py
 create mode 100644 read_head_cookie.py
 create mode 100644 redirect_m3u8_decorator.py
 create mode 100644 requirements.txt
 create mode 100644 retry_decorator.py
 create mode 100644 sqlite_cache_decorator.py
 create mode 100644 test/cellfunc_test.py
 create mode 100644 test/path_tools_test.py

D:\3DS\test\hanime_videos_spider>git checkout 2.2
Switched to branch '2.2'

D:\3DS\test\hanime_videos_spider>git merge new-branch
fatal: refusing to merge unrelated histories

D:\3DS\test\hanime_videos_spider>git merge new-branch --allow-unrelated-histories
Merge made by the 'ort' strategy.

D:\3DS\test\hanime_videos_spider>git branch -D new-branch
Deleted branch new-branch (was bccd90a).

D:\3DS\test\hanime_videos_spider>