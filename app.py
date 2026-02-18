import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="IA Premium VIP",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CÓDIGO MASTER (seu código secreto)
MASTER_CODE = "GuizinhsDono"

# Função para gerar hash de código
def hash_code(code):
    return hashlib.sha256(code.encode()).hexdigest()

# Inicializar session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_master" not in st.session_state:
    st.session_state.is_master = False
if "vip_until" not in st.session_state:
    st.session_state.vip_until = None
if "username" not in st.session_state:
    st.session_state.username = None
if "msgs" not in st.session_state:
    st.session_state.msgs = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "total_requests_today" not in st.session_state:
    st.session_state.total_requests_today = 0
if "theme" not in st.session_state:
    st.session_state.theme = "claro"
if "used_codes" not in st.session_state:
    st.session_state.used_codes = {}  # {hash_code: {"user": "nome", "used_at": "data"}}
if "created_codes" not in st.session_state:
    st.session_state.created_codes = {}  # {code: {"days": X, "created_by": "master", "created_at": "data", "used": False}}

# CSS personalizado
def get_css(theme="claro"):
    bg_color = "#ffffff" if theme == "claro" else "#1a1a1a"
    text_color = "#000000" if theme == "claro" else "#ffffff"
    card_bg = "#f7f7f8" if theme == "claro" else "#2d2d2d"
    
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
        
        .vip-header {{
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
            text-align: center;
        }}
        
        .vip-header h1 {{
            color: white;
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .master-badge {{
            background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            font-weight: 700;
            margin: 0.5rem 0;
            animation: pulse 2s infinite;
        }}
        
        .vip-badge {{
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            font-weight: 700;
            margin: 0.5rem 0;
        }}
        
        .free-badge {{
            background: linear-gradient(135deg, #808080 0%, #696969 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            font-weight: 700;
            margin: 0.5rem 0;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        .login-container {{
            max-width: 400px;
            margin: 5rem auto;
            padding: 2rem;
            background: {card_bg};
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .code-card {{
            background: {card_bg};
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #667eea;
        }}
        
        .stat-card {{
            background: {card_bg};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            margin: 0.5rem 0;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .stChatMessage {{
            background-color: {card_bg};
            border-radius: 15px;
            padding: 1.2rem;
            margin: 0.8rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
    </style>
    """

# Aplicar CSS
st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# Configurar API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Função para verificar se é VIP ativo
def is_vip_active():
    if st.session_state.is_master:
        return True
    if st.session_state.vip_until:
        return datetime.now() < st.session_state.vip_until
    return False

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

# ====== TELA DE LOGIN ======
if not st.session_state.authenticated:
    st.markdown("""
    <div class="vip-header">
        <h1>👑 IA PREMIUM VIP</h1>
        <p style="color: white; font-size: 1.2rem;">Sistema de Acesso Exclusivo</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown("### 🔐 Acesso ao Sistema")
    
    username = st.text_input("👤 Nome de usuário", placeholder="Digite seu nome")
    access_code = st.text_input("🎫 Código de acesso", type="password", placeholder="Cole seu código aqui")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Entrar", use_container_width=True):
            if not username or not access_code:
                st.error("❌ Preencha todos os campos!")
            else:
                code_hash = hash_code(access_code)
                
                # Verificar se é código master
                if access_code == MASTER_CODE:
                    st.session_state.authenticated = True
                    st.session_state.is_master = True
                    st.session_state.username = username
                    st.session_state.vip_until = None  # Ilimitado
                    st.success("✅ Bem-vindo, MASTER! Acesso total concedido.")
                    st.balloons()
                    st.rerun()
                
                # Verificar se o código foi criado
                elif access_code in st.session_state.created_codes:
                    code_info = st.session_state.created_codes[access_code]
                    
                    # Verificar se já foi usado
                    if code_info.get("used", False):
                        st.error("❌ Este código já foi utilizado!")
                    else:
                        # Marcar como usado
                        st.session_state.created_codes[access_code]["used"] = True
                        st.session_state.created_codes[access_code]["used_by"] = username
                        st.session_state.created_codes[access_code]["used_at"] = datetime.now().isoformat()
                        
                        # Ativar VIP
                        days = code_info["days"]
                        if days == 999:  # Código ilimitado
                            st.session_state.vip_until = datetime.now() + timedelta(days=3650)  # 10 anos
                            st.success(f"✅ Código VIP ILIMITADO ativado! Bem-vindo, {username}!")
                        else:
                            st.session_state.vip_until = datetime.now() + timedelta(days=days)
                            st.success(f"✅ Código VIP de {days} dias ativado! Bem-vindo, {username}!")
                        
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.balloons()
                        st.rerun()
                else:
                    st.error("❌ Código inválido ou não encontrado!")
    
    with col2:
        if st.button("📋 Modo Gratuito", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.username = username if username else "Visitante"
            st.session_state.is_master = False
            st.session_state.vip_until = None
            st.info("ℹ️ Entrando no modo gratuito (limitado)")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Informações sobre planos
    st.markdown("---")
    st.markdown("### 💎 Planos Disponíveis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 3rem;">🆓</div>
            <div style="font-size: 1.5rem; font-weight: 700;">Gratuito</div>
            <hr>
            <div style="text-align: left; padding: 1rem;">
                ✅ 1.500 requisições/dia<br>
                ✅ Modelos básicos<br>
                ❌ Sem histórico salvo<br>
                ❌ Suporte limitado
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 3rem;">👑</div>
            <div style="font-size: 1.5rem; font-weight: 700;">VIP</div>
            <hr>
            <div style="text-align: left; padding: 1rem;">
                ✅ Requisições ilimitadas<br>
                ✅ TODOS os modelos<br>
                ✅ Histórico permanente<br>
                ✅ Upload de imagens<br>
                ✅ Suporte prioritário
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 3rem;">🔥</div>
            <div style="font-size: 1.5rem; font-weight: 700;">MASTER</div>
            <hr>
            <div style="text-align: left; padding: 1rem;">
                ✅ Tudo do VIP<br>
                ✅ Criar códigos VIP<br>
                ✅ Painel admin<br>
                ✅ Acesso vitalício<br>
                ✅ Estatísticas completas
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# ====== PAINEL ADMIN (MASTER) ======
if st.session_state.is_master:
    with st.sidebar:
        st.markdown('<div class="master-badge">🔥 MODO MASTER</div>', unsafe_allow_html=True)
        st.markdown(f"**👤 {st.session_state.username}**")
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.is_master = False
            st.rerun()
        
        st.divider()
        
        st.markdown("### 🎫 Gerenciador de Códigos")
        
        with st.expander("➕ Criar Novo Código", expanded=True):
            novo_codigo = st.text_input("📝 Código", placeholder="Ex: VIP2024", key="new_code")
            
            tipo_codigo = st.selectbox(
                "⏱️ Duração",
                ["1 dia", "7 dias", "30 dias", "Ilimitado"],
                key="code_duration"
            )
            
            if st.button("✨ Gerar Código", use_container_width=True):
                if not novo_codigo:
                    st.error("❌ Digite um código!")
                elif novo_codigo in st.session_state.created_codes:
                    st.error("❌ Código já existe!")
                else:
                    days_map = {
                        "1 dia": 1,
                        "7 dias": 7,
                        "30 dias": 30,
                        "Ilimitado": 999
                    }
                    
                    st.session_state.created_codes[novo_codigo] = {
                        "days": days_map[tipo_codigo],
                        "created_by": st.session_state.username,
                        "created_at": datetime.now().isoformat(),
                        "used": False
                    }
                    
                    st.success(f"✅ Código '{novo_codigo}' criado com sucesso!")
                    st.code(novo_codigo)
        
        st.divider()
        
        # Listar códigos criados
        st.markdown("### 📋 Códigos Criados")
        
        if st.session_state.created_codes:
            for code, info in st.session_state.created_codes.items():
                status = "✅ USADO" if info.get("used") else "🎫 DISPONÍVEL"
                days_text = "♾️ ILIMITADO" if info["days"] == 999 else f"{info['days']} dias"
                
                with st.expander(f"{status} - {code}"):
                    st.markdown(f"""
                    **Duração:** {days_text}  
                    **Criado em:** {datetime.fromisoformat(info['created_at']).strftime('%d/%m/%Y %H:%M')}  
                    **Status:** {status}
                    """)
                    
                    if info.get("used"):
                        st.markdown(f"""
                        **Usado por:** {info.get('used_by', 'Desconhecido')}  
                        **Usado em:** {datetime.fromisoformat(info['used_at']).strftime('%d/%m/%Y %H:%M')}
                        """)
                    else:
                        st.code(code)
                        if st.button(f"🗑️ Deletar", key=f"del_{code}"):
                            del st.session_state.created_codes[code]
                            st.rerun()
        else:
            st.info("ℹ️ Nenhum código criado ainda")
        
        st.divider()
        
        # Estatísticas
        total_codes = len(st.session_state.created_codes)
        used_codes = sum(1 for c in st.session_state.created_codes.values() if c.get("used"))
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_codes}</div>
            <div style="color: #666;">Códigos Criados</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{used_codes}</div>
            <div style="color: #666;">Códigos Usados</div>
        </div>
        """, unsafe_allow_html=True)

# ====== SIDEBAR NORMAL (VIP/FREE) ======
else:
    with st.sidebar:
        # Badge de status
        if is_vip_active():
            dias_restantes = (st.session_state.vip_until - datetime.now()).days
            st.markdown(f'<div class="vip-badge">👑 VIP - {dias_restantes} dias</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="free-badge">🆓 GRATUITO</div>', unsafe_allow_html=True)
        
        st.markdown(f"**👤 {st.session_state.username}**")
        
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        
        st.divider()

# ====== CONFIGURAÇÕES GERAIS (TODOS) ======
modelos_disponiveis = get_models()

with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    
    # Seletor de modelo (VIP tem todos, FREE limitado)
    if is_vip_active():
        modelo = st.selectbox(
            "🤖 Modelo IA",
            modelos_disponiveis,
            help="✅ VIP: Acesso a TODOS os modelos!"
        )
    else:
        # Apenas modelos básicos para free
        modelos_free = [m for m in modelos_disponiveis if "flash" in m.lower()]
        if modelos_free:
            modelo = st.selectbox(
                "🤖 Modelo IA",
                modelos_free,
                help="🆓 Modo gratuito: Apenas modelos básicos"
            )
        else:
            st.error("❌ Nenhum modelo disponível")
            st.stop()
    
    # Configurações avançadas
    with st.expander("🎛️ Configurações Avançadas"):
        temperatura = st.slider("🌡️ Temperatura", 0.0, 2.0, 0.7, 0.1)
        max_tokens = st.slider("📏 Tokens máximos", 100, 8000, 2048, 100)
        top_p = st.slider("🎯 Top P", 0.0, 1.0, 0.95, 0.05)
    
    st.divider()
    
    # Upload de imagem (apenas VIP)
    uploaded_file = None
    if is_vip_active():
        uploaded_file = st.file_uploader("🖼️ Enviar imagem", type=['png', 'jpg', 'jpeg'])
    else:
        st.info("🔒 Upload de imagens apenas para VIP")
    
    st.divider()
    
    # Gerenciamento de conversas
    st.markdown("### 💾 Conversas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Salvar", use_container_width=True):
            if st.session_state.msgs:
                st.session_state.chat_history.append({
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "messages": st.session_state.msgs.copy()
                })
                st.success("✅ Salvo!")
    
    with col2:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.msgs = []
            st.rerun()
    
    # Histórico (apenas VIP salva permanente)
    if is_vip_active() and st.session_state.chat_history:
        st.markdown("#### 📚 Histórico")
        for idx, conv in enumerate(reversed(st.session_state.chat_history[-5:])):
            if st.button(f"📅 {conv['timestamp']}", key=f"conv_{idx}", use_container_width=True):
                st.session_state.msgs = conv['messages'].copy()
                st.rerun()

# ====== ÁREA PRINCIPAL ======

# Header
if st.session_state.is_master:
    st.markdown("""
    <div class="vip-header">
        <h1>🔥 PAINEL MASTER</h1>
        <p style="color: white;">Controle total do sistema</p>
    </div>
    """, unsafe_allow_html=True)
elif is_vip_active():
    st.markdown("""
    <div class="vip-header">
        <h1>👑 IA PREMIUM VIP</h1>
        <p style="color: white;">Acesso completo liberado!</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0;">🤖 IA Premium</h1>
        <p style="color: white;">Modo Gratuito - Faça upgrade para VIP!</p>
    </div>
    """, unsafe_allow_html=True)

# Chat
for idx, msg in enumerate(st.session_state.msgs):
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("💭 Digite sua mensagem..."):
    
    # Verificar limite (apenas FREE)
    if not is_vip_active():
        if st.session_state.total_requests_today >= 1500:
            st.error("❌ Limite diário atingido! Faça upgrade para VIP.")
            st.stop()
    
    # Adicionar mensagem
    st.session_state.msgs.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        if uploaded_file:
            st.image(uploaded_file, width=300)
    
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
                
                # Preparar conteúdo
                content_parts = [prompt]
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    content_parts.append(image)
                
                # Gerar resposta
                chat = model.start_chat(history=history)
                response = chat.send_message(content_parts)
                
                resposta = response.text
                
                # Incrementar contador (apenas FREE)
                if not is_vip_active():
                    st.session_state.total_requests_today += 1
                
                # Mostrar resposta
                st.markdown(resposta)
                
                # Salvar resposta
                st.session_state.msgs.append({
                    "role": "assistant",
                    "content": resposta,
                    "timestamp": datetime.now().isoformat()
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")

# Rodapé
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🤖 Modelo", modelo.split('/')[-1])

with col2:
    st.metric("💬 Mensagens", len(st.session_state.msgs))

with col3:
    if is_vip_active():
        st.metric("⚡ Status", "♾️ ILIMITADO")
    else:
        restante = 1500 - st.session_state.total_requests_today
        st.metric("⚡ Restam", f"{restante}/1500")
