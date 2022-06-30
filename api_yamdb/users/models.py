import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOISES = (
    ('user', 'user'),
    ('moderator', 'moderator'),
    ('admin', 'admin'),
)


class User(AbstractUser):
    email = models.EmailField(
        blank=False, null=False,
        unique=True, max_length=254
    )
    password = models.CharField(blank=True, null=True, max_length=128)
    first_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(choices=ROLE_CHOISES, default='user', max_length=9)
    confirmation_code = models.CharField(
        default=uuid.uuid4,
        editable=True,
        unique=True,
        max_length=36,
        auto_created=True
    )

    REQUIRED_FIELDS = ['email', ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_login_fields',

            ),
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_superuser or self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'
