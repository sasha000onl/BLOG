from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db import models
from django.views.generic.edit import FormMixin
from django.shortcuts import redirect
from .models import Article, Comment
from .forms import CommentForm, ArticleForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
            return redirect('articles:article_detail', slug=self.object.slug)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = self.get_form()   # обов’язково!
        context['comments'] = self.object.comments.order_by('created_at')
        return context



class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Article.objects.all()
        qs = Article.objects.filter(status='published')
        if self.request.user.is_authenticated:
            qs = Article.objects.filter(
                models.Q(status='published') |
                models.Q(status='draft', author=self.request.user)
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
            return redirect('articles:article_detail', slug=self.object.slug)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = self.get_form()   # обов’язково!
        context['comments'] = self.object.comments.order_by('created_at')
        return context


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'

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
