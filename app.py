import streamlit as st
import requests

# ==============================
# CONFIG
# ==============================

st.set_page_config(
    page_title="Rynmaru IA",
    page_icon="🤖",
    layout="centered"
)

# ==============================
# ESTILO VISUAL (ChatGPT-like)
# ==============================

st.markdown("""
    <style>
        .user-msg {
            background-color: #2b2b2b;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 8px;
            color: white;
        }
        .bot-msg {
            background-color: #1a1a1a;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 8px;
            color: #00ffae;
        }
        .title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🤖 Rynmaru IA</div>', unsafe_allow_html=True)

# ==============================
# PEGAR SECRETS
# ==============================

API_KEY = st.secrets["API_KEY"]
API_URL = st.secrets["API_URL"]
MODEL = st.secrets["MODEL"]

# ==============================
# HISTÓRICO
# ==============================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================
# MOSTRAR CHAT
# ==============================

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg"><b>Você:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg"><b>Rynmaru IA:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

# ==============================
# INPUT
# ==============================

user_input = st.chat_input("Digite sua mensagem...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": st.session_state.messages
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
    else:
        reply = f"Erro: {response.text}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
