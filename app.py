import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
import re

# Configuração
st.set_page_config(
    page_title="ScriptMaster AI 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CÓDIGO MASTER
MASTER_CODE = "GuizinhsDono"

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

# ====== SISTEMA DE LOGIN PERSISTENTE ======

def generate_token(username, is_master, vip_days=0):
    """Gera token de login"""
    data = f"{username}|{is_master}|{vip_days}|scriptmaster"
    return hashlib.md5(data.encode()).hexdigest()[:16]

def save_login(username, is_master, vip_until=None):
    """Salva login na URL (query params)"""
    vip_days = 0
    if vip_until:
        vip_days = (vip_until - datetime.now()).days
    
    token = generate_token(username, is_master, vip_days)
    
    st.query_params["user"] = username
    st.query_params["master"] = "1" if is_master else "0"
    st.query_params["vip"] = str(vip_days)
    st.query_params["token"] = token

def load_login():
    """Carrega login da URL"""
    try:
        params = st.query_params
        
        if "user" in params and "token" in params:
            username = params.get("user", "")
            is_master = params.get("master", "0") == "1"
            vip_days = int(params.get("vip", "0"))
            token = params.get("token", "")
            
            # Verificar token
            expected_token = generate_token(username, is_master, vip_days)
            
            if token == expected_token:
                st.session_state.username = username
                st.session_state.is_master = is_master
                
                if vip_days > 0:
                    st.session_state.vip_until = datetime.now() + timedelta(days=vip_days)
                elif is_master:
                    st.session_state.vip_until = None
                else:
                    st.session_state.vip_until = None
                
                st.session_state.authenticated = True
                return True
        
        return False
    except:
        return False

def clear_login():
    """Limpa login"""
    st.query_params.clear()
    for key in ['authenticated', 'is_master', 'vip_until', 'username']:
        if key in st.session_state:
            st.session_state[key] = None if key != 'authenticated' else False

# Inicializar session state
default_states = {
    "authenticated": False,
    "is_master": False,
    "vip_until": None,
    "username": None,
    "current_script": "",
    "saved_scripts": [],
    "created_codes": {},
    "login_checked": False
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ====== AUTO-LOGIN ======
if not st.session_state.authenticated and not st.session_state.login_checked:
    st.session_state.login_checked = True
    if load_login():
        st.toast(f"✅ Bem-vindo de volta, {st.session_state.username}!", icon="🎉")

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
        <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">🔐 Login automático - Salve o link para entrar automaticamente!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Fazer Login")
        
        username = st.text_input("👤 Seu nome", placeholder="Digite seu nome", key="login_username")
        access_code = st.text_input("🎫 Código de acesso", type="password", placeholder="GuizinhsDono ou código VIP", key="login_code")
        
        # Checkbox lembrar
        remember = st.checkbox("🔒 Manter conectado (salvar na URL)", value=True)
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 ENTRAR", use_container_width=True, type="primary"):
                if not username:
                    st.error("❌ Digite seu nome!")
                elif not access_code:
                    st.error("❌ Digite o código!")
                elif access_code == MASTER_CODE:
                    # MASTER
                    st.session_state.authenticated = True
                    st.session_state.is_master = True
                    st.session_state.username = username
                    st.session_state.vip_until = None
                    
                    if remember:
                        save_login(username, True, None)
                    
                    st.success(f"✅ MASTER {username} ativado!")
                    st.balloons()
                    st.rerun()
                    
                elif access_code in st.session_state.created_codes:
                    # VIP
                    code_info = st.session_state.created_codes[access_code]
                    
                    if not code_info.get("used"):
                        st.session_state.created_codes[access_code]["used"] = True
                        st.session_state.created_codes[access_code]["used_by"] = username
                        
                        days = code_info["days"]
                        vip_until = datetime.now() + timedelta(days=days if days != 999 else 3650)
                        
                        st.session_state.authenticated = True
                        st.session_state.is_master = False
                        st.session_state.username = username
                        st.session_state.vip_until = vip_until
                        
                        if remember:
                            save_login(username, False, vip_until)
                        
                        dias_txt = "ILIMITADO" if days == 999 else f"{days} dias"
                        st.success(f"✅ VIP ativado por {dias_txt}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Código já usado!")
                else:
                    st.error("❌ Código inválido!")
        
        with col_btn2:
            if st.button("🆓 Modo Grátis", use_container_width=True):
                nome = username if username else "Visitante"
                
                st.session_state.authenticated = True
                st.session_state.username = nome
                st.session_state.is_master = False
                st.session_state.vip_until = None
                
                if remember:
                    save_login(nome, False, None)
                
                st.info(f"ℹ️ Modo grátis para {nome}")
                st.rerun()
        
        st.divider()
        
        st.success("""
        💡 **Login Automático:**
        
        ✅ Marque "Manter conectado"
        
        ✅ Salve o link/favorito do navegador
        
        ✅ Ao abrir o link, entra automaticamente!
        """)
    
    with col2:
        st.markdown("### 🎯 Recursos")
        st.markdown("""
        **🎮 Criar Jogos:**
        - Godot 4.6 (GDScript)
        - Unity (C#)
        - HTML5 Canvas/Phaser
        - React Native
        
        **💻 Scripts:**
        - Python (Bot, API, Scraper)
        - JavaScript/Node.js
        - Discord/Telegram Bot
        - SQL, Bash
        
        **👑 VIP:**
        - Geração ilimitada
        - Todos os templates
        - Salvar scripts
        
        **🔥 MASTER:**
        - Tudo do VIP
        - Criar códigos VIP
        - Painel admin
        """)
        
        st.divider()
        
        st.markdown("### 🎁 Código MASTER:")
        st.code("GuizinhsDono", language=None)
    
    st.stop()

# ====== SIDEBAR (LOGADO) ======
with st.sidebar:
    st.markdown(f"""
    <div class="welcome-box">
        <h3 style="margin:0;">👋 {st.session_state.username}</h3>
        <p style="margin:0.5rem 0 0 0; font-size: 0.9rem;">
            ✅ Logado automaticamente
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.is_master:
        st.markdown('<div class="master-badge">🔥 MASTER</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 🎫 Criar Códigos")
        
        with st.expander("➕ Novo Código"):
            novo_codigo = st.text_input("📝 Nome", key="new_code", placeholder="VIP2024")
            tipo = st.selectbox("⏱️ Duração", ["1 dia", "7 dias", "30 dias", "Ilimitado"])
            
            if st.button("✨ Criar", use_container_width=True):
                if novo_codigo and novo_codigo not in st.session_state.created_codes:
                    days_map = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                    st.session_state.created_codes[novo_codigo] = {
                        "days": days_map[tipo],
                        "created_at": datetime.now().isoformat(),
                        "used": False
                    }
                    st.success("✅ Criado!")
                    st.code(novo_codigo)
        
        if st.session_state.created_codes:
            st.markdown("### 📋 Códigos")
            for code, info in list(st.session_state.created_codes.items())[:10]:
                status = "✅" if info.get("used") else "🎫"
                days = "♾️" if info["days"] == 999 else f"{info['days']}d"
                st.text(f"{status} {code} ({days})")
        
        st.divider()
    
    elif is_vip_active():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<div class="vip-badge">👑 VIP - {dias}d</div>', unsafe_allow_html=True)
        st.divider()
    else:
        st.info("🆓 Modo Grátis")
        st.divider()
    
    # SAIR
    if st.button("🚪 SAIR", use_container_width=True, type="secondary"):
        clear_login()
        st.session_state.authenticated = False
        st.session_state.login_checked = False
        st.success("✅ Saiu!")
        st.rerun()
    
    st.caption("💾 Salve o link para login automático!")
    
    st.divider()
    
    # Templates
    st.markdown("### 📚 Templates")
    
    templates_code = {
        "🎮 Godot Mobile": '''extends CharacterBody2D

const SPEED = 300.0
const JUMP = -400.0
var gravity = 980

func _physics_process(delta):
    if not is_on_floor():
        velocity.y += gravity * delta
    
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = JUMP
    
    var direction = Input.get_axis("left", "right")
    velocity.x = direction * SPEED
    
    move_and_slide()
''',
        "🌐 HTML5 Game": '''<!DOCTYPE html>
<html>
<head>
    <title>Meu Jogo</title>
    <style>
        canvas { border: 2px solid #333; display: block; margin: auto; }
        body { background: #1a1a1a; }
    </style>
</head>
<body>
<canvas id="game" width="800" height="600"></canvas>
<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

let player = { x: 400, y: 300, size: 40, color: "#00ff00" };

function draw() {
    ctx.fillStyle = "#2d2d2d";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = player.color;
    ctx.fillRect(player.x, player.y, player.size, player.size);
}

function update() {
    draw();
    requestAnimationFrame(update);
}

document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") player.x -= 10;
    if (e.key === "ArrowRight") player.x += 10;
    if (e.key === "ArrowUp") player.y -= 10;
    if (e.key === "ArrowDown") player.y += 10;
});

update();
</script>
</body>
</html>
''',
        "🐍 Web Scraper": '''import requests
from bs4 import BeautifulSoup

def scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extrair títulos
    titles = [h.text for h in soup.find_all("h1")]
    
    # Extrair links
    links = [a.get("href") for a in soup.find_all("a")]
    
    return {"titles": titles, "links": links}

if __name__ == "__main__":
    data = scrape("https://example.com")
    print(data)
''',
        "🤖 Discord Bot": '''import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Bot {bot.user} online!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

@bot.command()
async def ola(ctx):
    await ctx.send(f"Olá, {ctx.author.mention}!")

bot.run("SEU_TOKEN")
'''
    }
    
    for name, code in templates_code.items():
        if st.button(name, use_container_width=True, key=f"temp_{name}"):
            st.session_state.current_script = code
            st.rerun()
    
    st.divider()
    
    # Salvos
    if st.session_state.saved_scripts:
        st.markdown("### 💾 Salvos")
        for idx, s in enumerate(st.session_state.saved_scripts[-5:]):
            if st.button(f"📄 {s['name']}", key=f"saved_{idx}", use_container_width=True):
                st.session_state.current_script = s['code']
                st.rerun()
    
    st.caption(f"📊 {len(st.session_state.saved_scripts)} scripts")

# ====== ÁREA PRINCIPAL ======

st.markdown("""
<div class="header-premium">
    <h1>🎮 ScriptMaster AI</h1>
    <p style="color: white;">Gerador de Scripts e Jogos</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🤖 Gerar", "💻 Editor", "📚 Biblioteca"])

# TAB 1: GERAR
with tab1:
    st.markdown("### 🎯 O que você quer criar?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_area(
            "📝 Descrição:",
            placeholder="Ex: Crie um jogo de nave espacial em HTML5 com Canvas",
            height=150,
            key="prompt"
        )
    
    with col2:
        tipo = st.selectbox(
            "🔤 Tipo",
            [
                "Godot 4.6 (GDScript)",
                "Unity (C#)",
                "HTML5 Canvas",
                "Python",
                "JavaScript",
                "Discord Bot",
                "SQL"
            ]
        )
        
        nivel = st.select_slider("📊 Nível", ["Básico", "Médio", "Avançado"])
    
    if st.button("⚡ GERAR CÓDIGO", use_container_width=True, type="primary"):
        if not prompt:
            st.error("❌ Descreva o que quer!")
        else:
            with st.spinner("🔮 Gerando código..."):
                try:
                    modelos = get_models()
                    if not modelos:
                        st.error("❌ API indisponível!")
                        st.stop()
                    
                    model = genai.GenerativeModel(modelos[0])
                    
                    prompt_ia = f"""
Você é expert em {tipo}. Crie código COMPLETO e FUNCIONAL.

TAREFA: {prompt}
NÍVEL: {nivel}

REGRAS:
1. Código COMPLETO pronto para usar
2. Comentários explicativos
3. Boas práticas
4. APENAS código, sem markdown

IMPORTANTE: NÃO use ``` no início ou fim. Retorne código puro.
"""
                    
                    response = model.generate_content(prompt_ia)
                    codigo = response.text
                    
                    # Limpar markdown
                    codigo = re.sub(r'^```[\w]*\n?', '', codigo)
                    codigo = re.sub(r'\n?```$', '', codigo)
                    codigo = codigo.strip()
                    
                    st.session_state.current_script = codigo
                    
                    st.success("✅ Código gerado!")
                    st.balloons()
                    
                    # Detectar linguagem
                    if "Godot" in tipo:
                        lang = "gdscript"
                        ext = ".gd"
                    elif "Unity" in tipo or "C#" in tipo:
                        lang = "csharp"
                        ext = ".cs"
                    elif "HTML" in tipo:
                        lang = "html"
                        ext = ".html"
                    elif "Python" in tipo or "Discord" in tipo:
                        lang = "python"
                        ext = ".py"
                    elif "SQL" in tipo:
                        lang = "sql"
                        ext = ".sql"
                    else:
                        lang = "javascript"
                        ext = ".js"
                    
                    # Mostrar código
                    st.markdown("### 📄 Seu Código:")
                    st.code(codigo, language=lang)
                    
                    # Botões
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.download_button(
                            "📥 DOWNLOAD",
                            data=codigo,
                            file_name=f"script{ext}",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col_b:
                        if st.button("💾 SALVAR", use_container_width=True, key="save_gen"):
                            st.session_state.saved_scripts.append({
                                "name": f"Script_{len(st.session_state.saved_scripts)+1}{ext}",
                                "code": codigo,
                                "language": lang,
                                "created_at": datetime.now().isoformat()
                            })
                            st.success("✅ Salvo!")
                            st.rerun()
                    
                    with col_c:
                        if st.button("✏️ EDITAR", use_container_width=True, key="edit_gen"):
                            st.info("👉 Vá para aba 'Editor'")
                    
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
                    st.info("💡 Tente descrever de outra forma")

# TAB 2: EDITOR
with tab2:
    st.markdown("### 💻 Editor de Código")
    
    if st.session_state.current_script:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nome = st.text_input("📝 Nome", value="meu_script", key="filename")
        
        with col2:
            ext = st.text_input("📄 Ext", value=".py", key="ext")
        
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
            height=400,
            key="editor"
        )
        
        st.session_state.current_script = codigo_edit
        
        col_s, col_c = st.columns(2)
        
        with col_s:
            if st.button("💾 Salvar na Biblioteca", use_container_width=True):
                st.session_state.saved_scripts.append({
                    "name": f"{nome}{ext}",
                    "code": codigo_edit,
                    "language": "python",
                    "created_at": datetime.now().isoformat()
                })
                st.success("✅ Salvo!")
                st.rerun()
        
        with col_c:
            if st.button("🗑️ Limpar Editor", use_container_width=True):
                st.session_state.current_script = ""
                st.rerun()
        
        st.divider()
        st.markdown("### 👁️ Preview")
        st.code(codigo_edit, language="python")
        
    else:
        st.info("📝 Gere um código ou selecione um template para editar!")
        
        st.markdown("### 💡 Dicas:")
        st.markdown("""
        1. Vá para aba **Gerar** e descreva o que quer
        2. Ou clique em um **Template** na sidebar
        3. O código aparecerá aqui para editar!
        """)

# TAB 3: BIBLIOTECA
with tab3:
    st.markdown("### 📚 Scripts Salvos")
    
    if st.session_state.saved_scripts:
        for idx, script in enumerate(reversed(st.session_state.saved_scripts)):
            with st.expander(f"📄 {script['name']} - {datetime.fromisoformat(script['created_at']).strftime('%d/%m %H:%M')}"):
                st.code(script['code'], language=script.get('language', 'python'))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        "📥 Download",
                        data=script['code'],
                        file_name=script['name'],
                        key=f"dl_{idx}",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("📋 Abrir no Editor", key=f"cp_{idx}", use_container_width=True):
                        st.session_state.current_script = script['code']
                        st.success("✅ Aberto!")
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Deletar", key=f"del_{idx}", use_container_width=True):
                        real_idx = len(st.session_state.saved_scripts) - 1 - idx
                        st.session_state.saved_scripts.pop(real_idx)
                        st.success("✅ Deletado!")
                        st.rerun()
    else:
        st.info("📭 Nenhum script salvo ainda!")
        st.markdown("""
        **Como salvar scripts:**
        1. Gere um código na aba **Gerar**
        2. Clique em **Salvar**
        3. Ou edite no **Editor** e salve
        """)

# ====== RODAPÉ ======
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Scripts", len(st.session_state.saved_scripts))

with col2:
    status = "👑 VIP" if is_vip_active() else "🆓 FREE"
    st.metric("⚡ Status", status)

with col3:
    linhas = len(st.session_state.current_script.split('\n')) if st.session_state.current_script else 0
    st.metric("📏 Linhas", linhas)

with col4:
    st.metric("🔐 Login", "Salvo ✅" if "user" in st.query_params else "Não")
