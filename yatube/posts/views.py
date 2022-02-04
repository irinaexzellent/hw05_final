from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required


from .models import Post, Group, User, Follow
"""Количество объектов модели."""
COUNT_OBJECT = 10


def index(request):
    """View-функция возвращает главную страницу.

    Ключевые аргументы:
    posts_list -- объекты модели Post,
    paginator -- количество записей на странице,
    page_number -- номер запрошенной страницы,
    page_obj -- набор записей для страницы с запрошенным номером
    """
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, COUNT_OBJECT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """ View-функция возвращает страницу сообщества.

    Ключевые аргументы:
    group -- объекты модели Group,
    поле slug у которых соответствует значению slug в запросе
    posts_list -- объекты модели Post у которых поле group
    соответсвует объекту модели Group
    """

    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, COUNT_OBJECT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """ View-функция возвращает страницу профайла пользователя.

    Ключевые аргументы:
    user -- объект класса User, username=username,
    posts -- все посты объекта user,
    paginator -- количество записей на странице,
    page_number -- номер запрошенной страницы,
    page_obj -- набор записей для страницы с запрошенным номером
    """
    user_profile = get_object_or_404(User, username=username)
    posts = user_profile.posts.all()
    paginator = Paginator(posts, COUNT_OBJECT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Страница пользователя'
    fullname = user_profile.get_full_name()
    user = request.user
    following = user.is_authenticated and user_profile.following.exists()
    context = {
        'author': user_profile,
        'posts': posts,
        'page_obj': page_obj,
        'title': title,
        'fullname': fullname,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """ View-функция возвращает страницу поста.

    Ключевые аргументы:
    post -- объект модели Post, id=post_id,
    posts -- все объекты модели Post,
    comments -- все комментарии объекта post с id=post_id,
    form -- объект класса CommentForm
    """
    post = get_object_or_404(Post, id=post_id)
    posts = Post.objects.all()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'posts': posts,
        'form': form,
        'comments': comments}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """ View-функция создает пост и возвращает страницу профайла пользоваетеля.

    Ключевые аргументы:
    form -- объект класса PostForm,
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            username = post.author
            return redirect('posts:profile', username=username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """ View-функция редактирует пост и возвращает страницу поста.

    Ключевые аргументы:
    post -- объект модели Post, id=post_id,
    form -- объект класса PostForm
    """
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {'form': form,
               'is_edit': True,
               'post': post}
    if request.user != post.author:
        return post_detail(request, post_id)
    else:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save()
                return redirect('posts:post_detail', post_id=post.id)
        return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """ View-функция создает комментарий и возвращает страницу поста.

    Ключевые аргументы:
    post -- объект модели Post, id=post_id,
    form -- объект класса CommentForm
    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """View-функция возвращает страницу
    с избранными авторами.

    Ключевые аргументы:
    user -- текущий пользователь,
    authors -- список объектов класса User,
    на которых подписан текущий пользователь
    posts_list -- объекты модели Post, отфильтрованные по
    авторам, на которых подписан текущий пользователь
    paginator -- количество записей на странице,
    page_number -- номер запрошенной страницы,
    page_obj -- набор записей для страницы с запрошенным номером
    """
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    posts_list = Post.objects.filter(author__id__in=authors)
    paginator = Paginator(posts_list, COUNT_OBJECT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    print(authors)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """ View-функция создает подписку на автора
    (если текущий пользователь не является автором профиля)
    и возвращает страницу профиля автора.

    Ключевые аргументы:
    author -- объект класса User, username=username
    user -- текущий пользователь
    """
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect('posts:profile', username=username)
    return HttpResponse(request)


@login_required
def profile_unfollow(request, username):
    """ View-функция отменяет подписку на автора
    и перенаправляет на страницу
    'profile/<str:username>/unfollow/'.

    Ключевые аргументы:
    user -- текущий пользователь;
    """

    user = request.user
    Follow.objects.get(user=user, author__username=username).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
