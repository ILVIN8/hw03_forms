from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User

# Импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import PostForm
from django.http import HttpResponseRedirect

NUMBER_OF_POSTS = 10


def index(request):
    template = "posts/index.html"
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {"page_obj": page_obj, "title": "Главная страница проекта YaTube"}
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    template = "posts/profile.html"
    # Здесь код запроса к модели и создание словаря контекста
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    post_count = post_list.count()
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {
        "page_obj": page_obj,
        "title": f"Профайл пользователя {username}",
        "author": author,
        "post_count": post_count,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    # Здесь код запроса к модели и создание словаря контекста
    post = Post.objects.get(id=post_id)
    # group = Group.objects.filter(id=post_id)
    group = post.group
    title = post.text[0:29]
    post_count = Post.objects.filter(author=post.author).count()
    # Отдаем в словаре контекста
    context = {
        "post": post,
        "title": f"Пост {title}",
        "group": group,
        "post_count": post_count,
        "username": request.user.username,
    }
    return render(request, template, context)


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author_id = request.user.id
            new_post.save()
            # После успешного создания поста перенаправляем пользователя на страницу его профиля.
            return HttpResponseRedirect(f"/profile/{request.user.username}/")

    template = "posts/create_post.html"
    form = PostForm(request.POST)
    context = {
        "form": form,
    }

    return render(request, template, context)


def post_edit(request, post_id):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post.objects.get(pk=post_id)
            form = PostForm(request.POST, instance=post)
            form.save()
            # После успешного редактирования поста перенаправляем пользователя на страницу этого поста.
            return HttpResponseRedirect(f"/posts/{post_id}/")

    template = "posts/create_post.html"
    post = Post.objects.get(pk=post_id)
    form = PostForm(instance=post)
    context = {
        "form": form,
        "is_edit": True,
    }

    return render(request, template, context)
