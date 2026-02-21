import streamlit as st
from openai import OpenAI
import re

# ====== CONFIGURAÇÃO ======
st.set_page_config(
    page_title="Rynmaru IA 🎮",
    page_icon="🎮",
    layout="wide"
)

# ====== CSS ======
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
    .header-box h1 { color: white; margin: 0; }
    .header-box p { color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; }
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
    .error-box {
        background: #ff4444;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background: #00c853;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ====== INICIALIZAÇÃO ======
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_code" not in st.session_state:
    st.session_state.current_code = ""
if "api_testada" not in st.session_state:
    st.session_state.api_testada = False
if "api_funciona" not in st.session_state:
    st.session_state.api_funciona = False

# ====== HEADER ======
st.markdown("""
<div class="header-box">
    <h1>🎮 RYNMARU IA</h1>
    <p>Gerador de Scripts com DeepSeek</p>
</div>
""", unsafe_allow_html=True)

# ====== VERIFICAR API ======
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")

if not DEEPSEEK_API_KEY:
    st.error("❌ Chave API não configurada!")
    st.markdown("""
    ### 📋 Como configurar:
    
    1. Acesse [platform.deepseek.com](https://platform.deepseek.com/)
    2. Crie uma conta e vá em **API Keys**
    3. Crie uma nova chave
    4. No Streamlit, vá em **Settings > Secrets**
    5. Adicione:
    ```
    DEEPSEEK_API_KEY = "sk-sua-chave-aqui"
    ```
    6. Clique Save e Reboot o app
    """)
    st.stop()

# ====== CRIAR CLIENTE ======
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ====== FUNÇÃO PARA TESTAR API ======
def testar_api():
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Diga apenas: OK"}],
            max_tokens=10
        )
        return True, "Conectado!"
    except Exception as e:
        erro = str(e)
        if "401" in erro or "invalid" in erro.lower() or "authentication" in erro.lower():
            return False, "❌ CHAVE API INVÁLIDA! Crie uma nova chave no site do DeepSeek."
        elif "402" in erro or "insufficient" in erro.lower() or "balance" in erro.lower():
            return False, "❌ SEM CRÉDITOS! Adicione saldo na sua conta DeepSeek."
        elif "429" in erro:
            return False, "❌ LIMITE DE REQUISIÇÕES! Aguarde um momento."
        else:
            return False, f"❌ Erro: {erro}"

# ====== TESTAR CONEXÃO ======
with st.sidebar:
    st.markdown("## 🎮 Rynmaru IA")
    st.markdown("---")
    
    if st.button("🔄 Testar API", use_container_width=True):
        with st.spinner("Testando..."):
            funciona, msg = testar_api()
            st.session_state.api_testada = True
            st.session_state.api_funciona = funciona
            if funciona:
                st.success("✅ " + msg)
            else:
                st.error(msg)
    
    if st.session_state.api_testada:
        if st.session_state.api_funciona:
            st.success("🟢 API OK")
        else:
            st.error("🔴 API com problema")
    
    st.markdown("---")
    st.markdown("### 📊 Status")
    st.write(f"💬 Mensagens: {len(st.session_state.messages)}")
    st.write(f"📄 Código: {'✅' if st.session_state.current_code else '❌'}")
    
    st.markdown("---")
    if st.button("🗑️ Limpar Tudo", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_code = ""
        st.rerun()
    
    st.markdown("---")
    st.caption("DeepSeek AI 🧠")

# ====== FUNÇÃO GERAR ======
def gerar(prompt, sistema="Você é um programador expert. Responda em português."):
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
        erro = str(e)
        if "401" in erro or "invalid" in erro.lower():
            return None, "🔑 CHAVE INVÁLIDA! Vá em platform.deepseek.com e crie uma nova API key."
        elif "402" in erro or "insufficient" in erro.lower():
            return None, "💰 SEM CRÉDITOS! Adicione saldo na sua conta DeepSeek."
        elif "429" in erro:
            return None, "⏳ Muitas requisições! Aguarde 1 minuto."
        else:
            return None, f"Erro: {erro}"

# ====== ABAS ======
tab1, tab2, tab3 = st.tabs(["🤖 Gerar Código", "💬 Chat", "📄 Ver Código"])

# ====== TAB 1: GERAR ======
with tab1:
    st.markdown("### 🎯 O que você quer criar?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        descricao = st.text_area(
            "📝 Descreva:",
            placeholder="Ex: Jogo de nave em HTML5 para celular Android",
            height=100
        )
    
    with col2:
        tipo = st.selectbox("📦 Tipo:", [
            "HTML5 / JavaScript",
            "Python",
            "Godot 4 (GDScript)",
            "Game Guardian (Lua)",
            "Unity C#",
            "Discord Bot"
        ])
    
    if st.button("⚡ GERAR CÓDIGO", type="primary", use_container_width=True):
        if not descricao:
            st.error("Digite uma descrição!")
        else:
            with st.spinner("🧠 Gerando com DeepSeek..."):
                sistema = f"""Você é expert em {tipo}. 
Crie código COMPLETO e FUNCIONAL.
Retorne APENAS o código sem explicações.
Não use ``` markdown.
Código pronto para usar."""
                
                resultado, erro = gerar(descricao, sistema)
                
                if erro:
                    st.error(erro)
                    if "CHAVE" in erro or "CRÉDITOS" in erro:
                        st.markdown("""
                        ### 🔧 Como resolver:
                        1. Acesse [platform.deepseek.com](https://platform.deepseek.com/)
                        2. Vá em **API Keys** e crie uma NOVA chave
                        3. Verifique se tem créditos em **Billing**
                        4. Atualize em **Settings > Secrets** no Streamlit
                        5. Clique **Reboot app**
                        """)
                else:
                    # Limpar markdown
                    codigo = re.sub(r'^```[\w]*\n?', '', resultado)
                    codigo = re.sub(r'\n?```$', '', codigo).strip()
                    st.session_state.current_code = codigo
                    st.success("✅ Código gerado!")
                    st.rerun()
    
    # Mostrar código
    if st.session_state.current_code:
        st.markdown("---")
        st.markdown("### 📄 Código:")
        st.code(st.session_state.current_code)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Baixar",
                st.session_state.current_code,
                "codigo.txt",
                use_container_width=True
            )
        with col2:
            if st.button("🗑️ Limpar", use_container_width=True, key="limpar1"):
                st.session_state.current_code = ""
                st.rerun()

# ====== TAB 2: CHAT ======
with tab2:
    st.markdown("### 💬 Chat com IA")
    
    # Histórico
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    # Input
    mensagem = st.text_input("💭 Sua mensagem:", key="msg_input")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if st.button("📤 Enviar", type="primary", use_container_width=True):
            if mensagem:
                st.session_state.messages.append({"role": "user", "content": mensagem})
                
                with st.spinner("🧠 Pensando..."):
                    contexto = "\n".join([
                        f"{'User' if m['role']=='user' else 'Bot'}: {m['content']}"
                        for m in st.session_state.messages[-6:]
                    ])
                    
                    resposta, erro = gerar(
                        f"Conversa:\n{contexto}\n\nResponda:",
                        "Você é Rynmaru, assistente de programação. Responda em português, de forma útil e clara."
                    )
                    
                    if erro:
                        st.session_state.messages.append({"role": "assistant", "content": f"Erro: {erro}"})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": resposta})
                
                st.rerun()
    
    with col2:
        if st.button("🧹 Limpar", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ====== TAB 3: VER CÓDIGO ======
with tab3:
    st.markdown("### 📄 Editor")
    
    if st.session_state.current_code:
        codigo = st.text_area("✏️ Código:", st.session_state.current_code, height=400)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar", use_container_width=True):
                st.session_state.current_code = codigo
                st.success("✅ Salvo!")
        with col2:
            st.download_button("📥 Baixar", codigo, "codigo.txt", use_container_width=True)
    else:
        st.info("💡 Gere um código na primeira aba!")
        st.markdown("""
        **Exemplos:**
        - Jogo de snake em HTML5
        - Script GG para moedas infinitas
        - Player 2D para Godot 4
        - Bot Discord com comandos
        """)

st.markdown("---")
st.caption("🎮 Rynmaru IA | DeepSeek 🧠")
