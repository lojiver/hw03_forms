from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


# Create your views here.


def is_author(func):
    def check_user(request, *args, **kwargs):
        if Post.author == request.user:
            return func(request, *args, **kwargs)
        return redirect('/auth/login')
    return check_user


def index(request):
    template = 'posts/index.html'
    text: str = 'Это главная страница проекта Yatube'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context: dict = {
        'main_title': text,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    text: str = 'Здесь будет информация о группах проекта Yatube'
    context: dict = {
        'group_posts_title': text,
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user404 = get_object_or_404(User, username=username)
    user_posts = user404.posts.select_related('author', 'group')
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context: dict = {
        'author': user404,
        'user_posts': user_posts,
        'page_obj': page_obj,
        'profile_title': 'Страница пользователя'
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    context: dict = {
        'post': post
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.pub_date = date.today()
            new_post.save()
            return redirect('posts:profile', request.user)
        return render(request, template, {'form': form})
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    is_edit = True
    post = get_object_or_404(Post,
                             pk=post_id)
    if post.author == request.user:
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post_id)
        form = PostForm(instance=post)
        return render(request, template,
                      context={'form': form,
                               'post': post,
                               'is_edit': is_edit})
    redirect('posts:create_post')
