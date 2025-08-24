# account/views.py
from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm 
from voting.forms import VoterForm 
from django.contrib.auth import login, logout, update_session_auth_hash 
from .models import CustomUser
from django.contrib.auth.decorators import login_required 
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

# Create your views here.


def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        user = EmailBackend.authenticate(request, username=request.POST.get(
            'email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("adminDashboard"))
            else:
                return redirect(reverse("voterDashboard"))
        else:
            messages.error(request, "Detalhes de login inválidos. Por favor, tente novamente.") 
            return redirect("/")

    return render(request, "voting/login.html", context)


import logging

logger = logging.getLogger(__name__)

def account_register(request):
    if request.method == 'POST':
        logger.info("POST request received for account_register")
        logger.info(f"Request POST data: {request.POST}")
        logger.info(f"Request FILES data: {request.FILES}")

        # Inicialize o formulário com os dados do POST e FILES
        userForm = CustomUserForm(request.POST, request.FILES)
        voterForm = VoterForm(request.POST)

        password_input = request.POST.get('password')
        confirm_password_input = request.POST.get('password_confirm')

        logger.info(f"Password input: {password_input}, Confirm password input: {confirm_password_input}")

        # Validação manual de senha
        if not password_input:
            logger.info("Password is empty, showing error")
            messages.error(request, "A senha é obrigatória para o registro.")
            context = {'form1': userForm, 'form2': voterForm}
            return render(request, "voting/reg.html", context)
        
        if len(password_input) < 8:
            logger.info("Password length less than 8, showing error")
            messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
            context = {'form1': userForm, 'form2': voterForm}
            return render(request, "voting/reg.html", context)
        
        if password_input != confirm_password_input:
            logger.info("Passwords do not match, showing error")
            messages.error(request, "A senha e a confirmação de senha não coincidem.")
            context = {'form1': userForm, 'form2': voterForm}
            return render(request, "voting/reg.html", context)

        # Forçar os campos de senha no formulário para evitar erros de validação
        if userForm.is_valid() and voterForm.is_valid():
            logger.info("Forms are valid, proceeding to save")
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            
            # Use a senha validada manualmente
            user.set_password(password_input)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "Conta criada com sucesso! Você já pode fazer login.")
            return redirect(reverse('account_login'))
        else:
            logger.info("Forms are invalid")
            logger.info(f"UserForm errors: {userForm.errors}")
            logger.info(f"VoterForm errors: {voterForm.errors}")
            # Exiba erros de validação dos formulários
            for field, errors in userForm.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field.replace('_', ' ').capitalize()}: {error}")
            for field, errors in voterForm.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field.replace('_', ' ').capitalize()}: {error}")
            
            context = {'form1': userForm, 'form2': voterForm}
            return render(request, "voting/reg.html", context)
    else:
        logger.info("GET request received for account_register")
        userForm = CustomUserForm()
        voterForm = VoterForm()
        context = {'form1': userForm, 'form2': voterForm}
        return render(request, "voting/reg.html", context)


def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Obrigado por nos visitar! Volte sempre.") 
    else:
        messages.error(
            request, "Você precisa estar logado para realizar esta ação.") 

    return redirect(reverse("account_login"))


@login_required
def profile_update(request):
    user = request.user

    if request.method == 'POST':
        # Inicialize o formulário apenas com os campos que devem ser sempre atualizados (exclua os campos de senha)
        form = CustomUserForm(request.POST, request.FILES, instance=user)

        # Obtenha os campos de senha diretamente do POST
        current_password_input = request.POST.get('password')
        new_password_input = request.POST.get('new_password')
        confirm_password_input = request.POST.get('confirm_password')

        password_changed = False

        # Processe a lógica de senha apenas se uma nova senha for fornecida
        if new_password_input:
            if new_password_input != confirm_password_input:
                messages.error(request, 'A nova senha e a confirmação não coincidem.')
                return redirect(request.META.get('HTTP_REFERER', reverse('adminDashboard')))
            
            if not user.check_password(current_password_input):
                messages.error(request, 'A senha atual está incorreta.')
                return redirect(request.META.get('HTTP_REFERER', reverse('adminDashboard')))
            
            user.set_password(new_password_input)
            password_changed = True
        else:
            # Se nenhuma nova senha for fornecida, remova os campos de senha da validação
            form.fields.pop('password', None)
            form.fields.pop('password_confirm', None)

        # Valide e salve o formulário (apenas campos não relacionados à senha se não houver alteração de senha)
        if form.is_valid():
            try:
                form.save()
                if password_changed:
                    user.save()
                    update_session_auth_hash(request, user)
                messages.success(request, 'Perfil atualizado com sucesso!')
            except Exception as e:
                logger.error(f"Erro ao salvar perfil do usuário {user.email}: {e}")
                messages.error(request, f'Erro ao atualizar o perfil: {e}')
        else:
            logger.error(f"Erros de validação do formulário de perfil para {user.email}: {form.errors}")
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').capitalize()
                for error in errors:
                    messages.error(request, f"{field_name}: {error}")

        return redirect(request.META.get('HTTP_REFERER', reverse('adminDashboard')))

    return redirect(request.META.get('HTTP_REFERER', reverse('adminDashboard')))