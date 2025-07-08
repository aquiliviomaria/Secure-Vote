from django.shortcuts import render, reverse, redirect
from voting.models import Voter, Position, Candidate, Votes
from account.models import CustomUser, ElectionSetting 
from account.forms import CustomUserForm, ElectionSettingForm
from voting.forms import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import json
from django_renderpdf.views import PDFView
from datetime import datetime
from django.utils import timezone 


def find_n_winners(data, n):
    final_list_names = []
    candidate_data_sorted = sorted(data, key=lambda x: x['votes'], reverse=True)

    if not candidate_data_sorted:
        return "Nenhum candidato com votos registados."

    # Coleta os nomes dos principais candidatos até 'n'
    for i in range(min(n, len(candidate_data_sorted))):
        final_list_names.append(f"{candidate_data_sorted[i]['name']} ({candidate_data_sorted[i]['votes']} votos)")

    if n > 0 and len(candidate_data_sorted) > n:
        if candidate_data_sorted[n-1]['votes'] == candidate_data_sorted[n]['votes']:
            tie_score = candidate_data_sorted[n-1]['votes']
            tied_candidates = [c['name'] for c in candidate_data_sorted if c['votes'] == tie_score]
            
            if len(tied_candidates) > n:
                return f"Empate: {len(tied_candidates)} candidatos com {tie_score} votos cada."
            else:
                return f"Empate: {', '.join(final_list_names)}"
    
    return "Vencedor(a): " + ", ".join(final_list_names)


class PrintView(PDFView):
    template_name = 'admin/print.html'
    prompt_download = True

    @property
    def download_name(self):
        return "Resultados_Votacao.pdf"

    def get_context_data(self, *args, **kwargs):
        # AQUI VOCÊ TAMBÉM PODE PEGAR O TÍTULO DO ElectionSetting
        election_setting = ElectionSetting.load() # <-- ESTA LINHA ESTÁ CORRETA, BUSCA O OBJETO

        context = super().get_context_data(*args, **kwargs)
        position_data = {}
        
        for position in Position.objects.all().order_by('priority'): 
            candidate_data = []
            candidate_names = [] 
            candidate_votes = [] 
            vencedor = ""
            total_votos_posicao = 0 
            
            candidates_for_position = Candidate.objects.filter(position=position)
            
            temp_candidate_data = []
            for candidate in candidates_for_position:
                votes_count = Votes.objects.filter(candidate=candidate).count()
                temp_candidate_data.append({
                    'name': candidate.fullname,
                    'votes': votes_count
                })
                total_votos_posicao += votes_count 

            candidate_data_sorted = sorted(temp_candidate_data, key=lambda x: x['votes'], reverse=True)

            for data in candidate_data_sorted:
                candidate_data.append(data)
                candidate_names.append(data['name'])
                candidate_votes.append(data['votes'])

            if not candidate_data:
                vencedor = "Nenhum candidato registado para esta posição."
            else:
                if position.max_vote > 1:
                    vencedor = find_n_winners(candidate_data, position.max_vote)
                else:
                    vencedor_candidato = max(candidate_data, key=lambda x: x['votes'])
                    if vencedor_candidato['votes'] == 0:
                        vencedor = "Ninguém votou para esta posição ainda."
                    else:
                        count_empate = sum(1 for d in candidate_data if d.get('votes') == vencedor_candidato['votes'])
                        if count_empate > 1:
                            empatados_nomes = [d['name'] for d in candidate_data if d['votes'] == vencedor_candidato['votes']]
                            vencedor = f"Empate: {', '.join(empatados_nomes)} com {vencedor_candidato['votes']} votos cada."
                        else:
                            vencedor = f"Vencedor: {vencedor_candidato['name']} com {vencedor_candidato['votes']} votos."
            
            position_data[position.name] = {
                'candidate_data': candidate_data, 
                'winner': vencedor, 
                'max_vote': position.max_vote, 
                'total_votos_posicao': total_votos_posicao, 
                'candidate_names': json.dumps(candidate_names),
                'candidate_votes': json.dumps(candidate_votes),
            }
        
        voted_voters = Voter.objects.filter(voted=True).select_related('admin').order_by('admin__first_name', 'admin__last_name')
        
        context['voted_voters'] = voted_voters 
        context['positions'] = position_data
        context['print_date'] = datetime.now()
        # context['election_title'] = titulo # Esta linha não é mais necessária, pois passaremos o objeto completo
        context['election_setting'] = election_setting # <--- ADICIONE ESTA LINHA!

        return context


# --- As outras funções da sua view permanecem as mesmas ---

def dashboard(request):
    # Carrega a única instância de ElectionSetting para passar para o template
    election_setting = ElectionSetting.load()

    positions = Position.objects.all().order_by('priority')
    candidates = Candidate.objects.all()
    voters = Voter.objects.all()
    voted_voters = Voter.objects.filter(voted=1)
    list_of_candidates = []
    votes_count = []
    chart_data = {}

    for position in positions:
        list_of_candidates = []
        votes_count = []
        for candidate in Candidate.objects.filter(position=position):
            list_of_candidates.append(candidate.fullname)
            votes = Votes.objects.filter(candidate=candidate).count()
            votes_count.append(votes)
        chart_data[position] = {
            'candidates': list_of_candidates,
            'votes': votes_count,
            'pos_id': position.id
        }

    context = {
        'position_count': positions.count(),
        'candidate_count': candidates.count(),
        'voters_count': voters.count(),
        'voted_voters_count': voted_voters.count(),
        'positions': positions,
        'chart_data': chart_data,
        'page_title': "Painel de Controlo",
        'election_setting': election_setting, # MUITO IMPORTANTE: Passe o objeto ElectionSetting
    }
    return render(request, "admin/home.html", context)


def voters(request):
    voters = Voter.objects.all()
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm,
        'voters': voters,
        'page_title': 'Lista de Eleitores'
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "Novo eleitor criado com sucesso!")
        else:
            messages.error(request, "Falha na validação do formulário. Verifique os dados.")
    return render(request, "admin/voters.html", context)


def view_voter_by_id(request):
    voter_id = request.GET.get('id', None)
    voter = Voter.objects.filter(id=voter_id)
    context = {}
    if not voter.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        voter = voter[0]
        context['first_name'] = voter.admin.first_name
        context['last_name'] = voter.admin.last_name
        context['phone'] = voter.phone
        context['id'] = voter.id
        context['email'] = voter.admin.email
    return JsonResponse(context)


def view_position_by_id(request):
    pos_id = request.GET.get('id', None)
    pos = Position.objects.filter(id=pos_id)
    context = {}
    if not pos.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        pos = pos[0]
        context['name'] = pos.name
        context['max_vote'] = pos.max_vote
        context['id'] = pos.id
    return JsonResponse(context)


def updateVoter(request):
    if request.method != 'POST':
        messages.error(request, "Acesso Negado.")
    try:
        instance = Voter.objects.get(id=request.POST.get('id'))
        user = CustomUserForm(request.POST or None, instance=instance.admin)
        voter = VoterForm(request.POST or None, instance=instance)
        user.save()
        voter.save()
        messages.success(request, "Biografia do eleitor atualizada com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao atualizar o eleitor: {e}")
    return redirect(reverse('adminViewVoters'))


def deleteVoter(request):
    if request.method != 'POST':
        messages.error(request, "Acesso negado.")
    try:
        admin = Voter.objects.get(id=request.POST.get('id')).admin
        admin.delete()
        messages.success(request, "Eleitor foi excluído com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao excluir o eleitor: {e}")
    return redirect(reverse('adminViewVoters'))


def viewPositions(request):
    positions = Position.objects.order_by('-priority').all()
    form = PositionForm(request.POST or None)
    context = {
        'positions': positions,
        'form1': form,
        'page_title': "Posições"
    }
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.priority = positions.count() + 1
            form.save()
            messages.success(request, "Nova posição criada com sucesso!")
        else:
            messages.error(request, "Erros no formulário. Por favor, corrija-os.")
    return render(request, "admin/positions.html", context)


def updatePosition(request):
    if request.method != 'POST':
        messages.error(request, "Acesso negado.")
    try:
        instance = Position.objects.get(id=request.POST.get('id'))
        pos = PositionForm(request.POST or None, instance=instance)
        pos.save()
        messages.success(request, "A posição foi atualizada com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao atualizar a posição: {e}")
    return redirect(reverse('viewPositions'))


def deletePosition(request):
    if request.method != 'POST':
        messages.error(request, "Acesso negado.")
    try:
        pos = Position.objects.get(id=request.POST.get('id'))
        pos.delete()
        messages.success(request, "A posição foi excluída com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao excluir a posição: {e}")
    return redirect(reverse('viewPositions'))


def viewCandidates(request):
    candidates = Candidate.objects.all()
    form = CandidateForm(request.POST or None, request.FILES or None)
    context = {
        'candidates': candidates,
        'form1': form,
        'page_title': 'Candidatos'
    }
    if request.method == 'POST':
        if form.is_valid():
            form = form.save()
            messages.success(request, "Novo candidato criado com sucesso!")
        else:
            messages.error(request, "Erros no formulário. Por favor, corrija-os.")
    return render(request, "admin/candidates.html", context)


def updateCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Acesso negado.")
    try:
        candidate_id = request.POST.get('id')
        candidate = Candidate.objects.get(id=candidate_id)
        form = CandidateForm(request.POST or None,
                             request.FILES or None, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados do Candidato atualizados com sucesso!")
        else:
            messages.error(request, "O formulário contém erros. Por favor, corrija-os.")
    except Exception as e:
        messages.error(request, f"Acesso a este recurso negado ou erro inesperado: {e}")
    return redirect(reverse('viewCandidates'))


def deleteCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Acesso negado.")
    try:
        pos = Candidate.objects.get(id=request.POST.get('id'))
        pos.delete()
        messages.success(request, "Candidato foi excluído com sucesso!")
    except Exception as e:
        messages.error(request, f"Acesso a este recurso negado ou erro inesperado: {e}")
    return redirect(reverse('viewCandidates'))


def view_candidate_by_id(request):
    candidate_id = request.GET.get('id', None)
    candidate = Candidate.objects.filter(id=candidate_id)
    context = {}
    if not candidate.exists():
        context['code'] = 404
    else:
        candidate = candidate[0]
        context['code'] = 200
        context['fullname'] = candidate.fullname
        previous = CandidateForm(instance=candidate)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)


def ballot_position(request):
    context = {
        'page_title': "Posição na Cédula Eleitoral"
    }
    return render(request, "admin/ballot_position.html", context)


def update_ballot_position(request, position_id, up_or_down):
    try:
        context = {
            'error': False
        }
        position = Position.objects.get(id=position_id)
        if up_or_down == 'up':
            priority = position.priority - 1
            if priority == 0:
                context['error'] = True
                output = "Esta posição já está no topo."
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority+1))
                position.priority = priority
                position.save()
                output = "Movido para cima."
        else:
            priority = position.priority + 1
            if priority > Position.objects.all().count():
                output = "Esta posição já está na parte inferior."
                context['error'] = True
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority-1))
                position.priority = priority
                position.save()
                output = "Movido para baixo."
        context['message'] = output
    except Exception as e:
        context['message'] = f"Ocorreu um erro: {e}"

    return JsonResponse(context)


def ballot_title(request):
    # Apenas administradores podem acessar
    if request.user.user_type != '1': # Supondo '1' para Admin
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect(reverse('adminDashboard')) # Redireciona para a dashboard

    # Carrega a única instância de ElectionSetting
    election_setting = ElectionSetting.load() 

    if request.method == 'POST':
        form = ElectionSettingForm(request.POST, instance=election_setting)
        if form.is_valid():
            new_end_time = form.cleaned_data['end_time']
            current_end_time = election_setting.end_time

            # Lógica para não encurtar o tempo
            if current_end_time and new_end_time and new_end_time < current_end_time:
                messages.error(request, "Não é possível encurtar o tempo de votação. A data/hora final deve ser maior ou igual à atual.")
                return redirect(reverse('adminDashboard')) # Redireciona para a dashboard com a mensagem
            
            form.save()
            messages.success(request, "Configurações da eleição atualizadas com sucesso!")
            return redirect(reverse('adminDashboard')) # Redireciona para a dashboard
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            return redirect(reverse('adminDashboard')) # Redireciona com erros
    else:
        # Para GET requests (quando o modal é aberto)
        # O formulário será pré-preenchido no modal automaticamente pelo JS
        # Não precisamos de lógica complexa aqui, apenas retornar um HttpResponse se necessário.
        # A dashboard já passa o election_setting.
        pass


def viewVotes(request):
    votes = Votes.objects.all()
    context = {
        'votes': votes,
        'page_title': 'Votos'
    }
    return render(request, "admin/votes.html", context)


def resetVote(request):
    Votes.objects.all().delete()
    Voter.objects.all().update(voted=False, verified=False, otp=None)
    messages.success(request, "Todos os votos foram reiniciados com sucesso!")
    return redirect(reverse('viewVotes'))