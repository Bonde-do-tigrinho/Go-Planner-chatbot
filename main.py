from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from typing import List, Optional

# --- DIAGNÓSTICO DE VERSÃO ---
print(f"📚 Versão do google-generativeai instalada: {genai.__version__}")

app = FastAPI(title="Travel Activities API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# --- LÓGICA DE SELEÇÃO OTIMIZADA (PRIORIDADE: GEMINI 2.0) ---
def setup_gemini_model():
    """
    Lista os modelos e prioriza o Gemini 2.0 Flash (mais rápido).
    """
    print("🔍 Buscando modelos disponíveis na sua conta...")
    try:
        available_models = []
        # Obtém a lista exata de nomes da API
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Ordem de Preferência (Do mais rápido/novo para o mais antigo)
        priorities = [
            'models/gemini-2.0-flash',          # 1º: O mais rápido e novo (TOP)
            'models/gemini-2.0-flash-exp',      # 2º: Versão experimental do 2.0
            'models/gemini-1.5-flash',          # 3º: Flash anterior (muito bom)
            'models/gemini-1.5-flash-001',      # 4º: Flash versão estável específica
            'models/gemini-1.5-flash-latest',   # 5º: Flash alias
            'models/gemini-1.5-pro-latest',     # 6º: Pro (inteligente, mas mais lento)
            'models/gemini-pro'                 # 7º: Clássico (fallback final)
        ]

        chosen_model = None

        # Verifica qual da nossa lista de desejos existe na sua conta
        for priority in priorities:
            if priority in available_models:
                chosen_model = priority
                break
        
        # Fallback 1: Se não achou nenhum específico, pega qualquer um com "flash"
        if not chosen_model:
            for m in available_models:
                if 'flash' in m.lower():
                    chosen_model = m
                    break

        # Fallback 2: Se ainda não achou, pega o primeiro da lista geral
        if not chosen_model and available_models:
            chosen_model = available_models[0]
            
        if not chosen_model:
            raise Exception("Nenhum modelo compatível encontrado.")

        print(f"🚀 MODELO TURBO SELECIONADO: {chosen_model}")
        return genai.GenerativeModel(chosen_model)

    except Exception as e:
        print(f"❌ Erro ao configurar modelo: {e}")
        # Última esperança
        return genai.GenerativeModel('models/gemini-pro')

# Inicializa o modelo usando a função otimizada
model = setup_gemini_model()
# -------------------------------------------

class TripDestination(BaseModel):
    destination: str
    origin: Optional[str] = None
    trip_name: Optional[str] = None
    duration_days: Optional[int] = None

class Activity(BaseModel):
    title: str
    description: str
    category: str
    estimated_duration: str
    estimated_cost: str

class ChatRequest(BaseModel):
    destination: str
    message: Optional[str] = None
    context: Optional[TripDestination] = None

class ChatResponse(BaseModel):
    response: str
    activities: List[Activity]

def create_prompt(destination: str, context: Optional[TripDestination] = None) -> str:
    base_prompt = f"""Você é um assistente de viagens. Destino: {destination}.
"""
    if context:
        if context.origin: base_prompt += f"Origem: {context.origin}. "
        if context.duration_days: base_prompt += f"Duração: {context.duration_days} dias. "
    
    base_prompt += """
Liste 8 atividades turísticas. Use EXATAMENTE este formato:
---
ATIVIDADE: [Nome]
DESCRIÇÃO: [Curta]
CATEGORIA: [Tipo]
DURAÇÃO: [Tempo]
CUSTO: [Preço]
---
"""
    return base_prompt

def parse_gemini_response(response_text: str) -> List[Activity]:
    activities = []
    blocks = response_text.split("---")
    for block in blocks:
        if "ATIVIDADE:" in block:
            try:
                data = {}
                lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
                for line in lines:
                    if line.startswith("ATIVIDADE:"): data["title"] = line.split(":", 1)[1].strip()
                    elif line.startswith("DESCRIÇÃO:"): data["description"] = line.split(":", 1)[1].strip()
                    elif line.startswith("CATEGORIA:"): data["category"] = line.split(":", 1)[1].strip()
                    elif line.startswith("DURAÇÃO:"): data["estimated_duration"] = line.split(":", 1)[1].strip()
                    elif line.startswith("CUSTO:"): data["estimated_cost"] = line.split(":", 1)[1].strip()
                if len(data) >= 5: activities.append(Activity(**data))
            except: continue
    return activities

@app.get("/")
def read_root():
    return {"status": "Online"}

@app.post("/api/chat/activities", response_model=ChatResponse)
async def get_activities(request: ChatRequest):
    try:
        prompt = create_prompt(request.destination, request.context)
        
        # Gera resposta
        response = model.generate_content(prompt)
        
        activities = parse_gemini_response(response.text)
        
        if not activities:
            return ChatResponse(response=response.text, activities=[])
            
        return ChatResponse(
            response=f"Sugestões para {request.destination}:",
            activities=activities
        )
    except Exception as e:
        print(f"ERRO REQUEST: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/custom")
async def custom_chat(request: ChatRequest):
    try:
        response = model.generate_content(f"Fale sobre {request.destination}")
        return {"response": response.text, "destination": request.destination}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))