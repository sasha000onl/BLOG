from django.urls import path
from .views import CommentDeleteView
from .views import (
    ArticleListView,
    ArticleCreateView,
    ArticleDetailView,
    ArticleUpdateView,
    ArticleDeleteView,
    comment_delete,
    comment_edit,
)

app_name = 'articles'

urlpatterns = [
    path('', ArticleListView.as_view(), name='article_list'),
    path('article/create/', ArticleCreateView.as_view(), name='article_create'),
    path('<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('<slug:slug>/edit/', ArticleUpdateView.as_view(), name='article_update'),
    path('<slug:slug>/delete/', ArticleDeleteView.as_view(), name='article_delete'),

    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path("comment/<int:pk>/edit/", comment_edit, name="comment_edit"),
    path("comment/<int:pk>/delete/", comment_delete, name="comment_delete"),
]
