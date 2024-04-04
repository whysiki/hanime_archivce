from loguru import logger


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
