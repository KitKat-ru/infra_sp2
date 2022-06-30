from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = [
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role'
    ]
    empty_value_display = '-пусто-'


admin.site.register(User, CustomUserAdmin)
