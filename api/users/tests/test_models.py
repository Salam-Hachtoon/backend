import hashlib, os
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta
User = get_user_model()


class UserModelTests(TestCase):
    """
    Test suite for the User model.
    Classes:
        UserModelTests: TestCase for testing the User model.
    Methods:
        setUp():
            Sets up a test user for use in the test methods.
        test_user_creation():
            Tests the creation of a user and verifies the attributes.
        test_user_str_method():
            Tests the __str__ method of the User model.
        test_user_email_unique():
            Tests that the email field is unique.
        test_superuser_creation():
            Tests the creation of a superuser and verifies the attributes.
        test_generate_otp():
            Tests the generation of a one-time password (OTP) and its attributes.
        test_verify_otp_success():
            Tests the successful verification of an OTP.
        test_verify_otp_expired():
            Tests the verification of an expired OTP.
        test_verify_otp_invalid():
            Tests the verification of an invalid OTP.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            gender='Male',
            password='testpassword123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.gender, 'Male')
        self.assertTrue(self.user.check_password('testpassword123'))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_str_method(self):
        self.assertEqual(
            str(self.user),
            'Email: testuser@example.com, First Name: Test, Last Name: User, Gender: Male'
        )

    def test_user_email_unique(self):
        with self.assertRaises(ValidationError):
            user2 = User(
                email='testuser@example.com',
                first_name='Test2',
                last_name='User2',
                gender='Male',
                password='testpassword123'
            )
            user2.full_clean()

    def test_superuser_creation(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            gender='Female',
            password='adminpassword123'
        )
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertEqual(admin_user.first_name, 'Admin')
        self.assertEqual(admin_user.last_name, 'User'),
        self.assertEqual(admin_user.gender, 'Female')
        self.assertTrue(admin_user.check_password('adminpassword123'))
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_generate_otp(self):
        otp = self.user.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
        hashed_otp = hashlib.sha256(otp.encode()).hexdigest()
        self.assertEqual(self.user.otp, hashed_otp)
        self.assertTrue(self.user.otp_expires_at > now())

    def test_verify_otp_success(self):
        otp = self.user.generate_otp()
        self.assertTrue(self.user.verify_otp(otp))
        self.assertIsNone(self.user.otp)
        self.assertIsNone(self.user.otp_expires_at)

    def test_verify_otp_expired(self):
        otp = self.user.generate_otp()
        self.user.otp_expires_at = now() - timedelta(minutes=1)
        self.user.save()
        self.assertFalse(self.user.verify_otp(otp))

    def test_verify_otp_invalid(self):
        self.user.generate_otp()
        self.assertFalse(self.user.verify_otp("123456"))
