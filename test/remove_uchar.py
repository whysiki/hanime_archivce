def sanitize_path(name):
    name = name.replace(" ", "")
    invalid_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|", "'"]
    for char in invalid_chars:
        name = name.replace(char, "")
    # return name
    print(name)


# 测试案例
name = "path/with:invalid*characters"
sanitized_name = sanitize_path(name)
print(sanitized_name)
