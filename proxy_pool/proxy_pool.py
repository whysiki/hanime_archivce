from loguru import logger

# 这是代理池
# 请替换为你自己的代理池
# 这里只是一个简单的示范


# 配合错误重试装饰器使用

# This is a proxy pool.
# Please replace it with your own proxy pool.
# This is just a simple demonstration.

# Used in conjunction with error retry decorator.


# a simple proxy pool
# please replace it with your own proxy pool
class ProxyPool:

    def __init__(self):
        self.port_list = [40000 + i for i in range(90 + 1)]
        self.proxy_list = [f"http://127.0.0.1:{port}" for port in self.port_list]
        self.proxies_list = [
            {"http://": proxy, "https://": proxy} for proxy in self.proxy_list
        ]
        self.index = 0

    def next_proxies(self):
        next_proxies = self.proxies_list[self.index % len(self.proxies_list)]
        self.index += 1
        logger.debug(f"Next proxies: {next_proxies}")
        return next_proxies
