import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import base64
from PIL import Image
import io

# Configuração da página
st.set_page_config(
    page_title="IA Premium",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado SUPER BONITO + Modo Escuro
def get_css(theme="claro"):
    bg_color = "#ffffff" if theme == "claro" else "#1a1a1a"
    text_color = "#000000" if theme == "claro" else "#ffffff"
    card_bg = "#f7f7f8" if theme == "claro" else "#2d2d2d"
    sidebar_bg = "linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%)" if theme == "claro" else "linear-gradient(180deg, #2d2d2d 0%, #1a1a1a 100%)"
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{
            font-family: 'Inter', sans-serif;
        }}
        
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        .main-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: fadeIn 0.5s;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .main-header h1 {{
            color: white;
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }}
        
        .main-header p {{
            color: rgba(255,255,255,0.9);
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
        }}
        
        .stChatMessage {{
            background-color: {card_bg};
            border-radius: 15px;
            padding: 1.2rem;
            margin: 0.8rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        
        .stChatMessage:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        [data-testid="stSidebar"] {{
            background: {sidebar_bg};
        }}
        
        .stButton button {{
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
        }}
        
        .stButton button:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .stat-card {{
            background: {card_bg};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            margin: 0.5rem 0;
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: scale(1.05);
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .usage-bar {{
            height: 10px;
            border-radius: 10px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s;
        }}
        
        .copy-button {{
            background: transparent;
            border: 1px solid #667eea;
            color: #667eea;
            padding: 0.3rem 0.8rem;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.3s;
        }}
        
        .copy-button:hover {{
            background: #667eea;
            color: white;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .loading {{
            animation: pulse 1.5s ease-in-out infinite;
        }}
        
        .warning-banner {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            animation: shake 0.5s;
        }}
        
        @keyframes shake {{
            0%, 100% {{ transform: translateX(0); }}
            25% {{ transform: translateX(-5px); }}
            75% {{ transform: translateX(5px); }}
        }}
    </style>
    """

# Configurar API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Função para obter modelos
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

# Inicializar session state
if "msgs" not in st.session_state:
    st.session_state.msgs = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "total_requests_today" not in st.session_state:
    st.session_state.total_requests_today = 0
if "theme" not in st.session_state:
    st.session_state.theme = "claro"
if "last_reset" not in st.session_state:
    st.session_state.last_reset = datetime.now().date()

# Resetar contador diário
if datetime.now().date() > st.session_state.last_reset:
    st.session_state.total_requests_today = 0
    st.session_state.last_reset = datetime.now().date()

modelos_disponiveis = get_models()

# Aplicar CSS com tema
st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    
    # Toggle tema
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown("**Tema**")
    with col_t2:
        if st.button("🌙" if st.session_state.theme == "claro" else "☀️", key="theme_toggle"):
            st.session_state.theme = "escuro" if st.session_state.theme == "claro" else "claro"
            st.rerun()
    
    st.divider()
    
    # Seletor de modelo
    if modelos_disponiveis:
        modelo = st.selectbox(
            "🤖 Modelo IA",
            modelos_disponiveis,
            help="Escolha o modelo de IA"
        )
        
        # Indicador se suporta visão
        if "vision" in modelo.lower() or "1.5" in modelo:
            st.success("✅ Suporta imagens")
    else:
        st.error("❌ Nenhum modelo disponível")
        st.stop()
    
    # Configurações avançadas
    with st.expander("🎛️ Configurações Avançadas"):
        temperatura = st.slider("🌡️ Temperatura", 0.0, 2.0, 0.7, 0.1,
                               help="Controla a criatividade das respostas")
        max_tokens = st.slider("📏 Tokens máximos", 100, 8000, 2048, 100)
        top_p = st.slider("🎯 Top P", 0.0, 1.0, 0.95, 0.05)
    
    st.divider()
    
    # Monitoramento de uso
    st.markdown("### 📊 Uso da API")
    
    uso_hoje = st.session_state.total_requests_today
    limite_dia = 1500
    porcentagem = (uso_hoje / limite_dia) * 100
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{uso_hoje}/{limite_dia}</div>
        <div class="stat-label">Requisições Hoje</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra de progresso
    st.progress(min(porcentagem / 100, 1.0))
    
    # Alertas
    if uso_hoje >= 1450:
        st.markdown("""
        <div class="warning-banner">
            ⚠️ <b>ALERTA CRÍTICO!</b><br>
            Você está muito perto do limite diário!
        </div>
        """, unsafe_allow_html=True)
    elif uso_hoje >= 1200:
        st.warning("⚠️ Você usou mais de 80% do limite diário")
    elif uso_hoje >= 900:
        st.info("ℹ️ Você usou mais de 60% do limite")
    else:
        st.success(f"✅ Ainda restam {limite_dia - uso_hoje} requisições")
    
    # Estatísticas adicionais
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(st.session_state.msgs)}</div>
        <div class="stat-label">Mensagens nesta conversa</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(st.session_state.chat_history)}</div>
        <div class="stat-label">Conversas Salvas</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Gerenciamento de conversas
    st.markdown("### 💾 Histórico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Salvar", use_container_width=True):
            if st.session_state.msgs:
                conversation = {
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "messages": st.session_state.msgs.copy(),
                    "model": modelo,
                    "requests": st.session_state.total_requests_today
                }
                st.session_state.chat_history.append(conversation)
                st.success("✅ Salvo!")
    
    with col2:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.msgs = []
            st.rerun()
    
    # Mostrar conversas salvas
    if st.session_state.chat_history:
        st.markdown("#### 📚 Conversas Anteriores")
        for idx, conv in enumerate(reversed(st.session_state.chat_history[-5:])):  # Últimas 5
            if st.button(f"📅 {conv['timestamp']}", key=f"conv_{idx}", use_container_width=True):
                st.session_state.msgs = conv['messages'].copy()
                st.rerun()
    
    st.divider()
    
    # Exportar conversa
    if st.session_state.msgs:
        export_data = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "modelo": modelo,
            "uso_api": f"{uso_hoje}/{limite_dia}",
            "mensagens": st.session_state.msgs
        }
        
        st.download_button(
            "📥 Exportar JSON",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name=f"conversa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.divider()
    
    # Informações
    st.caption("🚀 Powered by Google Gemini")
    st.caption(f"✨ Versão Premium 3.0")
    st.caption(f"⏰ Última atualização: {datetime.now().strftime('%H:%M')}")

# ====== ÁREA PRINCIPAL ======

# Header bonito
st.markdown("""
<div class="main-header">
    <h1>🤖 IA Premium</h1>
    <p>Sua assistente inteligente com Google Gemini - Agora com monitoramento em tempo real!</p>
</div>
""", unsafe_allow_html=True)

# Upload de imagem
uploaded_file = st.file_uploader("🖼️ Enviar imagem (opcional)", type=['png', 'jpg', 'jpeg'], help="Gemini 1.5 pode analisar imagens!")

# Área de chat
chat_container = st.container()

with chat_container:
    # Mostrar mensagens
    for idx, msg in enumerate(st.session_state.msgs):
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            
            # Botão copiar para respostas da IA
            if msg["role"] == "assistant":
                if st.button(f"📋 Copiar", key=f"copy_{idx}"):
                    st.code(msg["content"])
                    st.success("✅ Copiado!")
            
            # Timestamp
            if "timestamp" in msg:
                st.caption(f"🕐 {datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')}")

# Input do usuário
if prompt := st.chat_input("💭 Digite sua mensagem...", key="chat_input"):
    
    # Verificar limite
    if st.session_state.total_requests_today >= 1500:
        st.error("❌ Você atingiu o limite diário de 1.500 requisições!")
        st.info("💡 Aguarde até amanhã ou crie uma nova chave API")
        st.stop()
    
    # Adicionar mensagem do usuário
    st.session_state.msgs.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        if uploaded_file:
            st.image(uploaded_file, width=300)
        st.caption(f"🕐 {datetime.now().strftime('%H:%M')}")
    
    # Gerar resposta
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 Pensando..."):
            try:
                model = genai.GenerativeModel(
                    modelo,
                    generation_config={
                        "temperature": temperatura,
                        "max_output_tokens": max_tokens,
                        "top_p": top_p,
                    }
                )
                
                # Construir histórico
                history = []
                for m in st.session_state.msgs[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({
                        "role": role,
                        "parts": [{"text": m["content"]}]
                    })
                
                # Preparar conteúdo (com ou sem imagem)
                content_parts = [prompt]
                
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    content_parts.append(image)
                
                # Gerar resposta
                chat = model.start_chat(history=history)
                response = chat.send_message(content_parts)
                
                resposta = response.text
                
                # Incrementar contador
                st.session_state.total_requests_today += 1
                
                # Mostrar resposta
                st.markdown(resposta)
                st.caption(f"🕐 {datetime.now().strftime('%H:%M')}")
                
                # Salvar resposta
                st.session_state.msgs.append({
                    "role": "assistant",
                    "content": resposta,
                    "timestamp": datetime.now().isoformat()
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                st.info("💡 Tente novamente ou escolha outro modelo")
                
                # Dicas específicas
                if "quota" in str(e).lower():
                    st.warning("📊 Limite de requisições atingido. Aguarde alguns minutos.")
                elif "404" in str(e):
                    st.warning("🔧 Modelo não disponível. Tente outro.")

# Rodapé com métricas
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🤖 Modelo", modelo.split('/')[-1])

with col2:
    st.metric("💬 Mensagens", len(st.session_state.msgs))

with col3:
    st.metric("📊 Uso Hoje", f"{st.session_state.total_requests_today}/1500")

with col4:
    restante = 1500 - st.session_state.total_requests_today
    st.metric("⚡ Restam", restante, delta=None if restante > 300 else "⚠️ Baixo")
