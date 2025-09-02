import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import User

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Generate email verification token
            user.email_verification_token = str(uuid.uuid4())
            user.save()
            
            # Send verification email
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'token': user.email_verification_token})
            )
            
            subject = 'Verify your email address'
            message = f'''
            Hi {user.get_full_name()},
            
            Thank you for registering at Blog Site!
            
            Please click the link below to verify your email address:
            {verification_url}
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            Blog Site Team
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        user.is_active = True
        user.is_email_verified = True
        user.email_verification_token = ''
        user.save()
        messages.success(request, 'Email verified successfully! You can now login.')
        return redirect('accounts:login')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
        return redirect('accounts:register')

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_email_verified:
            messages.error(self.request, 'Please verify your email address before logging in.')
            return redirect('accounts:login')
        return super().form_valid(form)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('blog:home')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_update_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_update.html', {'form': form})

@login_required
def favorites_view(request):
    favorites = request.user.favorites.all().select_related('blog', 'blog__author')
    return render(request, 'accounts/favorites.html', {'favorites': favorites})

def author_detail_view(request, username):
    author = get_object_or_404(User, username=username, role__in=['author', 'admin'])
    blogs = author.blogs.filter(status='published').order_by('-created_at')
    return render(request, 'accounts/author_detail.html', {
        'author': author,
        'blogs': blogs
    })
