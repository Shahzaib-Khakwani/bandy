from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.timezone import now



class FriendshipManager(models.Manager):
    def active(self):
        """Return only active friendships."""
        return super().get_queryset().filter(is_active=True)


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, user_name, first_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name, first_name, password, **other_fields)

    def create_user(self, email, user_name, first_name, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name,
                          first_name=first_name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_OPTIONS = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Others", "Others"),
    )

    email = models.EmailField(_('email address'), unique=True)
    user_name = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_OPTIONS )
    department = models.CharField(max_length=150, blank=True, null=True)
    about = models.TextField(_(
        'about'), max_length=500, blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_varified = models.BooleanField(default=False)

    friends = models.ManyToManyField(
        'self', 
        through='Friendship', 
        symmetrical=False, 
        related_name='friend_of'
    )

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name', 'first_name']

    def __str__(self):
        return self.user_name
    

class Friendship(models.Model):
    """Intermediary model to manage friendships between users."""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friendships_initiated')
    friend = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friendships_received')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    objects = FriendshipManager()
    all = models.Manager()

    class Meta:
        unique_together = ('user', 'friend')
        ordering = ['-created_at']

    def accept_friendship(self):
        """Accept a pending friendship request."""
        self.is_active = True
        self.accepted_at = now()
        self.save()

    def __str__(self):
        return f"{self.user.user_name} is friends with {self.friend.user_name} (active: {self.is_active})"
