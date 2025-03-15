import os, random, hashlib, logging
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils.timezone import now
from users.UserManager import UserManager

# Create a models
logger = logging.getLogger('models')


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
    otp = models.CharField(max_length=64, blank=True, null=True)  # Store hashed OTP
    otp_expires_at = models.DateTimeField(blank=True, null=True)  # Expiration time
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

    def generate_otp(self):
        """
        Generates a One-Time Password (OTP), hashes it for security, and saves it to the model instance.
        The OTP is a 6-digit number that expires in 5 minutes. The hashed OTP and its expiration time
        are saved to the model instance, and the plain OTP is returned for sending via email or SMS.
        Returns:
            str: The plain 6-digit OTP.
        """

        otp_code = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
        hashed_otp = hashlib.sha256(otp_code.encode()).hexdigest()  # Hash OTP for security
        self.otp = hashed_otp
        self.otp_expires_at = now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        self.save()
        return otp_code  # Return plain OTP for sending via email/SMS

    def verify_otp(self, otp_input):
        """
        Verify the provided OTP (One-Time Password) against the stored OTP.
        Args:
            otp_input (str): The OTP input provided by the user.
        Returns:
            bool: True if the OTP is verified successfully, False otherwise.
        Logs:
            - "OTP has expired." if the OTP has expired.
            - "Invalid OTP." if the provided OTP does not match the stored OTP.
            - "OTP verified successfully." if the OTP is verified successfully.
        Side Effects:
            - Clears the stored OTP and its expiration time upon successful verification.
            - Saves the changes to the database.
        """

        # Chech the opt code time
        if (self.otp_expires_at and now()) > self.otp_expires_at:
            logger.info("OTP has expired.")
            return False
        hashed_input_otp = hashlib.sha256(otp_input.encode()).hexdigest()
        if self.otp != hashed_input_otp:
            logger.info("Invalid OTP.")
            return False
        self.otp = None  # Clear OTP after successful verification
        self.otp_expires_at = None
        self.save()
        logger.info("OTP verified successfully.")
        return True

    def __str__(self):
        return "Email: {}, First Name: {}, Last Name: {}".format(
            self.email,
            self.first_name,
            self.last_name
        )
