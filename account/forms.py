from django import forms
from .models import CustomUser, ElectionSetting 

class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True, label="E-mail")
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Senha",
        min_length=8,
        help_text="A senha deve ter pelo menos 8 caracteres."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Confirmar Senha"
    )

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            # Para edição, os campos de senha não são obrigatórios
            self.fields['password'].required = False
            self.fields['password_confirm'].required = False
            self.fields['first_name'].required = True 
            self.fields['last_name'].required = True  
        else:
            # Para criação, todos os campos são obrigatórios
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

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

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:  # Apenas para novos usuários
            password = cleaned_data.get('password')
            password_confirm = cleaned_data.get('password_confirm')
            if password and password_confirm and password != password_confirm:
                self.add_error('password_confirm', "As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.pk:  # Novo usuário
            user.set_password(self.cleaned_data['password'])  # Usa a senha fornecida
            user.is_active = True  # Garante usuário ativo
            user.user_type = '2'  # Define como Voter
        # Para edição, não alteramos a senha se os campos estiverem vazios
        elif self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'profile_image', 'password', 'password_confirm']
        labels = {
            'first_name': 'Primeiro Nome',
            'last_name': 'Apelido',
            'profile_image': 'Foto de Perfil'
        }

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