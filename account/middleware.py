from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages


class AccountCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Quem é o usuário atual?
        if user.is_authenticated:
            if user.user_type == '1':  # Administrador
                if modulename == 'voting.views':
                    # A variável 'error' não está sendo usada, pode ser removida se não houver outra lógica.
                    # error = True
                    if request.path == reverse('fetch_ballot'):
                        pass
                    else:
                        messages.error(
                            request, "Você não tem acesso a este recurso."
                        )
                        return redirect(reverse('adminDashboard'))
            elif user.user_type == '2':  # Eleitor
                if modulename == 'administrator.views':
                    messages.error(
                        request, "Você não tem acesso a este recurso."
                    )
                    return redirect(reverse('voterDashboard'))
            else:  # Nenhum dos tipos de usuário acima? Leve o usuário para a página de login
                return redirect(reverse('account_login'))
        else:
            # Se o caminho for de login, registro ou qualquer coisa relacionada à autenticação, passe.
            # Removido a duplicação de 'request.path == reverse('account_login')'
            if request.path == reverse('account_login') \
                    or request.path == reverse('account_register') \
                    or modulename == 'django.contrib.auth.views': # Isso inclui todas as views de password_reset
                pass
            elif modulename == 'administrator.views' or modulename == 'voting.views':
                # Se o visitante tentar acessar funções de administrador ou eleitor
                messages.error(
                    request, "Você precisa estar logado para realizar esta operação."
                )
                return redirect(reverse('account_login'))
            else:
                # Caso padrão, redireciona para o login se não for uma página pública permitida
                return redirect(reverse('account_login'))