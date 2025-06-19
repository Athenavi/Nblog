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


from rest_framework import serializers
from .models import ShortLink
from django.utils import timezone
from datetime import timedelta
import re


class ShortLinkCreateSerializer(serializers.ModelSerializer):
    # 允许用户自定义短码（可选）
    short_code = serializers.CharField(
        max_length=12,
        required=False,
        allow_blank=True,
        help_text="自定义短码（6-12位字母数字），留空则自动生成"
    )

    # 允许用户设置过期时间（可选）
    expires_at = serializers.DateTimeField(
        required=False,
        help_text="过期时间（格式：YYYY-MM-DD HH:MM），留空则永不过期"
    )

    class Meta:
        model = ShortLink
        fields = ['original_url', 'short_code', 'expires_at']
        extra_kwargs = {
            'original_url': {
                'required': True,
                'allow_blank': False,
                'help_text': '原始URL（必填）'
            }
        }

    def validate_original_url(self, value):
        """验证原始URL格式"""
        if not re.match(r'^https?://', value):
            raise serializers.ValidationError("URL必须以http://或https://开头")
        return value

    def validate_short_code(self, value):
        """验证短码格式"""
        if value:
            if len(value) < 6 or len(value) > 12:
                raise serializers.ValidationError("短码长度必须在6-12位之间")
            if not re.match(r'^[a-zA-Z0-9]+$', value):
                raise serializers.ValidationError("短码只能包含字母和数字")
            if ShortLink.objects.filter(short_code=value).exists():
                raise serializers.ValidationError("该短码已被使用")
        return value

    def validate_expires_at(self, value):
        """验证过期时间"""
        if value and value < timezone.now():
            raise serializers.ValidationError("过期时间不能是过去的时间")
        return value

    def create(self, validated_data):
        """创建短链接对象"""
        request = self.context.get('request')
        user = request.user if request else None

        # 自动生成短码（如果未提供）
        if not validated_data.get('short_code'):
            validated_data['short_code'] = self.generate_short_code()

        # 设置默认过期时间（7天后）
        if not validated_data.get('expires_at'):
            validated_data['expires_at'] = timezone.now() + timedelta(days=7)

        # 创建短链接
        short_link = ShortLink.objects.create(
            original_url=validated_data['original_url'],
            short_code=validated_data['short_code'],
            expires_at=validated_data['expires_at'],
            user=user
        )

        return short_link

    def generate_short_code(self, length=8):
        """生成随机短码"""
        import random
        import string

        chars = string.ascii_letters + string.digits  # 字母+数字
        while True:
            code = ''.join(random.choice(chars) for _ in range(length))
            # 确保短码唯一
            if not ShortLink.objects.filter(short_code=code).exists():
                return code
