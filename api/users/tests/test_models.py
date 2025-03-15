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
    This test suite includes the following test cases:
    - User creation and attribute validation.
    - String representation of the User model.
    - Email uniqueness validation.
    - Superuser creation and attribute validation.
    - OTP generation and validation.
    Test Cases:
    - setUp: Initializes a test user for use in the test cases.
    - test_user_creation: Verifies that a user is created with the correct attributes.
    - test_user_str_method: Checks the string representation of the user.
    - test_user_email_unique: Ensures that the email field is unique.
    - test_superuser_creation: Verifies that a superuser is created with the correct attributes.
    - test_generate_otp: Tests the OTP generation method.
    - test_verify_otp_success: Tests successful OTP verification.
    - test_verify_otp_expired: Tests OTP verification when the OTP has expired.
    - test_verify_otp_invalid: Tests OTP verification with an invalid OTP.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertTrue(self.user.check_password('testpassword123'))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_str_method(self):
        self.assertEqual(str(self.user), 'Email: testuser@example.com, First Name: Test, Last Name: User')

    def test_user_email_unique(self):
        with self.assertRaises(ValidationError):
            user2 = User(
                email='testuser@example.com',
                first_name='Test2',
                last_name='User2',
                password='testpassword123'
            )
            user2.full_clean()

    def test_superuser_creation(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='adminpassword123'
        )
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertEqual(admin_user.first_name, 'Admin')
        self.assertEqual(admin_user.last_name, 'User')
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
