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
    modelo = st.selectbox("Modelo", ["gemini-1.5-flash", "gemini-1.5-pro"])
    temp = st.slider("Criatividade", 0.0, 2.0, 0.7)
    if st.button("🗑️ Limpar conversa"):
        st.session_state.msgs = []
        st.rerun()
    
    st.divider()
    st.caption("Powered by Google Gemini 1.5")

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
st.caption("🚀 Conversa inteligente com Gemini 1.5")

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
                # Criar modelo com configuração
                model = genai.GenerativeModel(
                    model_name=modelo,
                    generation_config={
                        "temperature": temp,
                        "top_p": 0.95,
                        "top_k": 64,
                        "max_output_tokens": 8192,
                    }
                )
                
                # Converter histórico para formato correto
                history = []
                for m in st.session_state.msgs[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({
                        "role": role,
                        "parts": [{"text": m["content"]}]
                    })
                
                # Iniciar chat e enviar mensagem
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
                
                resposta = response.text
                st.markdown(resposta)
                st.session_state.msgs.append({"role": "assistant", "content": resposta})
                
            except Exception as e:
                erro = str(e)
                st.error(f"❌ Erro: {erro}")
                
                # Mensagens de ajuda específicas
                if "404" in erro or "not found" in erro.lower():
                    st.warning("🔧 **Solução:** O modelo não está disponível na sua região ou API key.")
                    st.info("✅ Teste criar uma NOVA chave API em: https://aistudio.google.com/app/apikey")
                elif "quota" in erro.lower() or "limit" in erro.lower():
                    st.warning("📊 Você atingiu o limite de requisições. Aguarde alguns minutos.")
                elif "api" in erro.lower():
                    st.warning("🔑 Problema com a chave API. Verifique se está correta e ativa.")
                    st.code(st.secrets.get("GEMINI_API_KEY", "Não configurada")[:20] + "...")
