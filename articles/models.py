from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Чернетка'),
        ('published', 'Опубліковано'),
    )

    title = models.CharField(max_length=200, unique=True, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(verbose_name="Текст статті")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:  # автогенерація slug із заголовка
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Коментар")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Коментар від {self.author.username} до "{self.article.title}"'
