from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegisterForm
from loans.models import Loan
from customers.models import Customer

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from loans.models import Loan
from customers.models import Customer


# 🟢 REGISTER
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check existing username
        if User.objects.filter(username=username).exists():
            messages.error(request, "⚠️ Username already exists! Try another one.")
            return redirect('register')

        # Check existing email
        if User.objects.filter(email=email).exists():
            messages.error(request, "⚠️ Email already registered! Please log in.")
            return redirect('register')

        # Check password match
        if password != confirm_password:
            messages.error(request, "❌ Passwords do not match!")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "✅ Successfully Registered! Now you can log in.")
        return redirect('login')

    return render(request, 'accounts/register.html')


# 🟢 LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"👋 Welcome, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "❌ Invalid username or password!")

    return render(request, 'accounts/login.html')


# 🔵 LOGOUT
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "👋 You have been logged out successfully.")
    return redirect('login')


# 🟣 DASHBOARD
@login_required
def dashboard_view(request):
    total_customers = Customer.objects.count()
    total_loans = Loan.objects.count()
    active_loans = Loan.objects.filter(status__iexact='Active').count()

    context = {
        'total_customers': total_customers,
        'total_loans': total_loans,
        'active_loans': active_loans,
    }
    return render(request, 'dashboard.html', context)


# 🟠 CHANGE PASSWORD VIEW
@login_required
def change_password(request):
    success = False

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user
        if not user.check_password(old_password):
            messages.error(request, "❌ Old password is incorrect!")
        elif new_password != confirm_password:
            messages.warning(request, "⚠️ New passwords do not match!")
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "✅ Password updated successfully!")
            success = True

    return render(request, 'accounts/change_password.html', {'success': success})


# 🟢 PROFILE VIEW
@login_required
def profile_view(request):
    user = request.user
    return render(request, 'accounts/profile.html', {'user': user})


# 🔴 FORGOT PASSWORD VIEW (STEP 1)
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            messages.success(request, "✅ Email found! Please reset your username and password.")
            return redirect('reset_account', email=email)
        except User.DoesNotExist:
            messages.error(request, "❌ No user found with this email.")
    return render(request, 'accounts/forgot_password.html')


# 🔴 RESET ACCOUNT VIEW (STEP 2)
def reset_account(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "⚠️ Invalid email.")
        return redirect('forgot_password')

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')

        if not new_username or not new_password:
            messages.error(request, "⚠️ All fields are required.")
            return redirect('reset_account', email=email)

        user.username = new_username
        user.set_password(new_password)
        user.save()

        messages.success(request, "🎉 Account updated successfully! You can now log in.")
        return redirect('login')

    return render(request, 'accounts/reset_account.html', {'email': email})
