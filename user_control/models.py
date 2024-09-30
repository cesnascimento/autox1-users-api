from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from user_control.views import add_user_activity

Roles = (("admin", "admin"), ("user_1", "user1"), ("user_2", "user2"), ("user_3", "user3"))


class CustomUserManager(BaseUserManager):

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if not email:
            raise ValueError("Email field is required")

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class TokenWPP(models.Model):
    token_wpp = models.CharField(max_length=10000, null=True)

    def __str__(self):
        return self.token_wpp


class CustomUser(AbstractBaseUser, PermissionsMixin):
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=8, choices=Roles)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True)
    token = models.ForeignKey(TokenWPP, null=True, on_delete=models.CASCADE, related_name="tokenwpp")

    USERNAME_FIELD = "email"
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ("created_at", )


class WPPGroup(models.Model):
    created_by = models.ForeignKey(
        CustomUser, null=True, related_name="group",
        on_delete=models.SET_NULL
    )
    added_date = models.DateTimeField(auto_now_add=True)
    origin = models.CharField(max_length=255, blank=True, null=True)
    invite_link = models.URLField(unique=True)
    status_connect = models.BooleanField(null=True, default=False)

    class Meta:
        ordering = ("-id",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_name = self.origin

    def save(self, *args, **kwargs):
        action = f"Adicionado novo Grupo - '{self.origin}'"
        if self.pk is not None:
            action = f"Atualizado Grupo de - '{self.old_name}' para '{self.origin}'"
        super().save(*args, **kwargs)
        add_user_activity(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"Deletado Grupo - '{self.origin}'"
        super().delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return f'{self.origin}: {self.invite_link}'


class UserActivities(models.Model):
    user = models.ForeignKey(
        CustomUser, related_name="user_activities", null=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    fullname = models.CharField(max_length=255)
    action = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", )

    def __str__(self):
        return f"{self.fullname} {self.action} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"