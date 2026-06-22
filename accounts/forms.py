from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='邮箱', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '用户名'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'
        self.fields['password1'].help_text = '密码至少8位，不能太简单'
        self.fields['password2'].help_text = '重复输入密码'
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio', 'province', 'city', 'district', 'street_address')
        labels = {
            'phone': '手机号',
            'avatar': '头像',
            'bio': '个人简介',
            'province': '省份',
            'city': '城市',
            'district': '区/县',
            'street_address': '详细地址',
        }
        widgets = {
            'province': forms.HiddenInput(),
            'city': forms.HiddenInput(),
            'district': forms.HiddenInput(),
            'street_address': forms.TextInput(attrs={'placeholder': '街道、门牌号、楼层等'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.__class__.__name__ not in ('ClearableFileInput', 'HiddenInput'):
                field.widget.attrs.setdefault('class', 'form-control')
