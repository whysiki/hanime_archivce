import json

# from rich import print
import os

current_dir = os.path.dirname(__file__)
cookie_json_filepath = os.path.join(current_dir, "_cookies_.json")
headers_example = os.path.join(current_dir, "_headers_example.json")

assert os.path.exists(cookie_json_filepath), f"{cookie_json_filepath} not exists"
assert os.path.exists(headers_example), f"{headers_example} not exists"


# 这个函数是从cookies.json文件中读取cookie,并且更新到headers_examples中


def read_headers_from_json(
    cookie_json_filepath=cookie_json_filepath, headers_example=headers_example
) -> dict:
    """
    默认:
    从 headers_example="_headers_ example.json" 获取headers模板,
    从 cookie_json_filepath="cookies.json" 更新headers的cookie字段,
    (从函数所在代码文件目录找)
    返回: headers
    """

    # logger.debug("尝试从cookies.json获取headers 的cookie.......")
    with open(cookie_json_filepath, encoding="utf-8") as f:
        # try:
        # dread = dict(json.load(f))
        d_list: list = json.load(f)
        # dict().keys()
        # print(list(dread.keys())[0])
        headers_cookie = "; ".join([f'{d["name"]}={d["value"]}' for d in d_list])
        # headers_cookie = "; ".join([f"{k}={v}" for k, v in d_list[0].items()])
        # print(headers_cookie)
        with open(headers_example, encoding="utf-8") as h:
            headers__fierfox_original = dict(json.load(h))
            middle_: dict = headers__fierfox_original[
                list(headers__fierfox_original.keys())[0]
            ]
            d_list_headers = middle_["headers"]

            headers = {d["name"]: d["value"] for d in d_list_headers}
            headers["Cookie"] = headers_cookie
            # print(headers)
        # except Exception as e:
        #     raise e

        return headers


# if __name__ == "__main__":
#     h = read_headers_from_json()
#     print(h)
