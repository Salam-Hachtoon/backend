from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils import timezone
from users.UserManager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model that extends Django's AbstractBaseUser and PermissionsMixin.
    Attributes:
        email (EmailField): Unique email address used as the username.
        first_name (CharField): First name of the user, default is "Unknown".
        last_name (CharField): Last name of the user, default is "Unknown".
        profile_picture (ImageField): Profile picture of the user, optional.
        is_active (BooleanField): Indicates whether the user is active, default is True.
        is_staff (BooleanField): Indicates whether the user has admin access, default is False.
        groups (ManyToManyField): Groups the user belongs to, related to custom user groups.
        user_permissions (ManyToManyField): Permissions assigned to the user, related to custom user permissions.
        objects (UserManager): Manager for the User model.
        USERNAME_FIELD (str): Field used as the unique identifier, set to 'email'.
        REQUIRED_FIELDS (list): List of required fields when creating superusers, includes 'first_name' and 'last_name'.
    Methods:
        __str__(): Returns a string representation of the user with email, first name, and last name.
    """

    email = models.EmailField(unique=True)  # Use email instead of username
    first_name = models.CharField(max_length=50, default="Unknown")
    last_name = models.CharField(max_length=50, default="Unknown")
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for admin access
    # No password field is not explicitly defined
    # because it is inherited from Django's AbstractBaseUser class,
    # which provides the password field and related methods
    # for handling passwords securely.

    # Set the user groups and permissions for the user model
    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    # Set the user manager model
    objects = UserManager()
    # Those line for the create superuser command 
    USERNAME_FIELD = 'email'  # Set email as the unique identifier
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Required when creating superusers

    def __str__(self):
        return "Email: {}, First Name: {}, Last Name: {}".format(
            self.email,
            self.first_name,
            self.last_name
        )
