import streamlit as st
import requests

# ====== CONFIG ======
st.set_page_config(
    page_title="Rynmaru IA",
    page_icon="🤖",
    layout="centered"
)

# ====== CSS CHATGPT ======
st.markdown("""
<style>
    .stApp {
        background-color: #343541;
    }
    
    .title {
        text-align: center;
        color: white;
        font-size: 2rem;
        margin-bottom: 2rem;
    }
    
    .user-msg {
        background-color: #343541;
        color: #ececf1;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #19c37d;
    }
    
    .bot-msg {
        background-color: #444654;
        color: #d1d5db;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #8b5cf6;
    }
    
    .stTextInput > div > div > input {
        background-color: #40414f !important;
        color: white !important;
        border: 1px solid #565869 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stButton > button {
        background-color: #19c37d !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
    }
    
    .stButton > button:hover {
        background-color: #1a7f5a !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #202123;
    }
    
    .welcome {
        text-align: center;
        color: #8e8ea0;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ====== INIT ======
if "msgs" not in st.session_state:
    st.session_state.msgs = []

# ====== API ======
API_KEY = st.secrets.get("API_KEY", "")

if not API_KEY:
    st.error("❌ Configure API_KEY em Settings > Secrets")
    st.stop()

# ====== FUNÇÃO CHAT ======
def responder(msg):
    try:
        # Monta mensagens
        mensagens = [
            {"role": "system", "content": "Você é Rynmaru, um assistente amigável. Responda sempre em português."}
        ]
        
        # Adiciona histórico
        for m in st.session_state.msgs[-10:]:
            mensagens.append({"role": m["role"], "content": m["content"]})
        
        # Adiciona nova mensagem
        mensagens.append({"role": "user", "content": msg})
        
        # Tenta diferentes endpoints
        endpoints = [
            "https://api.apifreellm.com/v1/chat/completions",
            "https://apifreellm.com/api/v1/chat/completions",
            "https://api.apifreellm.com/chat/completions"
        ]
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": mensagens,
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        # Tenta cada endpoint
        for endpoint in endpoints:
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                elif response.status_code != 404:
                    return f"❌ Erro {response.status_code}: {response.text[:200]}"
            except:
                continue
        
        return "❌ Não consegui conectar à API. Verifique se a chave está correta em apifreellm.com"
        
    except Exception as e:
        return f"❌ Erro: {str(e)}"

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown("## 🤖 Rynmaru IA")
    st.markdown("---")
    
    # Teste de API
    if st.button("🔧 Testar API", use_container_width=True):
        with st.spinner("Testando..."):
            teste = responder("Diga apenas: OK")
            if "OK" in teste or "ok" in teste:
                st.success("✅ API funcionando!")
            else:
                st.error(teste)
    
    if st.button("🗑️ Nova Conversa", use_container_width=True):
        st.session_state.msgs = []
        st.rerun()
    
    st.markdown("---")
    st.write(f"💬 {len(st.session_state.msgs)} mensagens")
    
    st.markdown("---")
    st.caption("API Free LLM 🆓")
    
    with st.expander("ℹ️ Sobre a API"):
        st.markdown("""
        Verifique sua chave em:
        [apifreellm.com](https://apifreellm.com/en/api-access)
        
        Certifique-se de que:
        - A chave está ativa
        - Você tem créditos
        - Discord está vinculado
        """)

# ====== TÍTULO ======
st.markdown('<h1 class="title">🤖 Rynmaru IA</h1>', unsafe_allow_html=True)

# ====== HISTÓRICO ======
for m in st.session_state.msgs:
    if m["role"] == "user":
        st.markdown(f'<div class="user-msg"><b>👤 Você</b><br><br>{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg"><b>🤖 Rynmaru</b><br><br>{m["content"]}</div>', unsafe_allow_html=True)

# ====== INPUT ======
st.markdown("---")

col1, col2 = st.columns([5, 1])

with col1:
    texto = st.text_input(
        "Msg",
        placeholder="Digite sua mensagem...",
        label_visibility="collapsed",
        key="input"
    )

with col2:
    enviar = st.button("➤", type="primary", use_container_width=True)

# ====== ENVIAR ======
if enviar and texto:
    st.session_state.msgs.append({"role": "user", "content": texto})
    
    with st.spinner("🤔 Pensando..."):
        resp = responder(texto)
    
    st.session_state.msgs.append({"role": "assistant", "content": resp})
    st.rerun()

# ====== WELCOME ======
if not st.session_state.msgs:
    st.markdown("""
    <div class="welcome">
        <h2>👋 Olá! Sou o Rynmaru</h2>
        <p>Seu assistente de IA gratuito</p>
        <br>
        <p>💡 Pergunte qualquer coisa...</p>
        <br>
        <p style="font-size: 0.9rem; color: #6b7280;">
        Clique em "🔧 Testar API" na barra lateral para verificar a conexão
        </p>
    </div>
    """, unsafe_allow_html=True)
