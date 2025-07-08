from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", 1)
        extra_fields.setdefault("last_name", "System")
        extra_fields.setdefault("first_name", "Administrator")

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "Admin"), (2, "Voter"))
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=2, choices=USER_TYPE, max_length=1)
    
    # *** NOVO CAMPO ADICIONADO PARA A FOTO DE PERFIL ***
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True) 
    # 'profile_pics/' é o subdiretório dentro de MEDIA_ROOT onde as imagens serão salvas.
    # blank=True e null=True permitem que o campo seja opcional.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        # Melhorar o __str__ para lidar com casos onde first_name ou last_name podem estar vazios
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.email:
            return self.email
        return str(self.pk) # Fallback para o ID se nada mais estiver disponível
    

class ElectionSetting(models.Model):
    # O título da eleição
    title = models.CharField(max_length=255, default="Eleições SecureVote")
    
    # Campo para a data e hora de início da eleição
    start_time = models.DateTimeField(null=True, blank=True)
    
    # Campo para a data e hora de fim da eleição
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Adicionalmente, uma flag para ativar/desativar a eleição
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Configuração Global da Eleição"
        verbose_name_plural = "Configurações Globais da Eleição"

    def __str__(self):
        return self.title

    # Métodos para verificar o status da eleição
    def is_election_active(self):
        now = timezone.now()
        return self.is_active and self.start_time and self.end_time and \
               self.start_time <= now <= self.end_time

    def is_election_ended(self):
        now = timezone.now()
        return self.is_active and self.end_time and now > self.end_time

    # Garante que só haja uma instância deste modelo
    def save(self, *args, **kwargs):
        if not self.pk and ElectionSetting.objects.exists():
            # Não permite criar mais de uma instância
            raise Exception("Só pode haver uma configuração de eleição. Edite a existente.")
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        # Carrega a única instância ou cria uma se não existir
        obj, created = cls.objects.get_or_create(pk=1) # Sempre usa PK=1
        return obj
