from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import random
import string

from .models import OTPVerification, LoginAttempt
from core.models import UserProfile

class SignUpView(TemplateView):
    template_name = 'authentication/signup.html'
    
    def post(self, request, *args, **kwargs):
        # Handle user registration
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Basic validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return self.get(request, *args, **kwargs)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return self.get(request, *args, **kwargs)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return self.get(request, *args, **kwargs)
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Generate OTP for email verification
            otp = OTPVerification.objects.create(
                user=user,
                purpose='signup',
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            otp.generate_otp()
            otp.save()
            
            # In a real application, send OTP via email
            messages.success(request, f'Registration successful! Your OTP is: {otp.otp_code}')
            request.session['pending_user_id'] = user.id
            return redirect('authentication:verify_otp')
            
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
            return self.get(request, *args, **kwargs)

class LoginView(TemplateView):
    template_name = 'authentication/login.html'
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        # Log login attempt
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        LoginAttempt.objects.create(
            user=user,
            ip_address=ip_address,
            success=user is not None,
            user_agent=user_agent
        )
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect to next page or dashboard
            next_page = request.GET.get('next', 'dashboard:user_dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
            return self.get(request, *args, **kwargs)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('core:home')

class OTPVerificationView(TemplateView):
    template_name = 'authentication/verify_otp.html'
    
    def post(self, request, *args, **kwargs):
        otp_code = request.POST.get('otp_code')
        user_id = request.session.get('pending_user_id')
        
        if not user_id:
            messages.error(request, 'Session expired. Please try again.')
            return redirect('authentication:signup')
        
        try:
            user = User.objects.get(id=user_id)
            otp = OTPVerification.objects.filter(
                user=user,
                otp_code=otp_code,
                is_verified=False
            ).first()
            
            if not otp:
                messages.error(request, 'Invalid OTP code.')
                return self.get(request, *args, **kwargs)
            
            if otp.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return self.get(request, *args, **kwargs)
            
            # Mark as verified
            otp.is_verified = True
            otp.save()
            
            # Mark user profile as email verified
            profile = UserProfile.objects.get(user=user)
            profile.email_verified = True
            profile.save()
            
            # Log user in
            login(request, user)
            
            # Clear session
            del request.session['pending_user_id']
            
            messages.success(request, 'Email verified successfully! Welcome to AASEAANIC!')
            return redirect('dashboard:user_dashboard')
            
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('authentication:signup')

class PasswordResetView(TemplateView):
    template_name = 'authentication/password_reset.html'
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate OTP for password reset
            otp = OTPVerification.objects.create(
                user=user,
                purpose='password_reset',
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            otp.generate_otp()
            otp.save()
            
            # In a real application, send OTP via email
            messages.success(request, f'Password reset OTP sent to your email. OTP: {otp.otp_code}')
            request.session['reset_user_id'] = user.id
            return redirect('authentication:password_reset_confirm')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return self.get(request, *args, **kwargs)

class PasswordResetConfirmView(TemplateView):
    template_name = 'authentication/password_reset_confirm.html'
    
    def post(self, request, *args, **kwargs):
        otp_code = request.POST.get('otp_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user_id = request.session.get('reset_user_id')
        
        if not user_id:
            messages.error(request, 'Session expired. Please try again.')
            return redirect('authentication:password_reset')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return self.get(request, *args, **kwargs)
        
        try:
            user = User.objects.get(id=user_id)
            otp = OTPVerification.objects.filter(
                user=user,
                otp_code=otp_code,
                purpose='password_reset',
                is_verified=False
            ).first()
            
            if not otp:
                messages.error(request, 'Invalid OTP code.')
                return self.get(request, *args, **kwargs)
            
            if otp.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return self.get(request, *args, **kwargs)
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as verified
            otp.is_verified = True
            otp.save()
            
            # Clear session
            del request.session['reset_user_id']
            
            messages.success(request, 'Password reset successfully! Please log in with your new password.')
            return redirect('authentication:login')
            
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('authentication:password_reset')

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'authentication/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            context['profile'] = UserProfile.objects.create(user=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        # Update user basic info
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Update profile info
        profile.phone_number = request.POST.get('phone_number', '')
        profile.date_of_birth = request.POST.get('date_of_birth') or None
        profile.passport_number = request.POST.get('passport_number', '')
        profile.emergency_contact = request.POST.get('emergency_contact', '')
        profile.emergency_phone = request.POST.get('emergency_phone', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('authentication:profile')
