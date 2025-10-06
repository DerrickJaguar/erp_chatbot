from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ERPSignUpForm

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('erp:dashboard')
    
    if request.method == 'POST':
        form = ERPSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to ERP! Your account has been created successfully.')
            return redirect('erp:dashboard')
    else:
        form = ERPSignUpForm()
    
    return render(request, 'erp/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('erp:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('erp:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'erp/login.html')

@login_required
def dashboard_view(request):
    try:
        erp_user = request.user.erpuser
    except:
        erp_user = None
    
    context = {
        'user': request.user,
        'erp_user': erp_user
    }
    return render(request, 'erp/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('erp:login')