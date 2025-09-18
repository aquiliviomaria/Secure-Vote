# 🗳️ Sistema SecureVote: Votação Eletrónica Segura

**SecureVote: A urna, no seu bolso... a sua voz, aqui é validada!**

Um sistema de votação eletrónica robusto e seguro, desenvolvido com Django, que garante a integridade, privacidade e acessibilidade do processo eleitoral. Este projeto é ideal para gerir votações de forma eficiente e transparente.

## ✨ Funcionalidades Principais

  * ✅ **Autenticação e Autorização Robusta**: Login e registo seguro para diferentes perfis de usuário (eleitores e administradores).
  * ✅ **Gestão Abrangente de Eleições**: Administradores podem criar, configurar, monitorizar e gerir eleições e candidatos com facilidade.
  * ✅ **Votação Criptografada e Anónima**: Cada eleitor pode submeter um voto para uma eleição específica, com mecanismos que garantem o anonimato e a segurança do processo.
  * ✅ **Resultados em Tempo Real**: Visualização instantânea dos resultados à medida que a votação se desenrola e após o seu término.
  * ✅ **Temporizador Integrado**: Exibição de um temporizador para indicar o tempo restante para o início ou término da votação, mantendo os eleitores informados.
  * ✅ **Design Responsivo e Moderno**: Interface de utilizador otimizada para uma experiência consistente em dispositivos desktop e móveis.
  * ✅ **Gestão de Perfil com Foto**: Os usuários podem atualizar suas informações de perfil, incluindo o upload de uma foto de perfil.

## 🚀 Requisitos do Sistema

Certifique-se de ter os seguintes softwares instalados antes de prosseguir:

  * 🔹 **Python**: Versão 3.8 ou superior.
  * 🔹 **Django**: Versão 4.0 ou superior.
  * 🔹 **Base de Dados**: PostgreSQL (recomendado) ou qualquer outra base de dados suportada pelo Django (MySQL, SQLite, etc.).

## ⚙️ Instruções de Configuração e Instalação

Siga os passos abaixo para configurar e executar o projeto localmente:

### 1\. Clonar o Repositório

```bash
git clone https://github.com/aquiliviomaria/secure-vote.git
cd e-voting-system
```

### 2\. Criar e Ativar o Ambiente Virtual

É uma boa prática usar ambientes virtuais para isolar as dependências do projeto.

```bash
python -m venv .venv
source .venv/bin/activate  # No Linux/macOS
# No Windows: .venv\Scripts\activate
```

### 3\. Instalar as Dependências

Instale todas as bibliotecas Python necessárias listadas no `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4\. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (na mesma pasta de `manage.py`) e adicione as seguintes variáveis. **Substitua os valores pelos seus dados reais.**

```env
SECRET_KEY=sua_chave_secreta_muito_segura_aqui # Gere uma chave forte para produção
DEBUG=True # Altere para False em produção
DATABASE_URL=sua_url_da_base_de_dados # Ex: postgres://user:password@host:port/database_name
# Exemplo para SQLite (padrão do Django): DATABASE_URL=sqlite:///db.sqlite3
```

**Nota sobre `DATABASE_URL`:** Se você estiver usando SQLite para desenvolvimento, geralmente não precisa definir `DATABASE_URL` no `.env` a menos que configure o `settings.py` para lê-lo. O padrão do Django já aponta para `db.sqlite3`. Para outras bases de dados, certifique-se de que a `DATABASE_URL` está formatada corretamente para o `dj-database-url` ou configure suas credenciais diretamente em `settings.py`.

### 5\. Aplicar Migrações do Banco de Dados

Crie as tabelas do banco de dados a partir dos modelos do Django.

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6\. Criar um Superusuário (Opcional, mas recomendado para Administradores)

```bash
python manage.py createsuperuser
```

Siga as instruções no terminal para criar um usuário administrador.

### 7\. Executar o Servidor de Desenvolvimento

Inicie o servidor de desenvolvimento do Django.

```bash
python manage.py runserver
```

Acesse a aplicação no seu navegador: [http://127.0.0.1:8000/].

## 📖 Como Usar

### **Painel Administrativo (Backend)**

🛠️ Acesse o painel administrativo em [http://127.0.0.1:8000/admin/] utilizando as credenciais do superusuário criado.
🛠️ Crie e configure eleições, adicione candidatos e gerencie os usuários do sistema.

### **Portal do Eleitor (Frontend)**

🗳️ Eleitores podem registar-se ou iniciar sessão através da página principal.
🗳️ Após o login, terão acesso ao painel do eleitor, onde poderão visualizar as eleições ativas e submeter seus votos.

### **Visualização de Resultados**

📊 Os resultados da eleição podem ser visualizados em tempo real ou após o término da votação, dependendo da configuração.

## 📸 Screenshots

Aqui estão algumas imagens do sistema em funcionamento:

*Painel Administrativo*


*Listagem e Gestão de Eleições*


*Detalhes da Eleição e Temporizador*


*Interface de Votação para o Eleitor*


*Tela de Login e Registo de Usuários*


-----

## 🤝 Contribuição

Contribuições são sempre bem-vindas\! Se você deseja contribuir para o projeto, por favor, siga os passos abaixo:

1.  Faça um fork do repositório.
2.  Crie uma nova branch (`git checkout -b feature/sua-feature`).
3.  Faça suas alterações e commit-as (`git commit -m 'Adiciona nova feature'`).
4.  Envie para a branch (`git push origin feature/sua-feature`).
5.  Abra um Pull Request.

-----