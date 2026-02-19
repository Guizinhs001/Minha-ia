import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
import re
import extra_streamlit_components as stx

# Configuração
st.set_page_config(
    page_title="ScriptMaster AI 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CÓDIGO MASTER
MASTER_CODE = "GuizinhsDono"

# Gerenciador de cookies
@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()

cookie_manager = get_cookie_manager()

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@400;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .header-premium {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .header-premium h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .master-badge {
        background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ====== FUNÇÕES DE COOKIE ======

def save_login_cookie(username, is_master, vip_until):
    """Salva login nos cookies"""
    try:
        login_data = {
            "username": username,
            "is_master": is_master,
            "vip_until": vip_until.isoformat() if vip_until else None,
            "saved_at": datetime.now().isoformat()
        }
        
        # Salvar como JSON no cookie (expira em 365 dias)
        cookie_manager.set(
            "scriptmaster_login", 
            json.dumps(login_data),
            expires_at=datetime.now() + timedelta(days=365)
        )
        return True
    except Exception as e:
        st.warning(f"Aviso: Não foi possível salvar login automaticamente")
        return False

def load_login_cookie():
    """Carrega login dos cookies"""
    try:
        cookies = cookie_manager.get_all()
        
        if cookies and "scriptmaster_login" in cookies:
            login_data = json.loads(cookies["scriptmaster_login"])
            
            # Restaurar sessão
            st.session_state.username = login_data["username"]
            st.session_state.is_master = login_data["is_master"]
            
            if login_data["vip_until"]:
                vip_date = datetime.fromisoformat(login_data["vip_until"])
                # Verificar se ainda é válido
                if vip_date > datetime.now():
                    st.session_state.vip_until = vip_date
                else:
                    st.session_state.vip_until = None
            
            st.session_state.authenticated = True
            return True
        
        return False
    except Exception as e:
        return False

def delete_login_cookie():
    """Remove login dos cookies"""
    try:
        cookie_manager.delete("scriptmaster_login")
        return True
    except:
        return False

# Inicializar session state
default_states = {
    "authenticated": False,
    "is_master": False,
    "vip_until": None,
    "username": None,
    "current_script": "",
    "saved_scripts": [],
    "created_codes": {},
    "auto_login_attempted": False
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ====== TENTAR AUTO-LOGIN (UMA VEZ) ======
if not st.session_state.authenticated and not st.session_state.auto_login_attempted:
    st.session_state.auto_login_attempted = True
    if load_login_cookie():
        st.success(f"✅ Bem-vindo de volta, {st.session_state.username}! 🎉")
        st.balloons()
        # Forçar rerun para atualizar interface
        st.rerun()

# Configurar API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("❌ Chave API não configurada!")
    st.stop()

def is_vip_active():
    if st.session_state.is_master:
        return True
    if st.session_state.vip_until:
        return datetime.now() < st.session_state.vip_until
    return False

@st.cache_resource
def get_models():
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except:
        return []

# ====== TELA DE LOGIN ======
if not st.session_state.authenticated:
    st.markdown("""
    <div class="header-premium">
        <h1>🎮 ScriptMaster AI</h1>
        <p style="color: white; font-size: 1.2rem;">Gerador de Scripts e Jogos com IA</p>
        <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">🔐 Login automático com cookies - Faça login uma vez!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Fazer Login")
        
        username = st.text_input("👤 Seu nome", placeholder="Digite seu nome", key="login_username")
        access_code = st.text_input("🎫 Código de acesso", type="password", placeholder="GuizinhsDono ou código VIP", key="login_code")
        
        # Checkbox "Lembrar de mim"
        remember_me = st.checkbox("🔒 Lembrar de mim (login automático)", value=True)
        
        st.caption("✅ Seus dados ficam salvos de forma segura no navegador")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 ENTRAR", use_container_width=True, type="primary"):
                if not username:
                    st.error("❌ Digite seu nome!")
                elif not access_code:
                    st.error("❌ Digite o código de acesso!")
                elif access_code == MASTER_CODE:
                    # Login MASTER
                    st.session_state.authenticated = True
                    st.session_state.is_master = True
                    st.session_state.username = username
                    st.session_state.vip_until = None
                    
                    # Salvar cookie se marcado
                    if remember_me:
                        save_login_cookie(username, True, None)
                    
                    st.success(f"✅ Bem-vindo, MASTER {username}!")
                    st.balloons()
                    st.rerun()
                    
                elif access_code in st.session_state.created_codes:
                    # Login VIP
                    code_info = st.session_state.created_codes[access_code]
                    
                    if not code_info.get("used"):
                        st.session_state.created_codes[access_code]["used"] = True
                        st.session_state.created_codes[access_code]["used_by"] = username
                        st.session_state.created_codes[access_code]["used_at"] = datetime.now().isoformat()
                        
                        days = code_info["days"]
                        vip_until = datetime.now() + timedelta(days=days if days != 999 else 3650)
                        
                        st.session_state.authenticated = True
                        st.session_state.is_master = False
                        st.session_state.username = username
                        st.session_state.vip_until = vip_until
                        
                        # Salvar cookie
                        if remember_me:
                            save_login_cookie(username, False, vip_until)
                        
                        dias_texto = "ILIMITADO" if days == 999 else f"{days} dias"
                        st.success(f"✅ VIP ativado por {dias_texto}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Este código já foi usado!")
                else:
                    st.error("❌ Código inválido!")
        
        with col_btn2:
            if st.button("🆓 Modo Grátis", use_container_width=True):
                username_final = username if username else "Visitante"
                
                st.session_state.authenticated = True
                st.session_state.username = username_final
                st.session_state.is_master = False
                st.session_state.vip_until = None
                
                # Salvar cookie se marcado
                if remember_me:
                    save_login_cookie(username_final, False, None)
                
                st.info(f"ℹ️ Modo gratuito ativado para {username_final}")
                st.rerun()
        
        st.divider()
        
        st.info("""
        💡 **Como funciona o login automático:**
        
        ✅ Marque "Lembrar de mim" ao fazer login
        
        ✅ Seus dados ficam salvos nos cookies do navegador
        
        ✅ Na próxima vez, você entra automaticamente
        
        ✅ Funciona mesmo fechando o navegador
        
        🔒 Para sair, use o botão "Sair" no menu lateral
        """)
    
    with col2:
        st.markdown("### 🎯 Recursos Disponíveis")
        st.markdown("""
        **🎮 Criar Jogos:**
        - Godot 4.6 (GDScript/C#)
        - Unity (C#)
        - HTML5 (Phaser, Canvas)
        - React Native Mobile
        
        **💻 Gerar Scripts:**
        - Python (Bot, Scraper, API)
        - JavaScript/Node.js
        - Discord/Telegram Bots
        - SQL, Bash, PowerShell
        
        **🆓 MODO GRATUITO:**
        - ✅ Geração básica de código
        - ✅ Templates simples
        - ⚠️ Limite de uso
        
        **👑 MODO VIP:**
        - ✅ Geração ILIMITADA
        - ✅ TODOS os templates
        - ✅ Salvar scripts
        - ✅ Sem anúncios
        
        **🔥 MODO MASTER:**
        - ✅ Tudo do VIP
        - ✅ Criar códigos VIP
        - ✅ Painel admin
        - ✅ Acesso total
        """)
        
        st.divider()
        
        st.markdown("### 🎁 Código MASTER")
        st.code("GuizinhsDono", language=None)
        st.caption("Use este código para acesso MASTER total")
    
    st.stop()

# ====== SIDEBAR (LOGADO) ======
with st.sidebar:
    # Boas-vindas
    st.markdown(f"""
    <div class="welcome-box">
        <h3 style="margin:0;">👋 Olá, {st.session_state.username}!</h3>
        <p style="margin:0.5rem 0 0 0; font-size: 0.9rem;">
            ✅ Login salvo automaticamente
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Badge
    if st.session_state.is_master:
        st.markdown('<div class="master-badge">🔥 MASTER</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 🎫 Criar Códigos VIP")
        
        with st.expander("➕ Novo Código"):
            novo_codigo = st.text_input("📝 Nome", key="new_code", placeholder="VIP2024")
            tipo = st.selectbox("⏱️ Duração", ["1 dia", "7 dias", "30 dias", "Ilimitado"])
            
            if st.button("✨ Gerar", use_container_width=True):
                if novo_codigo and novo_codigo not in st.session_state.created_codes:
                    days_map = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                    st.session_state.created_codes[novo_codigo] = {
                        "days": days_map[tipo],
                        "created_at": datetime.now().isoformat(),
                        "used": False
                    }
                    st.success("✅ Código criado!")
                    st.code(novo_codigo)
        
        if st.session_state.created_codes:
            st.markdown("### 📋 Códigos")
            for code, info in list(st.session_state.created_codes.items())[:10]:
                status = "✅" if info.get("used") else "🎫"
                days = "♾️" if info["days"] == 999 else f"{info['days']}d"
                user = f" ({info.get('used_by', '')})" if info.get("used") else ""
                st.text(f"{status} {code} {days}{user}")
        
        st.divider()
    
    elif is_vip_active():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<div class="vip-badge">👑 VIP - {dias}d</div>', unsafe_allow_html=True)
        st.divider()
    else:
        st.info("🆓 Modo Gratuito")
        st.divider()
    
    # BOTÃO SAIR
    if st.button("🚪 SAIR DA CONTA", use_container_width=True, type="secondary"):
        # Limpar cookie
        delete_login_cookie()
        
        # Limpar session
        for key in ['authenticated', 'is_master', 'vip_until', 'username', 'auto_login_attempted']:
            if key in st.session_state:
                st.session_state[key] = False if key != 'auto_login_attempted' else False
        
        st.success("✅ Você saiu com sucesso!")
        st.info("🔄 Recarregando...")
        st.rerun()
    
    st.caption("💾 Seu login está salvo nos cookies")
    
    st.divider()
    
    # Templates
    st.markdown("### 📚 Templates")
    
    templates = {
        "🎮 Godot Mobile": "godot",
        "🌐 HTML5 Game": "html5",
        "🐍 Web Scraper": "scraper",
        "🤖 Discord Bot": "discord",
        "📱 React Native": "react"
    }
    
    for name, key in templates.items():
        if st.button(name, use_container_width=True, key=f"temp_{key}"):
            st.info(f"Template {name} selecionado!")
    
    st.divider()
    
    # Scripts salvos
    if st.session_state.saved_scripts:
        st.markdown("### 💾 Salvos")
        for idx, script in enumerate(st.session_state.saved_scripts[-5:]):
            if st.button(f"📄 {script['name']}", key=f"saved_{idx}", use_container_width=True):
                st.session_state.current_script = script['code']
                st.rerun()
    
    st.caption(f"📊 {len(st.session_state.saved_scripts)} scripts")

# ====== ÁREA PRINCIPAL ======

st.markdown("""
<div class="header-premium">
    <h1>🎮 ScriptMaster AI</h1>
    <p style="color: white;">Gerador de Scripts e Jogos com IA</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🤖 Gerar", "💻 Editor", "📚 Biblioteca"])

# TAB 1: GERAR
with tab1:
    st.markdown("### 🎯 O que você quer criar?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_prompt = st.text_area(
            "📝 Descrição:",
            placeholder="Ex: Crie um jogo de plataforma em Godot 4.6",
            height=150,
            key="user_input"
        )
    
    with col2:
        tipo_codigo = st.selectbox(
            "🔤 Tipo",
            [
                "Godot 4.6 (GDScript)",
                "Unity (C#)",
                "HTML5 - Canvas",
                "Python Script",
                "JavaScript",
                "Discord Bot",
                "SQL Database"
            ]
        )
        
        nivel = st.select_slider("📊 Nível", ["Básico", "Médio", "Avançado"])
    
    if st.button("⚡ GERAR CÓDIGO", use_container_width=True, type="primary"):
        if not user_prompt:
            st.error("❌ Descreva o que você quer!")
        else:
            with st.spinner("🔮 Gerando..."):
                try:
                    modelos = get_models()
                    if not modelos:
                        st.error("❌ API indisponível!")
                        st.stop()
                    
                    model = genai.GenerativeModel(modelos[0])
                    
                    prompt = f"""
Crie código {tipo_codigo} COMPLETO e FUNCIONAL.

Descrição: {user_prompt}
Nível: {nivel}

Regras:
1. Código COMPLETO pronto para usar
2. Comentários explicativos
3. Boas práticas
4. SEM markdown, APENAS código

Retorne o código diretamente:
"""
                    
                    response = model.generate_content(prompt)
                    codigo = response.text
                    
                    codigo = re.sub(r'```[\w]*\n?', '', codigo)
                    codigo = codigo.replace('```', '').strip()
                    
                    st.session_state.current_script = codigo
                    
                    st.success("✅ Código gerado!")
                    st.balloons()
                    
                    # Detectar linguagem
                    if "Godot" in tipo_codigo:
                        lang = "gdscript"
                    elif "Unity" in tipo_codigo or "C#" in tipo_codigo:
                        lang = "csharp"
                    elif "HTML" in tipo_codigo:
                        lang = "html"
                    elif "Python" in tipo_codigo:
                        lang = "python"
                    elif "SQL" in tipo_codigo:
                        lang = "sql"
                    else:
                        lang = "javascript"
                    
                    st.markdown("### 📄 Código:")
                    st.code(codigo, language=lang)
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.download_button(
                            "📥 Download",
                            data=codigo,
                            file_name=f"script.{lang}",
                            use_container_width=True
                        )
                    
                    with col_b:
                        if st.button("💾 Salvar", use_container_width=True):
                            st.session_state.saved_scripts.append({
                                "name": f"Script_{len(st.session_state.saved_scripts)+1}",
                                "code": codigo,
                                "language": lang,
                                "created_at": datetime.now().isoformat()
                            })
                            st.success("✅ Salvo!")
                            st.rerun()
                    
                    with col_c:
                        if st.button("✏️ Editar", use_container_width=True):
                            st.info("👉 Vá para 'Editor'")
                    
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")

# TAB 2: EDITOR
with tab2:
    if st.session_state.current_script:
        st.markdown("### 💻 Editor")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.text_input("📝 Nome", value="script", key="fname")
        
        with col2:
            ext = st.text_input("📄 Ext", value=".py", key="fext")
        
        with col3:
            st.download_button(
                "📥 Download",
                data=st.session_state.current_script,
                file_name=f"{nome}{ext}",
                use_container_width=True
            )
        
        codigo_edit = st.text_area(
            "Código:",
            value=st.session_state.current_script,
            height=500,
            key="editor"
        )
        
        st.session_state.current_script = codigo_edit
        
        st.markdown("### 👁️ Preview")
        st.code(codigo_edit, language="python")
    else:
        st.info("👈 Gere um código primeiro!")

# TAB 3: BIBLIOTECA
with tab3:
    if st.session_state.saved_scripts:
        st.markdown("### 📚 Scripts Salvos")
        for idx, s in enumerate(reversed(st.session_state.saved_scripts)):
            with st.expander(f"📄 {s['name']}"):
                st.code(s['code'], language=s.get('language', 'python'))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("📥", data=s['code'], file_name=s['name'], key=f"dl{idx}")
                with col2:
                    if st.button("📋", key=f"cp{idx}"):
                        st.session_state.current_script = s['code']
                        st.success("✅ Copiado!")
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"del{idx}"):
                        st.session_state.saved_scripts.pop(len(st.session_state.saved_scripts)-1-idx)
                        st.rerun()
    else:
        st.info("📭 Nenhum script salvo")

# Rodapé
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Scripts", len(st.session_state.saved_scripts))
with col2:
    st.metric("⚡ Status", "VIP" if is_vip_active() else "FREE")
with col3:
    if st.session_state.current_script:
        st.metric("📏 Linhas", len(st.session_state.current_script.split('\n')))
with col4:
    st.metric("🔐 Login", "Salvo ✅")
