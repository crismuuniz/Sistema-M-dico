# Sistema de Gestão Médica (Backend)

API robusta para gestão de pacientes, jornadas clínicas e eventos médicos, desenvolvida com **FastAPI** e **SQLAlchemy**.

## 🚀 Funcionalidades
- **Autenticação Segura**: JWT (JSON Web Tokens) com Bcrypt para hash de senhas.
- **Gestão de Pacientes**: CRUD completo com vínculo ao médico (User).
- **Jornadas Clínicas**: Acompanhamento de tratamentos específicos por paciente.
- **Linha do Tempo**: Registro de eventos clínicos cronológicos dentro de cada jornada.
- **Relatório Unificado**: Endpoint que retorna o histórico completo do paciente em um único JSON.

## 🛠️ Tecnologias
- **Python 3.13+**
- **FastAPI** (Framework web)
- **Pydantic v2** (Validação de dados)
 **SQLAlchemy** (ORM para banco de dados)
* **MySQL**

## 🔧 Como Rodar o Projeto
1. Clone o repositório: `git clone ...`
2. Crie um ambiente virtual: `python -m venv venv`
3. Instale as dependências: `pip install -r requirements.txt`
4. Inicie o servidor: `uvicorn app.main:app --reload`
5. Acesse a documentação: `http://127.0.0.1:8000/docs`
