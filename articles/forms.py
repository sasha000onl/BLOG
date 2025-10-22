from django import forms
from .models import Article, Comment, Rating, Category, Tag


class ArticleForm(forms.ModelForm):
    new_tag = forms.CharField(required=False, label="Додати новий тег")
    new_category = forms.CharField(required=False, label="Додати нову категорію")

    class Meta:
        model = Article
        fields = ['title', 'content', 'status', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def save(self, commit=True, user=None):
        article = super().save(commit=False)

        # --- створюємо нову категорію, якщо введена ---
        new_cat = self.cleaned_data.get('new_category')
        if new_cat:
            category_obj, created = Category.objects.get_or_create(name=new_cat)
            article.category = category_obj

        if commit:
            article.save()
            self.save_m2m()

            # --- створюємо новий тег, якщо введений ---
            new_tag = self.cleaned_data.get('new_tag')
            if new_tag:
                tag_obj, created = Tag.objects.get_or_create(name=new_tag)
                article.tags.add(tag_obj)

        return article


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
