from django.shortcuts import render, redirect, reverse
from account.views import account_login
from .models import Position, Candidate, Voter, Votes
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import requests
import json

def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    context = {}
    # return render(request, "voting/login.html", context)

def generate_ballot(display_controls=False):
    positions = Position.objects.order_by('priority').all()
    output = ""
    candidates_data = ""
    num = 1
    for position in positions:
        name = position.name
        position_name = slugify(name)
        candidates = Candidate.objects.filter(position=position)
        for candidate in candidates:
            if position.max_vote > 1:
                instruction = "Podes selecionar até " + \
                    str(position.max_vote) + " candidatos"
                input_box = '<input type="checkbox" value="'+str(candidate.id)+'" class="flat-red ' + \
                    position_name+'" name="' + \
                    position_name+"[]" + '">'
            else:
                instruction = "Seleciona apenas um candidato"
                input_box = '<input value="'+str(candidate.id)+'" type="radio" class="flat-red ' + \
                    position_name+'" name="'+position_name+'">'
            image = "/media/" + str(candidate.photo)
            candidates_data = candidates_data + '<li>' + input_box + '<button type="button" class="btn btn-primary btn-sm btn-flat clist platform" data-fullname="'+candidate.fullname+'" data-bio="'+candidate.bio+'"><i class="fa fa-search"></i> Biografia</button><img src="' + \
                image+'" height="100px" width="100px" class="clist"><span class="cname clist">' + \
                candidate.fullname+'</span></li>'
        up = ''
        if position.priority == 1:
            up = 'disabled'
        down = ''
        if position.priority == positions.count():
            down = 'disabled'
        output = output + f"""<div class="row"> <div class="col-xs-12"><div class="box box-solid" id="{position.id}">
             <div class="box-header with-border">
            <h3 class="box-title"><b>{name}</b></h3>"""
        if display_controls:
            output = output + f""" <div class="pull-right box-tools">
        <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i> Mover para Cima</button>
        <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i> Mover para Baixo</button>
        </div>"""
        output = output + f"""</div>
        <div class="box-body">
        <p>{instruction}
        <span class="pull-right">
        <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Resetar</button>
        </span>
        </p>
        <div id="candidate_list">
        <ul>
        {candidates_data}
        </ul>
        </div>
        </div>
        </div>
        </div>
        </div>
        """
        position.priority = num
        position.save()
        num = num + 1
        candidates_data = ''
    return output

def fetch_ballot(request):
    output = generate_ballot(display_controls=True)
    return JsonResponse(output, safe=False)

def generate_otp():
    """Link to this function
    https://www.codespeedy.com/otp-generation-using-random-module-in-python/
    """
    import random as r
    otp = ""
    for i in range(r.randint(5, 8)):
        otp += str(r.randint(1, 9))
    return otp

def dashboard(request):
    user = request.user
    if user.voter.otp is None or user.voter.verified == False:
        if not settings.SEND_OTP:
            msg = bypass_otp()
            messages.success(request, msg)
            return redirect(reverse('show_ballot'))
        else:
            return redirect(reverse('voterVerify'))
    else:
        if user.voter.voted:
            context = {
                'my_votes': Votes.objects.filter(voter=user.voter),
            }
            return render(request, "voting/voter/result.html", context)
        else:
            return redirect(reverse('show_ballot'))

def verify(request):
    context = {
        'page_title': 'Verificação de OTP'
    }
    return render(request, "voting/voter/verify.html", context)

def resend_otp(request):
    user = request.user
    voter = user.voter
    error = False
    if settings.SEND_OTP:
        if voter.otp_sent >= 3:
            error = True
            response = "Solicitaste OTP três vezes. Não podes fazer isso novamente! Por favor, introduz o OTP enviado anteriormente."
        else:
            phone = voter.phone
            otp = voter.otp
            if otp is None:
                otp = generate_otp()
                voter.otp = otp
                voter.save()
            try:
                msg = "Caro(a) " + str(user) + ", Por favor, utiliza " + \
                    str(otp) + " como o teu OTP"
                message_is_sent = send_sms(phone, msg)
                if message_is_sent:
                    voter.otp_sent = voter.otp_sent + 1
                    voter.save()
                    response = "O OTP foi enviado para o teu número de telefone. Por favor, insere-o na caixa fornecida abaixo."
                else:
                    error = True
                    response = "OTP não enviado. Por favor, tenta novamente."
            except Exception as e:
                response = "O OTP não pôde ser enviado: " + str(e)
    else:
        response = bypass_otp()
    return JsonResponse({"data": response, "error": error})

def bypass_otp():
    Voter.objects.all().filter(otp=None, verified=False).update(otp="0000", verified=True)
    response = "Por favor, emita o seu voto."
    return response

def send_sms(phone_number, msg):
    import requests
    import os
    import json
    response = ""
    email = os.environ.get('SMS_EMAIL')
    password = os.environ.get('SMS_PASSWORD')
    if email is None or password is None:
        raise Exception("O Email/Password não pode ser nulo.")
    url = "https://app.multitexter.com/v2/app/sms"
    data = {"email": email, "password": password, "message": msg,
            "sender_name": "OTP", "recipients": phone_number, "forcednd": 1}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    response = r.json()
    status = response.get('status', 0)
    if str(status) == '1':
        return True
    else:
        return False

def verify_otp(request):
    error = True
    if request.method != 'POST':
        messages.error(request, "Acesso negado.")
    else:
        otp = request.POST.get('otp')
        if otp is None:
            messages.error(request, "Por favor, forneça um OTP válido.")
        else:
            voter = request.user.voter
            db_otp = voter.otp
            if db_otp != otp:
                messages.error(request, "O OTP fornecido não é válido.")
            else:
                messages.success(
                    request, "Agora estás verificado. Por favor, emite o teu voto."
                )
                voter.verified = True
                voter.save()
                error = False
    if error:
        return redirect(reverse('voterVerify'))
    return redirect(reverse('show_ballot'))

def show_ballot(request):
    if request.user.voter.voted:
        messages.error(request, "Já votaste.")
        return redirect(reverse('voterDashboard'))
    ballot = generate_ballot(display_controls=False)
    context = {
        'ballot': ballot
    }
    return render(request, "voting/voter/ballot.html", context)

def preview_vote(request):
    if request.method != 'POST':
        error = True
        response = "Por favor, navega pelo sistema corretamente."
    else:
        output = ""
        form = dict(request.POST)
        form.pop('csrfmiddlewaretoken', None)
        error = False
        data = []
        positions = Position.objects.all()
        for position in positions:
            max_vote = position.max_vote
            pos = slugify(position.name)
            pos_id = position.id
            if position.max_vote > 1:
                this_key = pos + "[]"
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                if len(form_position) > max_vote:
                    error = True
                    response = "Só podes escolher " + \
                        str(max_vote) + " candidatos para " + position.name
                else:
                    start_tag = f"""
                       <div class='row votelist' style='padding-bottom: 2px'>
                                <span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
                                <span class='col-sm-8'>
                                <ul style='list-style-type:none; margin-left:-40px'>
                    """
                    end_tag = "</ul></span></div><hr/>"
                    data = ""
                    for form_candidate_id in form_position:
                        try:
                            candidate = Candidate.objects.get(
                                id=form_candidate_id, position=position)
                            data += f"""
                                <li><i class="fa fa-check-square-o"></i> {candidate.fullname}</li>
                            """
                        except:
                            error = True
                            response = "Por favor, navega pelo sistema corretamente."
                    output += start_tag + data + end_tag
            else:
                this_key = pos
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                try:
                    form_position = form_position[0]
                    candidate = Candidate.objects.get(
                        position=position, id=form_position)
                    output += f"""
                            <div class='row votelist' style='padding-bottom: 2px'>
                                <span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
                                <span class='col-sm-8'><i class="fa fa-check-circle-o"></i> {candidate.fullname}</span>
                            </div>
                      <hr/>
                    """
                except Exception as e:
                    error = True
                    response = "Por favor, navega pelo sistema corretamente."
    context = {
        'error': error,
        'list': output
    }
    return JsonResponse(context, safe=False)

def submit_ballot(request):
    if request.method != 'POST':
        messages.error(request, "Por favor, navega pelo sistema corretamente.")
        return redirect(reverse('show_ballot'))
    voter = request.user.voter
    if voter.voted:
        messages.error(request, "Já votaste.")
        return redirect(reverse('voterDashboard'))
    form = dict(request.POST)
    form.pop('csrfmiddlewaretoken', None)
    form.pop('submit_vote', None)
    if len(form.keys()) < 1:
        messages.error(request, "Por favor, seleciona pelo menos um candidato.")
        return redirect(reverse('show_ballot'))
    positions = Position.objects.all()
    form_count = 0
    for position in positions:
        max_vote = position.max_vote
        pos = slugify(position.name)
        pos_id = position.id
        if position.max_vote > 1:
            this_key = pos + "[]"
            form_position = form.get(this_key)
            if form_position is None:
                continue
            if len(form_position) > max_vote:
                messages.error(request, "Só podes escolher " +
                               str(max_vote) + " candidatos para " + position.name)
                return redirect(reverse('show_ballot'))
            else:
                for form_candidate_id in form_position:
                    form_count += 1
                    try:
                        candidate = Candidate.objects.get(
                            id=form_candidate_id, position=position)
                        vote = Votes()
                        vote.candidate = candidate
                        vote.voter = voter
                        vote.position = position
                        vote.save()
                    except Exception as e:
                        messages.error(
                            request, "Por favor, navega pelo sistema corretamente. Erro: " + str(e))
                        return redirect(reverse('show_ballot'))
        else:
            this_key = pos
            form_position = form.get(this_key)
            if form_position is None:
                continue
            form_count += 1
            try:
                form_position = form_position[0]
                candidate = Candidate.objects.get(
                    position=position, id=form_position)
                vote = Votes()
                vote.candidate = candidate
                vote.voter = voter
                vote.position = position
                vote.save()
            except Exception as e:
                messages.error(
                    request, "Por favor, navega pelo sistema corretamente. Erro: " + str(e))
                return redirect(reverse('show_ballot'))
    inserted_votes = Votes.objects.filter(voter=voter)
    if (inserted_votes.count() != form_count):
        inserted_votes.delete()
        messages.error(request, "Por favor, tenta votar novamente!")
        return redirect(reverse('show_ballot'))
    else:
        voter.voted = True
        voter.save()
        messages.success(request, "Obrigado por votar!")
        return redirect(reverse('voterDashboard'))