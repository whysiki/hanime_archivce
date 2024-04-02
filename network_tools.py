import socket


def is_internet_available():
    try:
        socket.create_connection(("223.5.5.5", 53), timeout=5)
        return True
    except OSError:
        return False


# print(is_internet_available())
