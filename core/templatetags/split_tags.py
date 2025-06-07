# templatetags/split_tags.py
from django import template
import random  # 添加这一行来导入random模块

register = template.Library()


@register.filter
def split(value, arg):
    return value.split(arg)


@register.filter
def color(value):
    colors = ['bg-blue-100', 'bg-green-100', 'bg-purple-100', 'bg-pink-100', 'bg-yellow-100', 'bg-red-100']
    return colors[random.randint(0, 5)]
