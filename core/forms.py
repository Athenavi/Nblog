from django import forms
from django.contrib.auth.models import User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


from .models import ShortLink
import re


class ShortLinkForm(forms.ModelForm):
    class Meta:
        model = ShortLink
        fields = ['original_url', 'short_code', 'expires_at']
        widgets = {
            'original_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/your-long-url'
            }),
            'short_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '自定义短码 (可选)'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }

    def clean_original_url(self):
        """验证原始URL格式"""
        url = self.cleaned_data['original_url']
        if not re.match(r'^https?://', url):
            raise forms.ValidationError("URL必须以http://或https://开头")
        return url

    def clean_short_code(self):
        """验证短码格式"""
        short_code = self.cleaned_data.get('short_code', '')
        if short_code:
            if len(short_code) < 6 or len(short_code) > 12:
                raise forms.ValidationError("短码长度必须在6-12位之间")
            if not re.match(r'^[a-zA-Z0-9]+$', short_code):
                raise forms.ValidationError("短码只能包含字母和数字")
        return short_code
