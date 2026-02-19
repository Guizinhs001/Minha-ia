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

# CÓDIGO MASTER (SECRETO - NÃO MOSTRAR)
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
    
    .vip-info {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: white;
        padding: 1.5rem;
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
        <p style="color: white; font-size: 1.2rem;">Gerador Profissional de Scripts e Jogos com IA</p>
        <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">🔐 Login automático - Salve seus favoritos!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔐 Entrar no Sistema")
        
        username = st.text_input("👤 Seu nome", placeholder="Digite seu nome", key="login_username")
        access_code = st.text_input("🎫 Código de acesso VIP", type="password", placeholder="Cole seu código VIP aqui", key="login_code")
        
        # Checkbox lembrar
        remember = st.checkbox("🔒 Manter conectado (recomendado)", value=True)
        
        st.caption("💡 Marque para entrar automaticamente na próxima vez")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 ENTRAR COM CÓDIGO VIP", use_container_width=True, type="primary"):
                if not username:
                    st.error("❌ Digite seu nome!")
                elif not access_code:
                    st.error("❌ Digite o código de acesso!")
                elif access_code == MASTER_CODE:
                    # MASTER (SECRETO)
                    st.session_state.authenticated = True
                    st.session_state.is_master = True
                    st.session_state.username = username
                    st.session_state.vip_until = None
                    
                    if remember:
                        save_login(username, True, None)
                    
                    st.success(f"✅ Bem-vindo, {username}! Acesso MASTER concedido!")
                    st.balloons()
                    st.rerun()
                    
                elif access_code in st.session_state.created_codes:
                    # VIP
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
                        
                        if remember:
                            save_login(username, False, vip_until)
                        
                        dias_txt = "ILIMITADO ♾️" if days == 999 else f"{days} dias"
                        st.success(f"✅ VIP ativado por {dias_txt}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Este código já foi usado anteriormente!")
                        st.info("💡 Solicite um novo código VIP")
                else:
                    st.error("❌ Código inválido ou expirado!")
                    st.warning("💡 Verifique se digitou corretamente ou solicite um novo código")
        
        with col_btn2:
            if st.button("🆓 Modo Grátis", use_container_width=True):
                nome = username if username else "Visitante"
                
                st.session_state.authenticated = True
                st.session_state.username = nome
                st.session_state.is_master = False
                st.session_state.vip_until = None
                
                if remember:
                    save_login(nome, False, None)
                
                st.info(f"ℹ️ Modo gratuito ativado para {nome}")
                st.rerun()
        
        st.divider()
        
        st.success("""
        ✅ **Login Automático Ativado:**
        
        🔒 Marque "Manter conectado"
        
        📌 Salve esta página nos favoritos
        
        🚀 Na próxima vez, entre automaticamente!
        
        💾 Seus dados ficam salvos de forma segura
        """)
    
    with col2:
        st.markdown("### 🎯 Recursos Disponíveis")
        
        # Modo Gratuito
        st.markdown("""
        **🆓 MODO GRATUITO:**
        - ✅ Geração básica de código
        - ✅ Templates simples
        - ✅ Editar e baixar scripts
        - ⚠️ Limite de uso diário
        """)
        
        st.divider()
        
        # Modo VIP
        st.markdown("""
        <div class="vip-info">
            <h3 style="margin:0; color: white;">👑 MODO VIP</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem;">
                ✅ Geração ILIMITADA de código<br>
                ✅ TODOS os templates premium<br>
                ✅ Salvar scripts permanentemente<br>
                ✅ Suporte prioritário<br>
                ✅ Sem anúncios<br>
                ✅ Novos recursos exclusivos
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Tipos de código
        st.markdown("### 💻 O que você pode criar:")
        st.markdown("""
        **🎮 Jogos:**
        - Godot 4.6 (GDScript/C#)
        - Unity (C#)
        - HTML5 (Phaser, Canvas)
        - React Native Mobile
        
        **🤖 Bots:**
        - Discord Bot
        - Telegram Bot
        - WhatsApp Bot
        
        **💾 Scripts:**
        - Python (Web Scraper, API, Automação)
        - JavaScript/Node.js
        - SQL Database
        - Bash/PowerShell
        """)
        
        st.divider()
        
        # Como conseguir VIP
        st.info("""
        **🎁 Como conseguir acesso VIP?**
        
        📧 Entre em contato para solicitar seu código VIP
        
        🎫 Códigos podem ter diferentes durações:
        - 1 dia (teste)
        - 7 dias
        - 30 dias
        - Ilimitado ♾️
        """)
    
    st.stop()

# ====== SIDEBAR (LOGADO) ======
with st.sidebar:
    st.markdown(f"""
    <div class="welcome-box">
        <h3 style="margin:0;">👋 Olá, {st.session_state.username}!</h3>
        <p style="margin:0.5rem 0 0 0; font-size: 0.9rem;">
            ✅ Login salvo automaticamente
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.is_master:
        st.markdown('<div class="master-badge">🔥 ADMINISTRADOR</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 🎫 Painel de Códigos VIP")
        
        with st.expander("➕ Criar Novo Código VIP", expanded=False):
            novo_codigo = st.text_input("📝 Nome do código", key="new_code", placeholder="Ex: VIP2024")
            tipo = st.selectbox("⏱️ Duração do acesso", ["1 dia", "7 dias", "30 dias", "Ilimitado"])
            
            if st.button("✨ Gerar Código", use_container_width=True):
                if novo_codigo and novo_codigo not in st.session_state.created_codes:
                    days_map = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                    st.session_state.created_codes[novo_codigo] = {
                        "days": days_map[tipo],
                        "created_at": datetime.now().isoformat(),
                        "used": False
                    }
                    st.success("✅ Código VIP criado com sucesso!")
                    st.code(novo_codigo, language=None)
                    st.info("💡 Compartilhe este código com o usuário")
                elif novo_codigo in st.session_state.created_codes:
                    st.error("❌ Este código já existe!")
                else:
                    st.error("❌ Digite um nome para o código!")
        
        if st.session_state.created_codes:
            st.markdown("### 📋 Códigos Criados")
            
            total_codes = len(st.session_state.created_codes)
            used_codes = sum(1 for c in st.session_state.created_codes.values() if c.get("used"))
            
            st.metric("Total de Códigos", total_codes)
            st.metric("Códigos Usados", used_codes)
            st.metric("Disponíveis", total_codes - used_codes)
            
            st.divider()
            
            for code, info in list(st.session_state.created_codes.items())[:15]:
                status = "✅ USADO" if info.get("used") else "🎫 ATIVO"
                days_icon = "♾️" if info["days"] == 999 else f"{info['days']}d"
                user_info = f" por {info.get('used_by', 'N/A')}" if info.get("used") else ""
                
                with st.expander(f"{status[:2]} {code} ({days_icon})"):
                    st.markdown(f"**Status:** {status}")
                    st.markdown(f"**Duração:** {days_icon}")
                    st.markdown(f"**Criado em:** {datetime.fromisoformat(info['created_at']).strftime('%d/%m/%Y %H:%M')}")
                    
                    if info.get("used"):
                        st.markdown(f"**Usado por:** {info.get('used_by', 'Desconhecido')}")
                        st.markdown(f"**Usado em:** {datetime.fromisoformat(info['used_at']).strftime('%d/%m/%Y %H:%M')}")
                    else:
                        st.code(code, language=None)
                        if st.button("🗑️ Deletar Código", key=f"del_code_{code}"):
                            del st.session_state.created_codes[code]
                            st.success("✅ Código deletado!")
                            st.rerun()
        
        st.divider()
    
    elif is_vip_active():
        dias_restantes = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<div class="vip-badge">👑 VIP ATIVO - {dias_restantes} dias</div>', unsafe_allow_html=True)
        st.divider()
    else:
        st.info("🆓 Modo Gratuito Ativo")
        st.caption("Faça upgrade para VIP e tenha acesso ilimitado!")
        st.divider()
    
    # BOTÃO SAIR
    if st.button("🚪 SAIR DA CONTA", use_container_width=True, type="secondary"):
        clear_login()
        st.session_state.authenticated = False
        st.session_state.login_checked = False
        st.success("✅ Você saiu com sucesso!")
        st.info("🔄 Redirecionando para login...")
        st.rerun()
    
    st.caption("💾 Seus dados estão salvos de forma segura")
    
    st.divider()
    
    # Templates
    st.markdown("### 📚 Templates Prontos")
    
    templates_code = {
        "🎮 Godot - Player Mobile": '''extends CharacterBody2D

const SPEED = 300.0
const JUMP = -400.0
var gravity = 980

func _physics_process(delta):
    # Gravidade
    if not is_on_floor():
        velocity.y += gravity * delta
    
    # Pulo (toque na tela)
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = JUMP
    
    # Movimento horizontal
    var direction = Input.get_axis("left", "right")
    velocity.x = direction * SPEED
    
    move_and_slide()
''',
        "🌐 HTML5 - Jogo Canvas": '''<!DOCTYPE html>
<html>
<head>
    <title>Meu Jogo</title>
    <style>
        canvas { 
            border: 3px solid #333; 
            display: block; 
            margin: 20px auto; 
            background: #1a1a1a;
        }
        body { 
            background: #0a0a0a; 
            font-family: Arial;
        }
    </style>
</head>
<body>
<canvas id="game" width="800" height="600"></canvas>
<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

let player = { 
    x: 50, 
    y: 300, 
    width: 40, 
    height: 40, 
    color: "#00ff00",
    velocityY: 0,
    jumping: false
};

const gravity = 0.8;
const jumpPower = -15;

function draw() {
    // Limpar tela
    ctx.fillStyle = "#1a1a1a";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Chão
    ctx.fillStyle = "#654321";
    ctx.fillRect(0, 550, canvas.width, 50);
    
    // Player
    ctx.fillStyle = player.color;
    ctx.fillRect(player.x, player.y, player.width, player.height);
}

function update() {
    // Física
    player.velocityY += gravity;
    player.y += player.velocityY;
    
    // Colisão com chão
    if (player.y + player.height > 550) {
        player.y = 550 - player.height;
        player.velocityY = 0;
        player.jumping = false;
    }
    
    draw();
    requestAnimationFrame(update);
}

// Controles
document.addEventListener("keydown", (e) => {
    if (e.key === " " && !player.jumping) {
        player.velocityY = jumpPower;
        player.jumping = true;
    }
});

canvas.addEventListener("click", () => {
    if (!player.jumping) {
        player.velocityY = jumpPower;
        player.jumping = true;
    }
});

update();
</script>
</body>
</html>
''',
        "🐍 Python - Web Scraper": '''import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def scrape_website(url):
    """Extrai dados de um website"""
    try:
        # Fazer requisição
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrair dados (exemplo: títulos e links)
        data = []
        
        for item in soup.find_all(['h1', 'h2', 'h3']):
            title = item.get_text(strip=True)
            if title:
                data.append({
                    'tipo': item.name,
                    'texto': title,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Salvar em CSV
        if data:
            filename = f'scraped_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['tipo', 'texto', 'timestamp'])
                writer.writeheader()
                writer.writerows(data)
            
            print(f"✅ {len(data)} itens salvos em {filename}")
            return data
        else:
            print("⚠️ Nenhum dado encontrado")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

if __name__ == "__main__":
    url = "https://example.com"
    resultados = scrape_website(url)
    print(f"Total de itens: {len(resultados)}")
''',
        "🤖 Discord Bot Completo": '''import discord
from discord.ext import commands
import asyncio

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} está online!")
    await bot.change_presence(activity=discord.Game(name="!help para comandos"))

@bot.event
async def on_member_join(member):
    """Mensagem de boas-vindas"""
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"👋 Bem-vindo(a) {member.mention}!")

@bot.command()
async def ping(ctx):
    """Verifica latência do bot"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latência: {latency}ms")

@bot.command()
async def ola(ctx):
    """Saudação"""
    await ctx.send(f"👋 Olá, {ctx.author.mention}!")

@bot.command()
async def servidor(ctx):
    """Informações do servidor"""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"📊 Informações de {guild.name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="👥 Membros", value=guild.member_count)
    embed.add_field(name="📅 Criado em", value=guild.created_at.strftime("%d/%m/%Y"))
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    """Mostra avatar de um usuário"""
    member = member or ctx.author
    embed = discord.Embed(title=f"Avatar de {member.name}", color=discord.Color.green())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def limpar(ctx, quantidade: int):
    """Limpa mensagens (admin)"""
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=quantidade + 1)
        await ctx.send(f"✅ {quantidade} mensagens deletadas!", delete_after=3)
    else:
        await ctx.send("❌ Você não tem permissão!")

# Rodar bot
bot.run("SEU_TOKEN_AQUI")
'''
    }
    
    for name, code in templates_code.items():
        if st.button(name, use_container_width=True, key=f"temp_{name}"):
            st.session_state.current_script = code
            st.rerun()
    
    st.divider()
    
    # Scripts salvos
    if st.session_state.saved_scripts:
        st.markdown("### 💾 Meus Scripts")
        for idx, s in enumerate(st.session_state.saved_scripts[-5:]):
            if st.button(f"📄 {s['name']}", key=f"saved_{idx}", use_container_width=True):
                st.session_state.current_script = s['code']
                st.rerun()
        
        if len(st.session_state.saved_scripts) > 5:
            st.caption(f"+ {len(st.session_state.saved_scripts) - 5} mais na biblioteca")
    
    st.divider()
    st.caption(f"📊 Total de scripts: {len(st.session_state.saved_scripts)}")

# ====== ÁREA PRINCIPAL ======

st.markdown("""
<div class="header-premium">
    <h1>🎮 ScriptMaster AI</h1>
    <p style="color: white;">Gerador Profissional de Scripts e Jogos com Inteligência Artificial</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🤖 Gerar Código", "💻 Editor", "📚 Biblioteca"])

# TAB 1: GERAR
with tab1:
    st.markdown("### 🎯 Descreva o que você quer criar")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_area(
            "📝 Descrição detalhada:",
            placeholder="Ex: Crie um jogo de plataforma 2D em Godot 4.6 para mobile com controles touch, sistema de score, moedas colecionáveis e 3 níveis de dificuldade",
            height=150,
            key="prompt"
        )
    
    with col2:
        tipo = st.selectbox(
            "🔤 Tipo de código",
            [
                "Godot 4.6 (GDScript)",
                "Godot 4.6 (C#)",
                "Unity (C#)",
                "HTML5 - Canvas Puro",
                "HTML5 - Phaser 3",
                "React Native Mobile",
                "Python Script",
                "JavaScript/Node.js",
                "Discord Bot",
                "Telegram Bot",
                "SQL Database",
                "Bash Script",
                "PowerShell"
            ]
        )
        
        nivel = st.select_slider("📊 Complexidade", ["Básico", "Intermediário", "Avançado", "Expert"])
    
    if st.button("⚡ GERAR CÓDIGO COMPLETO", use_container_width=True, type="primary"):
        if not prompt:
            st.error("❌ Por favor, descreva o que você quer criar!")
        else:
            with st.spinner("🔮 Gerando código profissional... Isso pode levar alguns segundos..."):
                try:
                    modelos = get_models()
                    if not modelos:
                        st.error("❌ API temporariamente indisponível. Tente novamente em alguns instantes.")
                        st.stop()
                    
                    model = genai.GenerativeModel(modelos[0])
                    
                    prompt_ia = f"""
Você é um programador EXPERT em {tipo}. Crie código COMPLETO, FUNCIONAL e PROFISSIONAL.

TAREFA: {prompt}

NÍVEL DE COMPLEXIDADE: {nivel}

REGRAS OBRIGATÓRIAS:
1. Código 100% COMPLETO e pronto para usar
2. Comentários explicativos em português
3. Seguir as melhores práticas da linguagem
4. Incluir tratamento de erros
5. Se for jogo: controles funcionais, física básica, sistema de pontuação
6. Se for mobile: otimizar para touch e performance
7. Código limpo e bem estruturado

IMPORTANTE: Retorne APENAS o código puro, SEM markdown, SEM ```, SEM explicações extras.
Comece diretamente com o código.
"""
                    
                    response = model.generate_content(prompt_ia)
                    codigo = response.text
                    
                    # Limpar markdown
                    codigo = re.sub(r'^```[\w]*\n?', '', codigo)
                    codigo = re.sub(r'\n?```$', '', codigo)
                    codigo = codigo.strip()
                    
                    st.session_state.current_script = codigo
                    
                    st.success("✅ Código gerado com sucesso!")
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
                    elif "Python" in tipo or "Discord" in tipo or "Telegram" in tipo:
                        lang = "python"
                        ext = ".py"
                    elif "SQL" in tipo:
                        lang = "sql"
                        ext = ".sql"
                    elif "Bash" in tipo:
                        lang = "bash"
                        ext = ".sh"
                    elif "PowerShell" in tipo:
                        lang = "powershell"
                        ext = ".ps1"
                    else:
                        lang = "javascript"
                        ext = ".js"
                    
                    # Mostrar código
                    st.markdown("### 📄 Seu Código Está Pronto:")
                    st.code(codigo, language=lang)
                    
                    # Informações
                    linhas = len(codigo.split('\n'))
                    caracteres = len(codigo)
                    
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.metric("📏 Linhas", linhas)
                    with col_info2:
                        st.metric("🔤 Caracteres", caracteres)
                    with col_info3:
                        st.metric("💾 Tipo", lang.upper())
                    
                    st.divider()
                    
                    # Botões de ação
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.download_button(
                            "📥 BAIXAR CÓDIGO",
                            data=codigo,
                            file_name=f"script{ext}",
                            mime="text/plain",
                            use_container_width=True,
                            type="primary"
                        )
                    
                    with col_b:
                        if st.button("💾 SALVAR NA BIBLIOTECA", use_container_width=True, key="save_gen"):
                            st.session_state.saved_scripts.append({
                                "name": f"Script_{len(st.session_state.saved_scripts)+1}{ext}",
                                "code": codigo,
                                "language": lang,
                                "created_at": datetime.now().isoformat()
                            })
                            st.success("✅ Script salvo na biblioteca!")
                            st.rerun()
                    
                    with col_c:
                        if st.button("✏️ EDITAR CÓDIGO", use_container_width=True, key="edit_gen"):
                            st.info("👉 Vá para a aba 'Editor' para editar!")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar código: {str(e)}")
                    st.info("💡 Dicas: Tente descrever de forma mais simples ou escolha outro tipo de código")

# TAB 2: EDITOR
with tab2:
    st.markdown("### 💻 Editor de Código Profissional")
    
    if st.session_state.current_script:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nome = st.text_input("📝 Nome do arquivo", value="meu_script", key="filename")
        
        with col2:
            ext = st.text_input("📄 Extensão", value=".py", key="ext")
        
        with col3:
            st.download_button(
                "📥 Download",
                data=st.session_state.current_script,
                file_name=f"{nome}{ext}",
                use_container_width=True
            )
        
        codigo_edit = st.text_area(
            "✏️ Edite seu código:",
            value=st.session_state.current_script,
            height=400,
            key="editor"
        )
        
        st.session_state.current_script = codigo_edit
        
        col_s, col_c, col_l = st.columns(3)
        
        with col_s:
            if st.button("💾 Salvar Alterações", use_container_width=True):
                st.session_state.saved_scripts.append({
                    "name": f"{nome}{ext}",
                    "code": codigo_edit,
                    "language": "python",
                    "created_at": datetime.now().isoformat()
                })
                st.success("✅ Script salvo com sucesso!")
                st.rerun()
        
        with col_c:
            if st.button("📋 Copiar Código", use_container_width=True):
                st.code(codigo_edit)
                st.info("📋 Código pronto para copiar!")
        
        with col_l:
            if st.button("🗑️ Limpar Editor", use_container_width=True):
                st.session_state.current_script = ""
                st.rerun()
        
        st.divider()
        
        # Estatísticas
        linhas_edit = len(codigo_edit.split('\n'))
        palavras = len(codigo_edit.split())
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("📏 Linhas", linhas_edit)
        with col_stat2:
            st.metric("📝 Palavras", palavras)
        with col_stat3:
            st.metric("💾 Caracteres", len(codigo_edit))
        
        st.divider()
        st.markdown("### 👁️ Preview do Código")
        st.code(codigo_edit, language="python")
        
    else:
        st.info("📝 Nenhum código carregado no editor!")
        
        st.markdown("### 💡 Como começar:")
        st.markdown("""
        **Opção 1:** Vá para a aba **Gerar Código** e crie um novo script
        
        **Opção 2:** Clique em um **Template** na barra lateral
        
        **Opção 3:** Abra um script da **Biblioteca**
        
        O código aparecerá aqui automaticamente para você editar!
        """)

# TAB 3: BIBLIOTECA
with tab3:
    st.markdown("### 📚 Biblioteca de Scripts Salvos")
    
    if st.session_state.saved_scripts:
        # Filtros e ordenação
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            search = st.text_input("🔍 Buscar script", placeholder="Digite para filtrar...")
        
        with col_filter2:
            ordem = st.selectbox("📊 Ordenar por", ["Mais recentes", "Mais antigos", "Nome A-Z"])
        
        st.divider()
        
        # Aplicar filtros
        scripts_filtered = st.session_state.saved_scripts.copy()
        
        if search:
            scripts_filtered = [s for s in scripts_filtered if search.lower() in s['name'].lower()]
        
        if ordem == "Mais antigos":
            scripts_filtered = scripts_filtered
        elif ordem == "Mais recentes":
            scripts_filtered = list(reversed(scripts_filtered))
        elif ordem == "Nome A-Z":
            scripts_filtered = sorted(scripts_filtered, key=lambda x: x['name'])
        
        # Mostrar scripts
        for idx, script in enumerate(scripts_filtered):
            data_criacao = datetime.fromisoformat(script['created_at']).strftime('%d/%m/%Y às %H:%M')
            
            with st.expander(f"📄 {script['name']} - Criado em {data_criacao}"):
                st.code(script['code'], language=script.get('language', 'python'))
                
                # Estatísticas do script
                linhas_script = len(script['code'].split('\n'))
                tamanho_kb = len(script['code']) / 1024
                
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.caption(f"📏 {linhas_script} linhas")
                with col_stat2:
                    st.caption(f"💾 {tamanho_kb:.2f} KB")
                
                st.divider()
                
                # Ações
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.download_button(
                        "📥 Download",
                        data=script['code'],
                        file_name=script['name'],
                        key=f"dl_{idx}",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("📋 Copiar", key=f"cp_{idx}", use_container_width=True):
                        st.session_state.current_script = script['code']
                        st.success("✅ Código copiado para o editor!")
                        st.rerun()
                
                with col3:
                    if st.button("✏️ Editar", key=f"ed_{idx}", use_container_width=True):
                        st.session_state.current_script = script['code']
                        st.info("👉 Vá para a aba 'Editor'")
                
                with col4:
                    if st.button("🗑️ Deletar", key=f"del_{idx}", use_container_width=True):
                        real_idx = st.session_state.saved_scripts.index(script)
                        st.session_state.saved_scripts.pop(real_idx)
                        st.success("✅ Script deletado!")
                        st.rerun()
        
        if not scripts_filtered and search:
            st.warning(f"🔍 Nenhum script encontrado com '{search}'")
        
    else:
        st.info("📭 Sua biblioteca está vazia!")
        st.markdown("""
        ### 💡 Como adicionar scripts à biblioteca:
        
        **1.** Vá para a aba **Gerar Código**
        
        **2.** Crie um novo script com a IA
        
        **3.** Clique em **Salvar na Biblioteca**
        
        **4.** Ou edite um código no **Editor** e salve
        
        Todos os seus scripts salvos aparecerão aqui! 📚
        """)

# ====== RODAPÉ ======
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Scripts Salvos", len(st.session_state.saved_scripts))

with col2:
    if st.session_state.is_master:
        status_text = "🔥 ADMIN"
    elif is_vip_active():
        status_text = "👑 VIP"
    else:
        status_text = "🆓 FREE"
    st.metric("⚡ Plano", status_text)

with col3:
    linhas_atual = len(st.session_state.current_script.split('\n')) if st.session_state.current_script else 0
    st.metric("📏 Linhas no Editor", linhas_atual)

with col4:
    login_status = "Salvo ✅" if "user" in st.query_params else "Temporário"
    st.metric("🔐 Login", login_status)

st.caption("💡 Desenvolvido com ❤️ usando Streamlit e Google Gemini AI")
