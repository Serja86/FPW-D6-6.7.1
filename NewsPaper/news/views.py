from django.shortcuts import render
from datetime import datetime
from django.views.generic import (ListView, DetailView, UpdateView, DeleteView, CreateView)
from .forms import PostForm
from django.urls import reverse_lazy
from .filters import PostFilter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .models import Post, Subscriber, Category
from .filters import PostSearch

# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД



class NewsList(ListView):
   model = Post
   ordering = 'title'
   template_name = 'News.html'
   context_object_name = 'news'
   extra_context = {'title': 'Новости'}
   author = 'author'
   # queryset = Post.objects.order_by('-dateCreation')
   paginate_by = 10

   # Переопределяем функцию получения списка товаров
   def __init__(self, **kwargs):
       super().__init__(kwargs)
       self.filterset = None

   def get_queryset(self):
       queryset = super().get_queryset()
       self.filterset = PostSearch(self.request.GET, queryset)
       return self.filterset.qs

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['filterset'] = self.filterset
       return context

   def post_search(request):
       f = PostSearch(request.GET,
                      queryset=Post.objects.all())
       return render(request,
                     'news_search.html',
                     {'filter': f})


class NewsDetail(DetailView):
    model = Post
    template_name = 'onenews.html'
    context_object_name = 'onenews'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        return context

class PostSearchView(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'NewsSearch'
    paginate_by = 10
    ordering = ['-id']
    queryset = Post.objects.all()

    def get_filter(self):
        return PostSearch(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'filter': self.get_filter(),
        }

class PostCreateAR(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'articles_edit.html'

    def form_valid(self, form):
        post = form.save(commit=True)
        post.categoryType = "AR"
        return super().form_valid(form)

class PostCreateNW(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        post = form.save(commit=True)
        post.categoryType = "NW"
        return super().form_valid(form)



class PostEditNW(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

class PostDeleteNW(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ('news.add_post',)
    raise_exception = True
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('post_list')

class PostEditAR(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'articles_edit.html'

class PostDeleteAR(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ('news.add_post',)
    raise_exception = True
    model = Post
    template_name = 'articles_delete.html'
    success_url = reverse_lazy('post_list')

@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscriber':
            Subscriber.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscriber.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscriber.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('pk')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )