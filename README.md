# 🌍 GoPlanner AI API

API desenvolvida em **FastAPI** integrada com **Google Gemini AI**. O objetivo deste backend é fornecer inteligência artificial para o aplicativo GoPlanner, gerando sugestões de atividades turísticas, roteiros e dicas de viagem personalizadas.

## 🚀 Funcionalidades

- **Sugestão de Atividades:** Gera listas de atividades turísticas baseadas no destino, duração e origem da viagem.
- **Seleção Inteligente de Modelo:** O sistema detecta automaticamente o melhor modelo Gemini disponível na sua conta (priorizando o *Gemini 2.0 Flash* ou *1.5 Flash* para velocidade).
- **Fallback Automático:** Se o modelo principal falhar ou atingir a cota, o sistema tenta automaticamente modelos alternativos para garantir a resposta.
- **Estrutura JSON:** Respostas formatadas para fácil consumo pelo front-end (React Native).

## 🛠️ Tecnologias Utilizadas

- [Python 3.10+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Generative AI SDK](https://ai.google.dev/)
- [Uvicorn](https://www.uvicorn.org/)

---

## 📦 Como Rodar o Projeto

Siga os passos abaixo para configurar o ambiente de desenvolvimento na sua máquina.

### 1. Pré-requisitos

- Python instalado.
- Git instalado.
- Uma chave de API do Google (Gemini). [Pegue a sua aqui](https://aistudio.google.com/app/apikey).

### 2. Clonar o Repositório

Abra o terminal e rode:

```bash
git clone [https://github.com/SEU-USUARIO/Go-Planner-chatbot.git](https://github.com/SEU-USUARIO/Go-Planner-chatbot.git)
cd Go-Planner-chatbot
```

### 3. Criar Ambiente Virtual

- [Windows]: python -m venv venv .\venv\Scripts\activate
- [Mac/Linux]: python3 -m venv venv source venv/bin/activate


### 4. Instalar Dependências

pip install -r requirements.txt


### 5. Configurar Variáveis de Ambiente

Crie um arquivo chamado .env na raiz do projeto (onde está o main.py) e adicione sua chave:

``` GEMINI_API_KEY=sua_chave_aqui_sem_aspas ```


### 6. Iniciar o Servidor

uvicorn main:app --reload