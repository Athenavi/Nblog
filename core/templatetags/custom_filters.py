# blog/templatetags/custom_filters.py
import json
import ast
from django import template

register = template.Library()


@register.filter
def parse_json(value):
    # 如果已经是字典直接返回
    if isinstance(value, dict):
        return value

    # 处理字符串类型的值
    if isinstance(value, str):
        try:
            # 尝试标准JSON解析
            return json.loads(value)
        except json.JSONDecodeError:
            try:
                # 尝试解析Python风格的字典（单引号）
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                pass

    # 打印调试信息（可选）
    print(f"Failed to parse: {value} | Type: {type(value)}")
    return None


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')
