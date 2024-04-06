# 对于函数输出的结果进行断言
# 来决定是否进行缓存
# Assertion function for verifying the output of a function, checking if the function output is normal.


def source_assert_result(result):
    assert result
    assert isinstance(result, dict)
    assert "source" in result


def parse_assert_result(result):
    assert result
    assert isinstance(result, dict)
    assert ("name" in result) and ("contentUrl" in result) and ("description" in result)
