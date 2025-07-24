from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

def login_view(request):
    """Login view that accepts username or email"""
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        if username_or_email and password:
            # Try to find user by username or email
            user = None
            try:
                user_obj = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                # If multiple users have same email, try username first
                try:
                    user_obj = User.objects.get(username=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.first_name or user.username}!')
                return redirect('bets:dashboard')
            else:
                messages.error(request, 'Credenciais inválidas.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')
    
    return render(request, 'accounts/login.html')

def register_view(request):
    """Simple registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        errors = []
        
        if not all([username, first_name, last_name, email, password1, password2]):
            errors.append('Todos os campos são obrigatórios.')
        
        if password1 != password2:
            errors.append('As passwords não coincidem.')
        
        if len(password1) < 8:
            errors.append('A password deve ter pelo menos 8 caracteres.')
        
        if User.objects.filter(username=username).exists():
            errors.append('Este username já existe.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Este email já está em uso.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'Erro ao criar conta: {str(e)}')
    
    return render(request, 'accounts/register.html')

def logout_view(request):
    """Simple logout view"""
    logout(request)
    messages.info(request, 'Sessão terminada com sucesso.')
    return redirect('accounts:login')
