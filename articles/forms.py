from django import forms
from .models import Article, Comment, Rating, Category, Tag


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'content_type',
            'media_file', 'media_url',
            'status', 'category', 'tags'
        ]

    def clean(self):
        cleaned_data = super().clean()
        ctype = cleaned_data.get('content_type')
        file = cleaned_data.get('media_file')
        url = cleaned_data.get('media_url')

        if ctype == 'image' and not file and not self.instance.media_file:
            self.add_error('media_file', 'Завантажте фото.')
        if ctype == 'video' and not url and not self.instance.media_url:
            self.add_error('media_url', 'Вставте посилання на відео.')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Передаємо всі теги та категорії
        self.fields['category'].queryset = Category.objects.all()
        self.fields['tags'].queryset = Tag.objects.all()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишіть коментар...',
            }),
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
        widgets = {
            'value': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control w-25'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
