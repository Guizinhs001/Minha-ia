import streamlit as st
import google.generativeai as genai

st.title("💬 Minha IA")

# Configurar API
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ Chave API não encontrada! Configure em Settings → Secrets")
    st.stop()

genai.configure(api_key=api_key)

if "msgs" not in st.session_state:
    st.session_state.msgs = []

# Mostrar histórico
for msg in st.session_state.msgs:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
if prompt := st.chat_input("Mensagem"):
    st.session_state.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            resposta = response.text
            st.write(resposta)
            st.session_state.msgs.append({"role": "assistant", "content": resposta})
        except Exception as e:
            st.error(f"❌ ERRO: {e}")
            st.code(f"Tipo: {type(e).__name__}")
            if "404" in str(e) or "NotFound" in str(e):
                st.warning("O modelo não foi encontrado. Teste criar uma NOVA chave API em: https://aistudio.google.com/app/apikey")
