from django import forms
from .models import Item, ItemImage, Message

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('title', 'description', 'price', 'condition', 'category')
        labels = {
            'title': '商品标题',
            'description': '商品描述',
            'price': '价格 (元)',
            'condition': '成色',
            'category': '分类',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ('image',)

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        labels = {'content': '消息内容'}
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': '请输入您想说的话...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['class'] = 'form-control'
