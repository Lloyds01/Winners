import random
import string

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


def generate_random_username():
    from account.models import User

    username = "".join(random.choice(string.ascii_letters) for i in range(10))

    if User.objects.filter(username=username).exists():
        return generate_random_username()

    return username


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, password, username=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        if not username:
            username = generate_random_username()

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, password, username=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not username:
            raise ValueError(_("The Email must be set"))

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(password, username=username, **extra_fields)
