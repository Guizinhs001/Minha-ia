import streamlit as st
import google.generativeai as genai

st.title("💬 Minha IA")

# Configurar
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Listar modelos disponíveis
@st.cache_resource
def get_models():
    try:
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return models
    except:
        return []

modelos_disponiveis = get_models()

if not modelos_disponiveis:
    st.error("❌ Nenhum modelo disponível. Crie uma NOVA chave API:")
    st.link_button("Criar chave", "https://aistudio.google.com/app/apikey")
    st.stop()

# Mostrar modelos encontrados
with st.sidebar:
    st.success(f"✅ {len(modelos_disponiveis)} modelos disponíveis")
    modelo = st.selectbox("Modelo", modelos_disponiveis)
    if st.button("🗑️ Limpar"):
        st.session_state.msgs = []
        st.rerun()

# Chat
if "msgs" not in st.session_state:
    st.session_state.msgs = []

for msg in st.session_state.msgs:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Mensagem"):
    st.session_state.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(modelo)
            response = model.generate_content(prompt)
            st.write(response.text)
            st.session_state.msgs.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro: {e}")
