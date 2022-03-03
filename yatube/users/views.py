from django.views.generic import CreateView

# Функция reverse_lazy позволяет получить URL по параметрам функции path()
# Берём, тоже пригодится
from django.urls import reverse_lazy

# Импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import CreationForm
from django.contrib.auth import logout
from django.shortcuts import render


class SignUp(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


def logout_user(request):
    template = "users/logged_out.html"
    # После успешной регистрации перенаправляем пользователя на главную.
    logout(request)
    return render(request, template)
