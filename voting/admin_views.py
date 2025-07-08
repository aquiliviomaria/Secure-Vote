from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from account.views import account_login # Assuming this is your custom login view
from voting.models import Position, Candidate, Voter, Votes # Keep these from voting app
from account.models import ElectionSetting # <-- MUDANÇA CRÍTICA AQUI: Importar de account.models

import logging

logger = logging.getLogger(__name__)

# --- Funções auxiliares para grupos de usuários (Reafirmando do voting/views.py) ---
def is_admin(user):
    return user.groups.filter(name='Administrators').exists()

def is_voter(user):
    return user.groups.filter(name='Voters').exists()


@login_required(login_url='login') # Garante que apenas usuários logados acessem
@user_passes_test(is_admin, login_url='voterDashboard') # Redireciona para o voterDashboard se não for admin
def admin_dashboard(request): # <-- RENOMEADO PARA CLAREZA (se não o fez, faça no urls.py também)
    # If it's not the admin, redirect to their respective dashboard
    if not is_admin(request.user):
        messages.error(request, "Você não tem permissão para acessar esta área.")
        return redirect('voterDashboard') # ou para a página de login se não for nem admin nem eleitor

    context = {}
    try:
        # Obter a configuração da eleição para exibir no dashboard
        # Use o método 'load()' que você definiu no ElectionSetting do account/models.py
        election_setting = ElectionSetting.load() # <-- MUDANÇA AQUI: Usar .load()
    except Exception as e: # Capture qualquer exceção, não apenas DoesNotExist, para robustez
        election_setting = None # ou ElectionSetting() se precisar de um objeto vazio
        messages.warning(request, f"Configurações da eleição não encontradas ou erro ao carregar: {e}. Uma configuração padrão será usada ou criada.")
        logger.error(f"Erro ao carregar ElectionSetting no admin_dashboard: {e}")
        # Tentar criar se não existir (o método load() já faz isso internamente com get_or_create)
        # Se você está aqui, significa que .load() falhou, então pode haver um problema mais sério.
        # Não tente ElectionSetting.objects.create_singleton() se load() já faz o get_or_create.

    # Adicionar dados para o dashboard
    context['election_setting'] = election_setting
    context['page_title'] = "Painel de Administração" # Título da página para o admin dashboard
    context['positions_count'] = Position.objects.count()
    context['candidates_count'] = Candidate.objects.count()
    context['voters_count'] = Voter.objects.count()
    context['voted_count'] = Voter.objects.filter(voted=True).count()

    # Calcular porcentagem de votantes
    total_voters = Voter.objects.count()
    voted_voters = Voter.objects.filter(voted=True).count()
    if total_voters > 0:
        context['voted_percentage'] = (voted_voters / total_voters) * 100
    else:
        context['voted_percentage'] = 0

    return render(request, "admin/home.html", context) # Assume que seu template do dashboard é admin/home.html