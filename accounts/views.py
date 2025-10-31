from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.shortcuts import render
from loans.models import  Loan
from customers.models import  Customer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# 🔹 REGISTER VIEW
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# 🔹 LOGIN VIEW
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')   # ✅ should redirect by name, not filename

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')   # ✅ corrected (removed .html)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')


# 🔹 LOGOUT VIEW
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')


# 🔹 DASHBOARD VIEW
@login_required
def dashboard_view(request):
    # 🔹 Total customers
    total_customers = Customer.objects.count()

    # 🔹 Total loans
    total_loans = Loan.objects.count()

    # 🔹 Active loans (where loan not closed or completed)
    active_loans = Loan.objects.filter(status='active').count()

    return render(request, 'dashboard.html', {
        'total_customers': total_customers,
        'total_loans': total_loans,
        'active_loans': active_loans,
    })
    return render(request, 'dashboard.html')

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@login_required
def change_password(request):
    success = False  # to show back button only after success

    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = request.user
        if not user.check_password(old_password):
            messages.error(request, "❌ Old password is incorrect!")
        elif new_password != confirm_password:
            messages.error(request, "⚠️ New passwords do not match!")
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "✅ Password updated successfully!")
            success = True  # show back button

    return render(request, 'accounts/change_password.html', {'success': success})

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def profile_view(request):
    user = request.user  # current logged-in user

    return render(request, 'accounts/profile.html', {'user': user})


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

# 🔹 Step 1: User enters email
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


# 🔹 Step 2: User resets username and password
def reset_account(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "Invalid email.")
        return redirect('forgot_password')

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')

        if not new_username or not new_password:
            messages.error(request, "All fields are required.")
            return redirect('reset_account', email=email)

        # ✅ Update username & password
        user.username = new_username
        user.set_password(new_password)
        user.save()

        messages.success(request, "🎉 Account updated successfully! You can now login.")
        return redirect('login')

    return render(request, 'accounts/reset_account.html', {'email': email})
