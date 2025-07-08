# voting/context_processors.py
from account.models import ElectionSetting # Correct: Import from account.models
import logging
from django.utils import timezone # Adicionar esta importação para timezone.now()

logger = logging.getLogger(__name__)

def election_settings_processor(request): # <-- THIS IS THE FUNCTION DJANGO IS LOOKING FOR
    context = {}
    try:
        election_setting = ElectionSetting.load()
        context['election_setting'] = election_setting
        context['TITLE'] = election_setting.title
    except Exception as e:
        logger.error(f"Error in election_settings_processor: {e}")
        context['election_setting'] = None
        context['TITLE'] = "Eleição Não Configurada"

    if context['election_setting']:
        now = timezone.now()
        is_active = context['election_setting'].is_active
        start_time = context['election_setting'].start_time
        end_time = context['election_setting'].end_time

        if not is_active:
            context['election_status_message'] = "A eleição está inativa."
            context['election_is_votable'] = False
        elif start_time and end_time and not (start_time <= now <= end_time):
            if now < start_time:
                context['election_status_message'] = "A votação ainda não começou."
                context['election_is_votable'] = False
                # Calculate time to start for countdowns in templates (optional)
                context['time_to_start'] = start_time - now
            elif now > end_time:
                context['election_status_message'] = "A votação já terminou."
                context['election_is_votable'] = False
                # Calculate time since end for results display (optional)
                context['time_since_end'] = now - end_time
            else:
                context['election_status_message'] = "Status de tempo indefinido."
                context['election_is_votable'] = False
        elif not start_time or not end_time:
            context['election_status_message'] = "As datas de início/fim da eleição não estão configuradas."
            context['election_is_votable'] = False
        else:
            context['election_status_message'] = "A votação está em andamento."
            context['election_is_votable'] = True
            # Calculate time remaining for countdowns in templates (optional)
            context['time_remaining'] = end_time - now
    else:
        context['election_status_message'] = "Configurações da eleição não carregadas."
        context['election_is_votable'] = False

    return context