from django.db import models
from django.contrib.auth.models import User
import random
import string

class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=[
        ('signup', 'Sign Up'),
        ('login', 'Login'),
        ('password_reset', 'Password Reset'),
    ])
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def generate_otp(self):
        """Generate a 6-digit OTP"""
        self.otp_code = ''.join(random.choices(string.digits, k=6))
        return self.otp_code
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.purpose}"

class LoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        username = self.user.username if self.user else "Unknown"
        return f"{status} login attempt for {username} from {self.ip_address}"
