from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from .utils import paginate_page


def is_author(func):
    def check_user(request, *args, **kwargs):
        if Post.author == request.user:
            return func(request, *args, **kwargs)
        return redirect('/auth/login')
    return check_user


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('group', 'author')
    page_obj = paginate_page(request, posts)
    context: dict = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    page_obj = paginate_page(request, posts)
    context: dict = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.select_related('author', 'group')
    page_obj = paginate_page(request, user_posts)
    context: dict = {
        'author': user,
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
    form = PostForm(request.POST or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.pub_date = date.today()
        new_post.save()
        return redirect('posts:profile', request.user)
    return render(request, template, {'form': form})


'''Денис, но этот код не работает, как надо. 
Вместо сохранения имеющегося поста он создаёт новый. 
Я очень удивилась, что меня пайтесты пропустили с этой ошибкой, 
но теперь меня с ней пропускаешь и ты (в Яндексе на "ты" вроде бы,
мне очень непривычно "выкать", но, если это неуместно или некомфортно,
то я прошу прощения и больше не буду)'''


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    is_edit = True
    post = get_object_or_404(Post,
                             pk=post_id)
    if post.author == request.user:
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post_id)
        return render(request, template,
                      context={'form': form,
                               'post': post,
                               'is_edit': is_edit})
    redirect('posts:create_post')
