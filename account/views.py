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


def account_register(request):
    if request.method == 'POST':
        userForm = CustomUserForm(request.POST, request.FILES) # Inclua FILES para registro de foto (se aplicável)
        voterForm = VoterForm(request.POST)

        password_input = request.POST.get('password') 
        confirm_password_input = request.POST.get('confirm_password')

        # === Validação de Senha para Registro ===
        if not password_input:
            messages.error(request, "A senha é obrigatória para o registro.")
            context = {
                'form1': userForm,
                'form2': voterForm
            }
            return render(request, "voting/reg.html", context)
        
        if len(password_input) < 8:
                    messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
                    context = {
                        'form1': userForm,
                        'form2': voterForm
                    }
                    return render(request, "voting/reg.html", context)

        if password_input != confirm_password_input:
            messages.error(request, "A senha e a confirmação de senha não coincidem.")
            context = {
                'form1': userForm,
                'form2': voterForm
            }
        
            return render(request, "voting/reg.html", context)
        # =======================================

        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            
            # Define e hasheia a senha para o novo usuário
            user.set_password(password_input) 
            
            voter.admin = user
            user.save() # Salva o CustomUser
            voter.save() # Salva o Voter que tem a FK para o CustomUser
            messages.success(request, "Conta criada com sucesso! Você já pode fazer login.") 
            return redirect(reverse('account_login'))
        else:
            # Se a validação dos formulários falhar (exceto senha que tratamos acima)
            for field, errors in userForm.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field.replace('_', ' ').capitalize()}: {error}")
            for field, errors in voterForm.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field.replace('_', ' ').capitalize()}: {error}")
            
            context = {
                'form1': userForm,
                'form2': voterForm
            }
            return render(request, "voting/reg.html", context)
    else: # request.method == 'GET'
        userForm = CustomUserForm() 
        voterForm = VoterForm()     
        context = {
            'form1': userForm,
            'form2': voterForm
        }
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
        # Instancie o formulário APENAS com os campos de profile_image, first_name, last_name, email.
        # A senha será tratada fora do ModelForm.
        form = CustomUserForm(request.POST, request.FILES, instance=user)

        # Obtenha os campos de senha diretamente do POST, pois eles não estão no CustomUserForm
        current_password_input = request.POST.get('password')
        new_password_input = request.POST.get('new_password')
        confirm_password_input = request.POST.get('confirm_password')

        password_changed = False # Flag para saber se a senha foi alterada

        # === Validação e Lógica da Senha para Atualização ===
        if new_password_input: # Se uma nova senha foi fornecida, significa que o usuário quer alterar
            if new_password_input != confirm_password_input:
                messages.error(request, 'A nova senha e a confirmação não coincidem.')
                return redirect(request.META.get('HTTP_REFERER', reverse('adminDashboard')))
            
            # Verifica a senha atual antes de permitir a alteração
            if not user.check_password(current_password_input):
                messages.error(request, 'A senha atual está incorreta.')
                return redirect(request.META.get('HTTP_REFERER', reverse('adminDashboard')))
            
            # Se as validações passarem, define a nova senha para o usuário
            user.set_password(new_password_input) # Isso hasheia a senha
            password_changed = True # Marca que a senha foi alterada

        # === Validação e Lógica dos Outros Campos (first_name, last_name, email, profile_image) ===
        if form.is_valid():
            try:
                # Salva o formulário para os campos que ele gerencia (nome, email, foto de perfil)
                form.save() 
                
                # Se a senha foi alterada, salve o usuário novamente (se já não foi salvo por set_password)
                # e atualize o hash da sessão.
                if password_changed:
                    user.save() # Salva a nova senha hasheada
                    # IMPORTANTE: Isso atualiza o hash de autenticação da sessão.
                    # É VITAL para que o usuário não seja deslogado imediatamente.
                    update_session_auth_hash(request, user) 
                
                messages.success(request, 'Perfil atualizado com sucesso!')
            except Exception as e:
                logger.error(f"Erro ao salvar perfil do usuário {user.email}: {e}")
                messages.error(request, f'Erro ao atualizar o perfil: {e}')
        else:
            # Se o formulário (campos de nome, email, foto) não for válido
            logger.error(f"Erros de validação do formulário de perfil para {user.email}: {form.errors}")
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').capitalize()
                for error in errors:
                    messages.error(request, f"{field_name}: {error}")
        
        return redirect(request.META.get('HTTP_REFERER', reverse('adminDashboard')))

    return redirect(request.META.get('HTTP_REFERER', reverse('adminDashboard')))
