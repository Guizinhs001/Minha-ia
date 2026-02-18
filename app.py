import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Minha IA", page_icon="🤖", layout="wide")

# CSS estilo ChatGPT
st.markdown("""
<style>
    .stChatMessage {background-color: #f7f7f8; border-radius: 10px; padding: 15px;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Configurações")
    modelo = st.selectbox("Modelo", ["gemini-pro", "gemini-1.5-flash-latest", "gemini-1.5-pro-latest"])
    temp = st.slider("Criatividade", 0.0, 2.0, 0.7)
    if st.button("🗑️ Limpar conversa"):
        st.session_state.msgs = []
        st.rerun()
    
    st.divider()
    st.caption("Powered by Google Gemini")

# Verificar e configurar API
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ Chave API não configurada!")
    st.info("Configure em: Settings → Secrets no Streamlit Cloud")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Inicializar histórico
if "msgs" not in st.session_state:
    st.session_state.msgs = []

# Título
st.title("💬 Minha IA Personalizada")
st.caption("🚀 Conversa inteligente com Gemini")

# Mostrar histórico
for msg in st.session_state.msgs:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adicionar mensagem do usuário
    st.session_state.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Gerar resposta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                model = genai.GenerativeModel(modelo)
                
                # Converter histórico para formato do Gemini
                history = []
                for m in st.session_state.msgs[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [m["content"]]})
                
                # Iniciar chat e enviar mensagem
                chat = model.start_chat(history=history)
                response = chat.send_message(
                    prompt,
                    generation_config=genai.types.GenerationConfig(temperature=temp)
                )
                
                resposta = response.text
                st.markdown(resposta)
                st.session_state.msgs.append({"role": "assistant", "content": resposta})
                
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                if "404" in str(e):
                    st.warning("Modelo não encontrado. Tente 'gemini-pro'")
                elif "API" in str(e):
                    st.warning("Verifique sua chave API em: https://aistudio.google.com/app/apikey")
