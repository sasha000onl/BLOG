from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


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

    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)

    multimedia = models.FileField(upload_to='articles_media/', blank=True, null=True)  # фото або відео

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    CONTENT_TYPE_CHOICES = [
        ('none', 'Без мультимедіа'),
        ('image', 'Фото'),
        ('video', 'Відео (YouTube/Vimeo)'),
    ]

    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default='none',
        verbose_name="Мультимедіа"
    )
    media_file = models.ImageField(
        upload_to='articles_media/',
        blank=True, null=True,
        verbose_name="Фото"
    )
    media_url = models.URLField(
        blank=True, null=True,
        verbose_name="Відео (YouTube/Vimeo)"
    )

    class Meta:
        ordering = ['-created_at']

    def average_rating(self):
        ratings = self.ratings.all()
        return round(sum(r.value for r in ratings) / len(ratings), 1) if ratings else 0


    def save(self, *args, **kwargs):
            if not self.slug and self.title:
                base_slug = slugify(self.title)
                slug = base_slug
                counter = 1
                while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug
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


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Підписка {self.user.username}"


class Rating(models.Model):
    article = models.ForeignKey(Article, related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('article', 'user')

    def __str__(self):
        return f"{self.user} → {self.article} ({self.value})"


    class Meta:
        unique_together = ('article', 'user')

    def __str__(self):
        return f"{self.user} → {self.article} ({self.value})"