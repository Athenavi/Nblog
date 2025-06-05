import json
from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'article_id', 'user_id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_id']

    depth = 1

    def to_representation(self, instance):
        # 获取完整的序列化数据（包含所有字段）
        representation = super().to_representation(instance)

        # 提取content字段并尝试解析为字典
        content_str = representation.get('content', '')
        try:
            # 处理单引号JSON字符串（替换为双引号）
            content_str = content_str.replace("'", '"')
            content_data = json.loads(content_str)
        except (TypeError, json.JSONDecodeError):
            # 解析失败则使用原始内容
            content_data = {'content': content_str}

        # 提取结构化字段（提供默认值）
        structured_content = {
            'text': content_data.get('content', content_str),
            'ip': content_data.get('ip', ''),
            'ua': content_data.get('ua', ''),
            'reply_to': content_data.get('reply_to', 0)
        }

        # 替换content字段为结构化数据（保留其他字段）
        representation['content'] = structured_content
        return representation

    def to_internal_value(self, data):
        # 复制原始数据避免修改原始输入
        data = data.copy()

        # 提取结构化内容并转换为JSON字符串
        if 'content' in data and isinstance(data['content'], dict):
            content_data = data['content']
            # 构建符合数据库格式的字典
            db_content = {
                'content': content_data.get('text', ''),
                'ip': content_data.get('ip', ''),
                'ua': content_data.get('ua', ''),
                'reply_to': content_data.get('reply_to', 0)
            }
            # 转换为JSON字符串
            data['content'] = json.dumps(db_content)

        return super().to_internal_value(data)
