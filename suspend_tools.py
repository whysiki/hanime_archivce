# import signal
# import asyncio
# import socket
# from loguru import logger


# class InternetUnavailableError(Exception):
#     pass


# def signal_handler(signum, frame):
#     print("Program interrupted by user")
#     exit(0)


# async def is_internet_available():
#     try:
#         loop = asyncio.get_event_loop()
#         _, _ = await asyncio.wait_for(
#             loop.create_connection(asyncio.Protocol, host="8.8.8.8", port=53), timeout=5
#         )
#         return True
#     except (OSError, asyncio.TimeoutError, ConnectionRefusedError):
#         return False


# async def tasks(condition):
#     for i in range(3000):
#         async with condition:
#             await condition.wait()
#         await asyncio.sleep(1)
#         logger.debug("Task working...")
#         await asyncio.sleep(1)
#         logger.success("Task done")
#         await asyncio.sleep(1)


# async def monitor_internet(condition):
#     while True:
#         async with condition:
#             if await is_internet_available():
#                 condition.notify_all()
#             else:
#                 logger.warning("Internet is not available. Waiting for connection...")
#         await asyncio.sleep(5)


# async def main():
#     signal.signal(signal.SIGINT, signal_handler)
#     condition = asyncio.Condition()
#     task = asyncio.create_task(tasks(condition))
#     monitor = asyncio.create_task(monitor_internet(condition))
#     await asyncio.gather(task, monitor)


# try:
#     asyncio.run(main())
# except KeyboardInterrupt:
#     print("Program interrupted by user")
