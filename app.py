import streamlit as st
from anthropic import Anthropic

# ====== CONFIG ======
st.set_page_config(
    page_title="Rynmaru IA",
    page_icon="🤖",
    layout="centered"
)

# ====== CSS ESTILO CHATGPT ======
st.markdown("""
<style>
    .stApp {
        background-color: #343541;
    }
    
    .main-title {
        text-align: center;
        color: white;
        font-size: 2rem;
        margin-bottom: 2rem;
    }
    
    .user-message {
        background-color: #343541;
        color: #ececf1;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #19c37d;
    }
    
    .assistant-message {
        background-color: #444654;
        color: #d1d5db;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #8b5cf6;
    }
    
    .stTextInput > div > div > input {
        background-color: #40414f;
        color: white;
        border: 1px solid #565869;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stButton > button {
        background-color: #19c37d;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #1a7f5a;
    }
    
    [data-testid="stSidebar"] {
        background-color: #202123;
    }
    
    .sidebar-title {
        color: white;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ====== INIT ======
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====== API ======
API_KEY = st.secrets.get("ANTHROPIC_API_KEY", "")

if not API_KEY:
    st.error("❌ Configure ANTHROPIC_API_KEY em Settings > Secrets")
    st.stop()

client = Anthropic(api_key=API_KEY)

# ====== FUNÇÃO CHAT ======
def chat(mensagem):
    try:
        # Monta histórico
        historico = []
        for msg in st.session_state.messages[-10:]:
            historico.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        historico.append({"role": "user", "content": mensagem})
        
        # Chama API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system="Você é um assistente útil chamado Rynmaru. Responda em português de forma clara e amigável.",
            messages=historico
        )
        
        return response.content[0].text
    except Exception as e:
        return f"Erro: {str(e)}"

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown('<p class="sidebar-title">🤖 Rynmaru IA</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🗑️ Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    st.markdown(f"💬 **{len(st.session_state.messages)}** mensagens")
    
    st.markdown("---")
    st.caption("Powered by Claude 3.5")

# ====== TÍTULO ======
st.markdown('<h1 class="main-title">🤖 Rynmaru IA</h1>', unsafe_allow_html=True)

# ====== HISTÓRICO ======
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'''
        <div class="user-message">
            <strong>👤 Você</strong><br><br>
            {msg["content"]}
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="assistant-message">
            <strong>🤖 Rynmaru</strong><br><br>
            {msg["content"]}
        </div>
        ''', unsafe_allow_html=True)

# ====== INPUT ======
st.markdown("---")

col1, col2 = st.columns([5, 1])

with col1:
    entrada = st.text_input(
        "Mensagem",
        placeholder="Digite sua mensagem...",
        label_visibility="collapsed",
        key="input"
    )

with col2:
    enviar = st.button("Enviar", type="primary", use_container_width=True)

# ====== ENVIAR ======
if enviar and entrada:
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": entrada})
    
    # Gera resposta
    with st.spinner("Pensando..."):
        resposta = chat(entrada)
    
    # Adiciona resposta
    st.session_state.messages.append({"role": "assistant", "content": resposta})
    
    st.rerun()

# ====== FOOTER ======
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; color: #8e8ea0; margin-top: 3rem;">
        <p>👋 Olá! Sou o Rynmaru, seu assistente de IA.</p>
        <p>Pergunte qualquer coisa!</p>
    </div>
    """, unsafe_allow_html=True)
