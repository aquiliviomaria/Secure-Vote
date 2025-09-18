
# 🗳️ SecureVote – Votação Eletrónica Segura

**SecureVote: A urna, no seu bolso... a sua voz, aqui é validada!**

Um sistema de votação eletrónica **robusto, seguro e moderno**, desenvolvido com **Django**, com suporte a **PWA (Progressive Web App)**, deploy em **Docker + Fly.io**, design **responsivo para mobile** e funcionalidades avançadas de privacidade.

---

## ✨ Funcionalidades Principais

* ✅ **Autenticação e Autorização Robusta**: Login e registo seguro para diferentes perfis (eleitores e administradores).
* ✅ **Gestão de Eleições**: Criar, configurar, monitorizar e gerir eleições e candidatos com facilidade.
* ✅ **Votação Criptografada e Anónima**: Garante integridade e sigilo, com opção de **ocultar votos individuais**.
* ✅ **Resultados em Tempo Real**: Resultados exibidos em tempo real ou apenas após o término.
* ✅ **Temporizador Integrado**: Contagem regressiva para início e fim da votação.
* ✅ **Gestão de Perfil com Foto**: Utilizadores podem atualizar dados e foto de perfil.
* ✅ **Design Responsivo e Mobile-First**:

  * Interface otimizada para desktop, tablets e smartphones.
  * Layout adaptável (grid flexível, botões acessíveis, texto legível).
  * Testado em múltiplos tamanhos de ecrã.
* ✅ **PWA Completo**:

  * Instalação como app nativo (Android/iOS/PC).
  * Funcionalidade offline e cache inteligente.
  * Tela de loading com animações modernas.
  * Notificações de status (online/offline).

---

## 🛠️ Tecnologias Utilizadas

* **Backend**: Django (Python)
* **Frontend**: HTML, CSS, JavaScript, Bootstrap (responsivo)
* **Banco de Dados**: PostgreSQL (recomendado) | SQLite/MySQL (opcional)
* **Infraestrutura**: Docker + Fly.io
* **PWA**: Manifest, Service Worker, Cache Offline, Instalação Mobile

---

## 🚀 Requisitos do Sistema

* 🔹 **Python** 3.8+
* 🔹 **Django** 4.0+
* 🔹 **PostgreSQL** (ou outro DB suportado pelo Django)
* 🔹 **Docker** (para deploy)

---

## ⚙️ Instalação Local

### 1. Clonar o Repositório

```bash
git clone https://github.com/aquiliviomaria/secure-vote.git
cd secure-vote
```

### 2. Criar e Ativar Ambiente Virtual

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Criar um arquivo `.env` com:

```env
SECRET_KEY=sua_chave_secreta
DEBUG=True
DATABASE_URL=postgres://user:password@host:port/database
```

### 5. Aplicar Migrações

```bash
python manage.py migrate
```

### 6. Criar Superusuário

```bash
python manage.py createsuperuser
```

### 7. Executar Servidor

```bash
python manage.py runserver
```

Acesse em http://127.0.0.1:8000

---

## 📱 PWA – Como Testar

1. Iniciar servidor Django:

   ```bash
   python manage.py runserver
   ```
2. Abrir `http://localhost:8000` no navegador.
3. Nas DevTools (F12 → Application), verificar **Manifest** e **Service Worker**.
4. Instalar como App:

   * Chrome/Edge → botão na barra de endereços.
   * Firefox → Menu → "Instalar".
   * iOS (Safari) → Partilhar → "Adicionar à Tela Inicial".
5. Testar modo **offline**: desconectar a internet e abrir o app.

---

## 🐳 Deploy com Docker + Fly.io

### 1. Build Local

```bash
docker build -t securevote .
docker run -p 8000:8000 securevote
```

### 2. Deploy Fly.io

```bash
fly deploy --local-only
```

---

## 📸 Screenshots

* Painel Administrativo
![alt text](<Screenshot From 2025-09-18 11-15-13-1.png>)

* Interface de Votação (mobile e desktop)
mobile
![alt text](<WhatsApp Image 2025-09-18 at 11.01.48 AM.jpeg>)

desktop
![alt text](<Screenshot From 2025-09-18 11-15-13.png>)

* Tela de Login
![alt text](<WhatsApp Image 2025-09-18 at 11.01.53 AM.jpeg>)

* Loading Animado (PWA)
![alt text](<WhatsApp Image 2025-09-18 at 11.01.46 AM.jpeg>)

---

## 🤝 Contribuição

1. Fork do repositório
2. Criar branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m 'Nova feature'`
4. Push: `git push origin feature/minha-feature`
5. Pull Request 🚀

---

## 🎉 Status Atual

* ✅ Backend Django configurado
* ✅ PWA completo (manifest, SW, offline, instalação)
* ✅ Docker + Fly.io deploy funcional
* ✅ Tela de loading animada
* ✅ **Responsividade mobile garantida**
* ✅ Opção de ocultar votos para máxima privacidade

