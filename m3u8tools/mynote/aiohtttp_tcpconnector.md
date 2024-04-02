- `verify_ssl`: 设置为`True`以检查 SSL 证书。
- `fingerprint`: 传递预期证书的二进制 SHA256 摘要，以 DER 格式，以验证服务器提供的证书是否匹配。参考[Certificate Pinning](https://en.wikipedia.org/wiki/Transport_Layer_Security#Certificate_pinning)。
- `resolver`: 启用 DNS 查找并使用此解析器。
- `use_dns_cache`: 使用内存缓存进行 DNS 查找。
- `ttl_dns_cache`: DNS 条目缓存的最长时间，以秒为单位。设置为`None`表示永远缓存。
- `family`: socket 地址族。
- `local_addr`: 绑定套接字的本地主机和端口的元组。
- `keepalive_timeout`: （可选）保持活动的超时时间。
- `force_close`: 设置为`True`以强制在每个请求（和重定向之间）关闭连接并重新连接。
- `limit`: 同时连接的总数。
- `limit_per_host`: 同一主机的同时连接数。
- `enable_cleanup_closed`: 启用清理关闭的 SSL 传输。默认情况下禁用。
- `loop`: 可选事件循环。

- `verify_ssl`（bool，默认为 True）：指定是否验证 SSL 证书。如果设置为 True，则表示验证 SSL 证书；如果设置为 False，则表示不验证 SSL 证书。

- `fingerprint`（bytes 或 None，默认为 None）：SSL 证书的指纹。如果指定了 SSL 证书的指纹，则用于验证服务器提供的证书。

- `use_dns_cache`（bool，默认为 True）：指定是否使用 DNS 缓存。如果设置为 True，则表示使用 DNS 缓存；如果设置为 False，则表示禁用 DNS 缓存。

- `ttl_dns_cache`（int 或 None，默认为 10）：DNS 缓存的存活时间（Time To Live），以秒为单位。如果设置为 None，则表示不设置缓存的存活时间。

- `family`（int，默认为 0）：指定要使用的套接字地址族。默认值 0 表示自动选择地址族。

- `ssl_context`（Unknown 或 None，默认为 None）：SSL 上下文对象，用于设置 SSL 相关参数。

- `ssl`（bool 或 Fingerprint 或 Unknown，默认为 True）：指定是否使用 SSL/TLS 进行安全连接。如果设置为 True，则表示使用 SSL/TLS 进行安全连接；如果设置为 False，则表示不使用 SSL/TLS 进行安全连接。

- `local_addr`（Tuple[str, int] 或 None，默认为 None）：本地地址元组，用于绑定本地端口和 IP 地址。

- `resolver`（AbstractResolver 或 None，默认为 None）：DNS 解析器对象，用于解析主机名。

- `keepalive_timeout`（float 或 object 或 None，默认为 sentinel）：指定 TCP 连接的保活超时时间，以秒为单位。如果设置为 sentinel，则表示使用系统默认值。

- `force_close`（bool，默认为 False）：指定是否强制关闭连接。如果设置为 True，则表示强制关闭连接。

- `limit`（int，默认为 100）：指定连接池的最大连接数限制。

- `limit_per_host`（int，默认为 0）：指定每个主机的连接池的最大连接数限制。如果设置为 0，则表示没有限制。

- `enable_cleanup_closed`（bool，默认为 False）：指定是否启用清理已关闭连接的功能。如果设置为 True，则表示启用清理已关闭连接的功能。

- `loop`（AbstractEventLoop 或 None，默认为 None）：事件循环对象。

- `timeout_ceil_threshold`（float，默认为 5）：指定连接超时时间的上限阈值，以秒为单位。超过这个阈值的超时时间会被截断为这个阈值。

class TCPConnector(
\*,
verify_ssl: bool = True,
fingerprint: bytes | None = None,
use_dns_cache: bool = True,
ttl_dns_cache: int | None = 10,
family: int = 0,
ssl_context: Unknown | None = None,
ssl: bool | Fingerprint | Unknown = True,
local_addr: Tuple[str, int] | None = None,
resolver: AbstractResolver | None = None,
keepalive_timeout: float | object | None = sentinel,
force_close: bool = False,
limit: int = 100,
limit_per_host: int = 0,
enable_cleanup_closed: bool = False,
loop: AbstractEventLoop | None = None,
timeout_ceil_threshold: float = 5
)
