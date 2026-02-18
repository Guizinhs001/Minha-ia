import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Minha IA", page_icon="🤖", layout="wide")

# CSS igual ChatGPT
st.markdown("""
<style>
    .stChatMessage {background-color: #f7f7f8; border-radius: 10px; padding: 15px;}
    .stChatInputContainer {position: fixed; bottom: 0; background: white;}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Configurações")
    modelo = st.selectbox("Modelo", ["gemini-1.5-flash", "gemini-1.5-pro"])
    temp = st.slider("Criatividade", 0.0, 1.0, 0.7)
    if st.button("🗑️ Limpar"):
        st.session_state.msgs = []
        st.rerun()

# Configurar API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(modelo)

# Inicializar chat
if "msgs" not in st.session_state:
    st.session_state.msgs = []

# Título
st.title("💬 Minha IA Personalizada")

# Mostrar mensagens
for msg in st.session_state.msgs:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    st.session_state.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            chat = model.start_chat(history=[])
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.msgs.append({"role": "assistant", "content": response.text})
