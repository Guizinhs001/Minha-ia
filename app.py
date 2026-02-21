import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta
import random
import re

# ====== CONFIGURAÇÃO ======
st.set_page_config(
    page_title="Rynmaru IA 🎮",
    page_icon="🎮",
    layout="wide"
)

# ====== CSS SIMPLES ======
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 100%);
    }
    .header-box {
        background: linear-gradient(135deg, #7b2ff7, #f107a3);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .header-box h1 {
        color: white;
        margin: 0;
    }
    .header-box p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
    }
    .chat-user {
        background: linear-gradient(135deg, #7b2ff7, #f107a3);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
    }
    .chat-bot {
        background: #1e293b;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border: 1px solid #7b2ff7;
    }
</style>
""", unsafe_allow_html=True)

# ====== INICIALIZAÇÃO ======
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_code" not in st.session_state:
    st.session_state.current_code = ""
if "api_ok" not in st.session_state:
    st.session_state.api_ok = False

# ====== API DEEPSEEK ======
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")

# Verificar API
if not DEEPSEEK_API_KEY:
    st.markdown("""
    <div class="header-box">
        <h1>🎮 RYNMARU IA</h1>
        <p>Configuração Necessária</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.error("❌ API do DeepSeek não configurada!")
    
    st.markdown("### 📋 Siga estes passos:")
    
    st.markdown("""
    **1.** Obtenha sua chave em: [platform.deepseek.com](https://platform.deepseek.com/)
    
    **2.** No Streamlit Cloud, clique em **⚙️ Settings** (canto inferior esquerdo)
    
    **3.** Vá em **Secrets**
    
    **4.** Cole exatamente isso:
    """)
    
    st.code('DEEPSEEK_API_KEY = "sk-sua-chave-aqui"', language="toml")
    
    st.markdown("**5.** Clique **Save** e depois **Reboot app**")
    
    st.stop()

# Criar cliente
try:
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
    st.session_state.api_ok = True
except Exception as e:
    st.error(f"❌ Erro ao criar cliente: {e}")
    st.stop()

# ====== FUNÇÃO PRINCIPAL ======
def gerar_com_deepseek(prompt, sistema="Você é um programador expert. Responda em português."):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

# ====== HEADER ======
st.markdown("""
<div class="header-box">
    <h1>🎮 RYNMARU IA</h1>
    <p>Gerador de Scripts com DeepSeek</p>
</div>
""", unsafe_allow_html=True)

# Status da API
if st.session_state.api_ok:
    st.success("✅ API DeepSeek conectada!")
else:
    st.error("❌ Problema com a API")

# ====== ABAS ======
tab1, tab2, tab3 = st.tabs(["🤖 Gerar Código", "💬 Chat", "📄 Ver Código"])

# ====== TAB GERAR ======
with tab1:
    st.markdown("### 🎯 O que você quer criar?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        descricao = st.text_area(
            "📝 Descreva o que quer:",
            placeholder="Ex: Um jogo de nave espacial em HTML5 para Android",
            height=100
        )
    
    with col2:
        tipo = st.selectbox(
            "📦 Tipo:",
            ["HTML5/JavaScript", "Python", "Godot 4", "Game Guardian", "Unity C#", "Discord Bot"]
        )
    
    # Botão Gerar
    if st.button("⚡ GERAR CÓDIGO", type="primary", use_container_width=True):
        if not descricao:
            st.error("❌ Digite uma descrição!")
        else:
            with st.spinner("🧠 DeepSeek está gerando..."):
                sistema = f"""Você é um expert em {tipo}. 
Crie código COMPLETO e FUNCIONAL.
Retorne APENAS o código, sem explicações.
Não use markdown com ```.
O código deve estar pronto para usar."""
                
                resultado, erro = gerar_com_deepseek(descricao, sistema)
                
                if erro:
                    st.error(f"❌ Erro: {erro}")
                elif resultado:
                    # Limpar markdown se houver
                    codigo = resultado
                    codigo = re.sub(r'^```[\w]*\n?', '', codigo)
                    codigo = re.sub(r'\n?```$', '', codigo)
                    codigo = codigo.strip()
                    
                    st.session_state.current_code = codigo
                    st.success("✅ Código gerado com sucesso!")
                    st.rerun()
    
    # Mostrar código gerado
    if st.session_state.current_code:
        st.markdown("---")
        st.markdown("### 📄 Código Gerado:")
        st.code(st.session_state.current_code, language="python")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Baixar Código",
                st.session_state.current_code,
                file_name="codigo_rynmaru.txt",
                use_container_width=True
            )
        with col2:
            if st.button("🗑️ Limpar", use_container_width=True):
                st.session_state.current_code = ""
                st.rerun()

# ====== TAB CHAT ======
with tab2:
    st.markdown("### 💬 Converse com a IA")
    
    # Mostrar histórico
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    # Input de mensagem
    mensagem = st.text_input("💭 Digite sua mensagem:", key="chat_input")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("📤 Enviar", type="primary", use_container_width=True):
            if mensagem:
                # Adicionar mensagem do usuário
                st.session_state.messages.append({"role": "user", "content": mensagem})
                
                with st.spinner("🧠 Pensando..."):
                    # Criar contexto
                    contexto = "\n".join([
                        f"{'Usuário' if m['role']=='user' else 'Assistente'}: {m['content']}"
                        for m in st.session_state.messages[-6:]
                    ])
                    
                    prompt = f"Conversa anterior:\n{contexto}\n\nResponda à última mensagem do usuário de forma útil e em português."
                    
                    resposta, erro = gerar_com_deepseek(
                        prompt,
                        "Você é Rynmaru, um assistente amigável especializado em programação e jogos. Responda em português de forma clara e útil."
                    )
                    
                    if resposta:
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": f"Erro: {erro}"})
                
                st.rerun()
            else:
                st.warning("Digite uma mensagem!")
    
    with col2:
        if st.button("🧹 Limpar Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ====== TAB VER CÓDIGO ======
with tab3:
    st.markdown("### 📄 Editor de Código")
    
    if st.session_state.current_code:
        # Editor
        codigo_editado = st.text_area(
            "✏️ Edite o código:",
            value=st.session_state.current_code,
            height=400
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Salvar Edição", use_container_width=True):
                st.session_state.current_code = codigo_editado
                st.success("✅ Salvo!")
        
        with col2:
            st.download_button(
                "📥 Baixar",
                codigo_editado,
                file_name="codigo.txt",
                use_container_width=True
            )
        
        with col3:
            if st.button("🗑️ Limpar", use_container_width=True):
                st.session_state.current_code = ""
                st.rerun()
    else:
        st.info("💡 Nenhum código gerado ainda. Vá na aba 'Gerar Código' para criar!")
        
        st.markdown("### 🚀 Exemplos de prompts:")
        st.markdown("""
        - "Crie um jogo de snake em HTML5 para celular"
        - "Script de Game Guardian para hackear moedas"
        - "Player 2D para Godot 4 com pulo e dash"
        - "Bot do Discord que responde comandos"
        - "API REST em Python com Flask"
        """)

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown("## 🎮 Rynmaru IA")
    st.markdown("---")
    
    if st.session_state.api_ok:
        st.success("🟢 API Online")
    else:
        st.error("🔴 API Offline")
    
    st.markdown("---")
    st.markdown("### 📊 Status")
    st.write(f"💬 Mensagens: {len(st.session_state.messages)}")
    st.write(f"📄 Código: {'Sim' if st.session_state.current_code else 'Não'}")
    
    st.markdown("---")
    st.markdown("### 🔧 Ações")
    
    if st.button("🔄 Resetar Tudo", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_code = ""
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by DeepSeek 🧠")

# ====== FOOTER ======
st.markdown("---")
st.caption("🎮 Rynmaru IA v1.0 | DeepSeek AI")
