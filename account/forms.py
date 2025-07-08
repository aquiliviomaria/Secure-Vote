# account/forms.py
from django import forms
from .models import CustomUser, ElectionSetting 

class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    # Removemos o campo 'password' do formulário diretamente aqui.
    # Ele será tratado separadamente na view.
    # Os campos de senha no HTML não corresponderão a um campo no ModelForm,
    # mas serão lidos diretamente do request.POST na view.

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        
        if kwargs.get('instance'):
            # Manter first_name e last_name como required=True no formulário para consistência com o modelo NOT NULL
            self.fields['first_name'].required = True 
            self.fields['last_name'].required = True  
        else: # Criação de novo usuário (Registro)
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True
            # Se fosse um formulário de registro, o campo 'password' seria adicionado aqui.
            # Mas este CustomUserForm agora é mais para os outros campos do usuário.

    def clean_email(self):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError("O email fornecido já está registado.")
        else:
            dbEmail = self.Meta.model.objects.get(id=self.instance.pk).email.lower()
            if dbEmail != formEmail:
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("O email fornecido já está registado.")
        return formEmail

    # Removemos a função clean_password daqui, ela será tratada na view.

    class Meta:
        model = CustomUser
        # O campo 'password' NÃO deve estar aqui. A senha será manipulada diretamente pela view.
        # Adicione 'profile_image' aqui.
        fields = ['first_name', 'last_name', 'email', 'profile_image'] 


class ElectionSettingForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label="Data/Hora de Início da Votação"
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label="Data/Hora de Fim da Votação"
    )
    
    title = forms.CharField(max_length=255, required=True, label="Título da Eleição")

    class Meta:
        model = ElectionSetting
        fields = ['title', 'start_time', 'end_time', 'is_active']