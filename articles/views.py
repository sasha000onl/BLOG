from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Article, Comment
from .forms import ArticleForm, CommentForm, RatingForm
from django.db.models import Q
from .models import Rating
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# -----------------------------------
# Article Views
# -----------------------------------

class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6
    queryset = Article.objects.filter(status='published').order_by('-created_at')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Article.objects.all()
        qs = Article.objects.filter(status='published')
        if self.request.user.is_authenticated:
            qs = Article.objects.filter(
                Q(status='published') | Q(status='draft', author=self.request.user)
            ).distinct()
        return qs



class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('articles:article_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('articles:article_list')

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'articles/article_confirm_delete.html'
    success_url = reverse_lazy('articles:article_list')

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff


# -----------------------------------
# ArticleDetailView з формою коментаря
# -----------------------------------

class ArticleDetailView(FormMixin, DetailView):
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'
    form_class = CommentForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, "Коментар додано ✅")
            return redirect('articles:article_detail', slug=self.object.slug)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = self.get_form()  # поле коментаря
        context['comments'] = self.object.comments.order_by('-created_at')  # всі коментарі
        context['rating_form'] = RatingForm()  # якщо треба для рейтингу
        if hasattr(self.object, 'average_rating'):
            context['average_rating'] = self.object.average_rating()
        return context


# 1. Опубліковані (для всіх)
class PublicArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        return Article.objects.filter(status='published').order_by('-created_at')

# 2. Твої статті (включно з чернетками)
class MyArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'articles/my_articles.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user).order_by('-created_at')
# -----------------------------------
# Коментарі
# -----------------------------------

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'articles/comment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('articles:article_detail', kwargs={'slug': self.object.article.slug})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author or self.request.user.is_staff


@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, "Ви не можете редагувати цей коментар.")
        return redirect("articles:article_detail", slug=comment.article.slug)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Коментар оновлено ✅")
            return redirect("articles:article_detail", slug=comment.article.slug)
    else:
        form = CommentForm(instance=comment)

    return render(request, "articles/comment_edit.html", {"form": form, "comment": comment})


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, "Ви не можете видалити цей коментар.")
        return redirect("articles:article_detail", slug=comment.article.slug)

    article_slug = comment.article.slug
    comment.delete()
    messages.success(request, "Коментар видалено 🗑️")
    return redirect("articles:article_detail", slug=article_slug)


# -----------------------------------
# Рейтинг
# -----------------------------------

@login_required
def rate_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                article=article,
                user=request.user,
                defaults={'value': form.cleaned_data['value']}
            )
    return redirect('articles:article_detail', slug=slug)

@login_required
def subscribe(request):
    Subscription.objects.get_or_create(user=request.user)
    return redirect('articles:article_list')

def article_update(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('articles:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/article_form.html', {
        'form': form,
        'article': article,
        'categories': Category.objects.all(),  # ← ОБОВ'ЯЗКОВО
        'tags': Tag.objects.all(),             # ← ОБОВ'ЯЗКОВО
    })