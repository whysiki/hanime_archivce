## clone

```shell
git clone --single-branch --branch 2.0 https://github.com/PCCAG/hanime_videos_spider.git
```

## Description

This is an asynchronous web crawler tool designed for the website hanime.

- **Resume Download Support**: Supports resuming downloads after interruption, ensuring that download tasks are not lost due to unexpected interruptions.
- **Simultaneous Downloads of Multiple Categories**: Can download multiple videos of different categories simultaneously, improving download efficiency.
- **Result Caching**: Supports result caching functionality, allowing caching of results as long as the source code parsing result is valid, reducing redundant requests and saving network resources and time.
- **Parameter Update Requests**: Only reissues requests when function parameters are updated, reducing unnecessary network requests and improving efficiency.

- **Asynchronous and resumable upload of M3U8 streams is supported, but make sure you have a strong enough proxy pool🤣🤔**

## Configuration

Before using, please refer to `config.py` for appropriate configuration.

## Usage

1. Firstly, configure `_cookies_.json` and `_headers_example.json` in `config.py` according to personal needs. The content should conform to the format of the Firefox browser.

2. Then, edit the configuration parameters such as download directory, number of downloads, and download categories in `main.py` as needed.

3. Start `main.py` and wait for the downloads to complete.

4. If errors occur, check the log files in the `log/` directory and take appropriate actions based on the error messages.

## 说明

这是一个针对网站 hanime 的异步爬虫工具。

- **断点续传下载**：支持在下载过程中断后继续下载，确保下载任务不会因意外中断而丢失。
- **多类别同时下载**：可以同时下载多个不同类别的视频，提高下载效率。
- **结果缓存**：支持结果缓存功能，只要源码解析结果合法，即可缓存结果，以减少重复请求，节省网络资源和时间。
- **参数更新请求**：仅在函数参数更新时才会重新发起请求，减少不必要的网络请求，提升效率。
- **支持 m3u8 流的异步和断点续传, 但是请确保你有足够强的代理池 🤣**

## 配置

在使用前，请查看 `config.py` 进行相应的配置。

## 使用

1. 首先，根据个人需要配置 `config.py` 中的 `_cookies_.json` 和 `_headers_example.json`，内容应符合 Firefox 浏览器格式。

2. 然后，根据需求编辑 `main.py` 中的下载目录、下载数量和下载分类等配置参数。

3. 启动`main.py`，等待下载完成。

4. 如果出现错误, 查看`log/`目录下的日志文件，根据错误信息进行相应的处理。
