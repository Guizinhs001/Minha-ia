import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
import re
import base64
import zlib
import random
import string

# ====== CONFIGURAÇÃO ======
st.set_page_config(
    page_title="ScriptMaster AI Pro 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CONSTANTES ======
DAILY_LIMIT_FREE = 4
DAILY_LIMIT_CHAT_FREE = 10

# ====== CSS ======
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    }
    
    .header-premium {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    }
    
    .header-premium h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
    }
    
    .header-premium p {
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
    }
    
    .master-badge {
        background: linear-gradient(135deg, #dc2626, #991b1b);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #f59e0b, #d97706);
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
    
    .chat-user {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
    }
    
    .chat-assistant {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .usage-box {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .welcome-box {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ====== FUNÇÕES DE PERSISTÊNCIA ======
def generate_unique_id():
    """Gera ID único"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def compress_data(data):
    """Comprime dados para URL"""
    try:
        json_str = json.dumps(data, separators=(',', ':'), default=str)
        compressed = zlib.compress(json_str.encode(), 9)
        return base64.urlsafe_b64encode(compressed).decode()
    except:
        return ""

def decompress_data(encoded):
    """Descomprime dados da URL"""
    try:
        compressed = base64.urlsafe_b64decode(encoded.encode())
        json_str = zlib.decompress(compressed).decode()
        return json.loads(json_str)
    except:
        return None

def generate_token(username, is_master):
    """Gera token de verificação"""
    data = f"{username}|{is_master}|scriptmaster_v3"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def save_session():
    """Salva sessão na URL"""
    try:
        data = {
            "u": st.session_state.get("username", ""),
            "m": 1 if st.session_state.get("is_master", False) else 0,
            "v": 0,
            "uc": st.session_state.get("usage_count", 0),
            "cc": st.session_state.get("chat_count", 0),
            "lr": st.session_state.get("last_reset", ""),
            "ss": st.session_state.get("saved_scripts", [])[-10:],
            "fv": st.session_state.get("favorites", [])[-5:],
            "ch": st.session_state.get("chat_history", [])[-20:],
        }
        
        if st.session_state.get("vip_until"):
            delta = st.session_state.vip_until - datetime.now()
            data["v"] = max(0, delta.days)
        
        encoded = compress_data(data)
        token = generate_token(data["u"], data["m"])
        
        if len(encoded) < 2000:
            st.query_params["d"] = encoded
            st.query_params["t"] = token
    except:
        pass

def load_session():
    """Carrega sessão da URL"""
    try:
        params = st.query_params
        
        if "d" in params and "t" in params:
            data = decompress_data(params.get("d", ""))
            token = params.get("t", "")
            
            if data and token == generate_token(data.get("u", ""), data.get("m", 0)):
                st.session_state.username = data.get("u", "")
                st.session_state.is_master = data.get("m", 0) == 1
                st.session_state.usage_count = data.get("uc", 0)
                st.session_state.chat_count = data.get("cc", 0)
                st.session_state.last_reset = data.get("lr", "")
                st.session_state.saved_scripts = data.get("ss", [])
                st.session_state.favorites = data.get("fv", [])
                st.session_state.chat_history = data.get("ch", [])
                
                vip_days = data.get("v", 0)
                if vip_days > 0:
                    st.session_state.vip_until = datetime.now() + timedelta(days=vip_days)
                else:
                    st.session_state.vip_until = None
                
                st.session_state.authenticated = True
                check_daily_reset()
                return True
        return False
    except:
        return False

def check_daily_reset():
    """Reseta limites diários"""
    today = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.get("last_reset") != today:
        st.session_state.usage_count = 0
        st.session_state.chat_count = 0
        st.session_state.last_reset = today

def clear_session():
    """Limpa sessão"""
    st.query_params.clear()
    keys_to_clear = list(st.session_state.keys())
    for key in keys_to_clear:
        del st.session_state[key]

# ====== INICIALIZAÇÃO ======
defaults = {
    "authenticated": False,
    "is_master": False,
    "vip_until": None,
    "username": "",
    "current_script": "",
    "saved_scripts": [],
    "favorites": [],
    "chat_history": [],
    "created_codes": {},
    "usage_count": 0,
    "chat_count": 0,
    "last_reset": "",
    "login_checked": False,
    "gen_counter": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Auto-login
if not st.session_state.authenticated and not st.session_state.login_checked:
    st.session_state.login_checked = True
    if load_session():
        st.toast(f"✅ Bem-vindo de volta, {st.session_state.username}!")

# ====== SECRETS ======
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    MASTER_CODE = st.secrets.get("MASTER_CODE", "GuizinhsDono")
except:
    st.error("❌ Configure a chave API em Settings > Secrets")
    st.code('GEMINI_API_KEY = "sua_chave_aqui"\nMASTER_CODE = "seu_codigo_master"')
    st.stop()

# Configurar API
genai.configure(api_key=GEMINI_API_KEY)

# ====== FUNÇÕES AUXILIARES ======
def is_vip():
    if st.session_state.is_master:
        return True
    if st.session_state.vip_until:
        return datetime.now() < st.session_state.vip_until
    return False

def can_generate():
    if is_vip():
        return True, 999
    remaining = DAILY_LIMIT_FREE - st.session_state.usage_count
    return remaining > 0, remaining

def can_chat():
    if is_vip():
        return True, 999
    remaining = DAILY_LIMIT_CHAT_FREE - st.session_state.chat_count
    return remaining > 0, remaining

def use_generation():
    st.session_state.usage_count += 1
    st.session_state.gen_counter += 1
    save_session()

def use_chat():
    st.session_state.chat_count += 1
    save_session()

@st.cache_resource
def get_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return genai.GenerativeModel(models[0]) if models else None
    except:
        return None

def detect_language(code):
    code_lower = code.lower()
    if 'extends' in code_lower and 'func' in code_lower:
        return 'gdscript', '.gd'
    elif 'using unityengine' in code_lower:
        return 'csharp', '.cs'
    elif '<!doctype' in code_lower or '<html' in code_lower:
        return 'html', '.html'
    elif 'gg.' in code_lower and 'function' in code_lower:
        return 'lua', '.lua'
    elif 'def ' in code_lower or 'import ' in code_lower:
        return 'python', '.py'
    elif 'function' in code_lower or 'const ' in code_lower:
        return 'javascript', '.js'
    return 'text', '.txt'

# ====== TEMPLATES ======
TEMPLATES = {
    "🎮 Android HTML5": {
        "Jogo Touch Simples": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <title>Touch Game</title>
    <style>
        * { margin: 0; padding: 0; touch-action: manipulation; user-select: none; }
        body { background: #1a1a2e; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="game"></canvas>
    <script>
        const canvas = document.getElementById('game');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        let score = 0;
        const player = { x: canvas.width/2 - 25, y: canvas.height - 70, w: 50, h: 50 };
        const target = { x: Math.random() * (canvas.width-30), y: 0, size: 30, speed: 3 };
        
        function draw() {
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(player.x, player.y, player.w, player.h);
            
            ctx.fillStyle = '#ffd700';
            ctx.fillRect(target.x, target.y, target.size, target.size);
            
            ctx.fillStyle = '#fff';
            ctx.font = '24px Arial';
            ctx.fillText('Score: ' + score, 10, 30);
        }
        
        function update() {
            target.y += target.speed;
            
            if (target.y + target.size > player.y && 
                target.x < player.x + player.w && 
                target.x + target.size > player.x) {
                score++;
                target.y = 0;
                target.x = Math.random() * (canvas.width - 30);
                target.speed += 0.1;
            }
            
            if (target.y > canvas.height) {
                alert('Game Over! Score: ' + score);
                score = 0;
                target.speed = 3;
                target.y = 0;
            }
        }
        
        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            player.x = e.touches[0].clientX - player.w/2;
        });
        
        canvas.addEventListener('mousemove', (e) => {
            player.x = e.clientX - player.w/2;
        });
        
        function loop() { update(); draw(); requestAnimationFrame(loop); }
        loop();
    </script>
</body>
</html>""",
        
        "Endless Runner": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Runner</title>
    <style>
        * { margin: 0; padding: 0; touch-action: manipulation; }
        body { background: #000; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="c"></canvas>
    <script>
        const c = document.getElementById('c'), ctx = c.getContext('2d');
        c.width = innerWidth; c.height = innerHeight;
        
        let score = 0, speed = 5, playing = true;
        const ground = c.height - 100;
        const player = { x: 80, y: ground - 50, w: 50, h: 50, vy: 0, jump: false };
        let obstacles = [];
        
        function addObs() {
            obstacles.push({ x: c.width, y: ground - 40, w: 30, h: 40 });
        }
        
        let timer = 0;
        function update() {
            if (!playing) return;
            
            player.vy += 0.8;
            player.y += player.vy;
            if (player.y > ground - player.h) {
                player.y = ground - player.h;
                player.vy = 0;
                player.jump = false;
            }
            
            timer++;
            if (timer > 60) { addObs(); timer = 0; }
            
            for (let i = obstacles.length - 1; i >= 0; i--) {
                obstacles[i].x -= speed;
                if (obstacles[i].x + obstacles[i].w < 0) {
                    obstacles.splice(i, 1);
                    score++;
                    continue;
                }
                if (player.x < obstacles[i].x + obstacles[i].w &&
                    player.x + player.w > obstacles[i].x &&
                    player.y + player.h > obstacles[i].y) {
                    playing = false;
                }
            }
        }
        
        function draw() {
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, c.width, c.height);
            
            ctx.fillStyle = '#333';
            ctx.fillRect(0, ground, c.width, 100);
            
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(player.x, player.y, player.w, player.h);
            
            ctx.fillStyle = '#e74c3c';
            obstacles.forEach(o => ctx.fillRect(o.x, o.y, o.w, o.h));
            
            ctx.fillStyle = '#fff';
            ctx.font = '24px Arial';
            ctx.fillText('Score: ' + score, 10, 30);
            
            if (!playing) {
                ctx.fillStyle = 'rgba(0,0,0,0.8)';
                ctx.fillRect(0, 0, c.width, c.height);
                ctx.fillStyle = '#fff';
                ctx.font = '48px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', c.width/2, c.height/2);
                ctx.font = '24px Arial';
                ctx.fillText('Score: ' + score + ' | Tap to restart', c.width/2, c.height/2 + 50);
            }
        }
        
        function jump() {
            if (!playing) {
                playing = true;
                score = 0;
                obstacles = [];
                player.y = ground - player.h;
                return;
            }
            if (!player.jump) {
                player.vy = -15;
                player.jump = true;
            }
        }
        
        c.addEventListener('touchstart', (e) => { e.preventDefault(); jump(); });
        c.addEventListener('click', jump);
        
        function loop() { update(); draw(); requestAnimationFrame(loop); }
        loop();
    </script>
</body>
</html>"""
    },
    
    "🛡️ Game Guardian": {
        "Script Básico": """--[[
    Game Guardian Script
    Use apenas para fins educacionais!
]]

gg.setVisible(false)
gg.toast("Script carregado!")

local running = true

function hackMoney()
    local input = gg.prompt({"Valor atual:", "Novo valor:"}, {0, 999999}, {"number", "number"})
    if input then
        gg.clearResults()
        gg.setRanges(gg.REGION_ANONYMOUS)
        gg.searchNumber(input[1], gg.TYPE_DWORD)
        local count = gg.getResultsCount()
        if count > 0 and count < 500 then
            local r = gg.getResults(count)
            for i,v in ipairs(r) do r[i].value = input[2] end
            gg.setValues(r)
            gg.toast("Alterado!")
        else
            gg.toast("Não encontrado")
        end
    end
end

function speedHack()
    local speeds = {0.5, 1, 2, 3, 5}
    local choice = gg.choice({"0.5x", "1x", "2x", "3x", "5x"}, nil, "Velocidade")
    if choice then
        gg.setSpeed(speeds[choice])
        gg.toast("Speed: " .. speeds[choice] .. "x")
    end
end

function mainMenu()
    local menu = gg.choice({
        "💰 Hack Valor",
        "⚡ Speed Hack",
        "🧹 Limpar",
        "❌ Sair"
    }, nil, "Menu")
    
    if menu == 1 then hackMoney()
    elseif menu == 2 then speedHack()
    elseif menu == 3 then gg.clearResults() gg.clearList() gg.toast("Limpo!")
    elseif menu == 4 then running = false gg.setSpeed(1) gg.toast("Bye!")
    end
end

while running do
    if gg.isVisible() then
        gg.setVisible(false)
        mainMenu()
    end
    gg.sleep(100)
end
os.exit()""",
    },
    
    "🎮 Godot 4.x": {
        "Player 2D": """extends CharacterBody2D

@export var speed = 300.0
@export var jump_velocity = -400.0

var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")

@onready var sprite = $AnimatedSprite2D

func _physics_process(delta):
    if not is_on_floor():
        velocity.y += gravity * delta
    
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = jump_velocity
    
    var direction = Input.get_axis("ui_left", "ui_right")
    
    if direction:
        velocity.x = direction * speed
        sprite.flip_h = direction < 0
        sprite.play("run")
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        sprite.play("idle")
    
    move_and_slide()
""",
    },
    
    "🐍 Python": {
        "Web Scraper": """import requests
from bs4 import BeautifulSoup
import json

def scrape(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'title': soup.title.string if soup.title else '',
            'links': [a.get('href') for a in soup.find_all('a', href=True)[:10]],
            'headings': [h.text.strip() for h in soup.find_all(['h1','h2','h3'])[:5]]
        }
        return data
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    result = scrape('https://example.com')
    print(json.dumps(result, indent=2))
""",
    },
    
    "🤖 Discord Bot": {
        "Bot Básico": """import discord
from discord import app_commands

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    print(f'{bot.user} online!')
    await tree.sync()

@tree.command(name="ping", description="Mostra latência")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency*1000)}ms")

@tree.command(name="ola", description="Diz olá")
async def ola(interaction: discord.Interaction):
    await interaction.response.send_message(f"Olá {interaction.user.name}!")

bot.run("SEU_TOKEN")
""",
    }
}

# ====== TELA DE LOGIN ======
if not st.session_state.authenticated:
    st.markdown("""
    <div class="header-premium">
        <h1>🎮 ScriptMaster AI Pro</h1>
        <p>Gerador Profissional de Scripts e Jogos com IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Entrar")
        username = st.text_input("👤 Seu nome", key="login_user_input")
        access_code = st.text_input("🎫 Código VIP (opcional)", type="password", key="login_code_input")
        remember = st.checkbox("🔒 Manter conectado", value=True, key="remember_check")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 ENTRAR", use_container_width=True, type="primary", key="btn_login"):
                if not username:
                    st.error("Digite seu nome!")
                elif access_code == MASTER_CODE:
                    st.session_state.authenticated = True
                    st.session_state.is_master = True
                    st.session_state.username = username
                    if remember:
                        save_session()
                    st.balloons()
                    st.rerun()
                elif access_code and access_code in st.session_state.created_codes:
                    code_info = st.session_state.created_codes[access_code]
                    if not code_info.get("used"):
                        st.session_state.created_codes[access_code]["used"] = True
                        days = code_info["days"]
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.vip_until = datetime.now() + timedelta(days=days if days != 999 else 3650)
                        if remember:
                            save_session()
                        st.success(f"VIP ativado!")
                        st.rerun()
                    else:
                        st.error("Código já usado!")
                elif access_code:
                    st.error("Código inválido!")
                else:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    if remember:
                        save_session()
                    st.rerun()
        
        with c2:
            if st.button("🆓 Modo Grátis", use_container_width=True, key="btn_free"):
                st.session_state.authenticated = True
                st.session_state.username = username if username else "Visitante"
                if remember:
                    save_session()
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 Recursos")
        st.markdown("""
        **🆓 GRATUITO:**
        - ✅ 4 gerações por dia
        - ✅ 10 mensagens de chat
        - ✅ Templates básicos
        
        **👑 VIP:**
        - ✅ Uso ILIMITADO
        - ✅ Todos os templates
        - ✅ Histórico salvo
        - ✅ Prioridade
        """)
    
    st.stop()

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown(f"""
    <div class="welcome-box">
        <h3>👋 Olá, {st.session_state.username}!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.is_master:
        st.markdown('<span class="master-badge">🔥 ADMIN</span>', unsafe_allow_html=True)
    elif is_vip():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<span class="vip-badge">👑 VIP - {dias}d</span>', unsafe_allow_html=True)
    else:
        st.info("🆓 Modo Gratuito")
    
    st.markdown("---")
    
    # Uso
    if is_vip():
        st.success("✨ Uso ilimitado!")
    else:
        st.markdown(f"""
        <div class="usage-box">
            ⚡ Gerações: {st.session_state.usage_count}/{DAILY_LIMIT_FREE}<br>
            💬 Chat: {st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}<br>
            <small>🔄 Renova à meia-noite</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Admin
    if st.session_state.is_master:
        st.markdown("---")
        with st.expander("🎫 Criar Código VIP"):
            new_code = st.text_input("Nome do código", key="new_code_input")
            code_days = st.selectbox("Duração", ["1 dia", "7 dias", "30 dias", "Ilimitado"], key="code_days_select")
            
            if st.button("✨ Criar Código", key="btn_create_code"):
                if new_code and new_code not in st.session_state.created_codes:
                    days_map = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                    st.session_state.created_codes[new_code] = {
                        "days": days_map[code_days],
                        "used": False
                    }
                    st.success(f"Código criado!")
                    st.code(new_code)
    
    # Templates
    st.markdown("---")
    st.markdown("### 📚 Templates")
    
    template_counter = 0
    for category, templates in TEMPLATES.items():
        with st.expander(category):
            for name, code in templates.items():
                template_counter += 1
                if st.button(f"📄 {name}", key=f"template_btn_{template_counter}", use_container_width=True):
                    st.session_state.current_script = code
                    st.toast(f"✅ Template carregado!")
                    st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
        clear_session()
        st.rerun()

# ====== ÁREA PRINCIPAL ======
st.markdown("""
<div class="header-premium">
    <h1>🎮 ScriptMaster AI Pro</h1>
    <p>Gerador de Scripts e Jogos com Inteligência Artificial</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 Gerar", "💬 Chat", "💻 Editor", "📚 Biblioteca", "📊 Stats"])

# ====== TAB GERAR ======
with tab1:
    st.markdown("### 🎯 Descreva o que você quer criar")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_area(
            "📝 Descrição:",
            placeholder="Ex: Crie um jogo de plataforma 2D em HTML5 para mobile...",
            height=120,
            key="gen_prompt_area"
        )
    
    with col2:
        tipo = st.selectbox("🔤 Tipo", [
            "HTML5 Android",
            "Godot 4.x (GDScript)",
            "Unity (C#)",
            "Discord Bot",
            "Game Guardian (Lua)",
            "Python Script",
            "JavaScript"
        ], key="gen_type_select")
        nivel = st.select_slider("📊 Complexidade", ["Básico", "Médio", "Avançado"], key="gen_level_slider")
    
    can_gen, remaining = can_generate()
    
    if not can_gen:
        st.warning(f"⚠️ Limite atingido! Volte amanhã ou seja VIP.")
    
    gen_btn_key = f"btn_generate_{st.session_state.gen_counter}"
    
    if st.button("⚡ GERAR CÓDIGO", use_container_width=True, type="primary", disabled=not can_gen, key=gen_btn_key):
        if not prompt:
            st.error("Descreva o que você quer criar!")
        else:
            with st.spinner("🔮 Gerando código..."):
                try:
                    model = get_model()
                    if not model:
                        st.error("API indisponível!")
                        st.stop()
                    
                    system_prompt = f"""Você é um programador expert em {tipo}. 
Crie código COMPLETO e FUNCIONAL.

TAREFA: {prompt}
NÍVEL: {nivel}

REGRAS:
1. Código 100% funcional
2. Comentários em português
3. Se for jogo mobile HTML5: usar touch events, viewport correto
4. Se for Game Guardian: usar gg.* API
5. Retorne APENAS o código, sem markdown"""

                    response = model.generate_content(system_prompt)
                    codigo = response.text
                    
                    codigo = re.sub(r'^```[\w]*\n?', '', codigo)
                    codigo = re.sub(r'\n?```$', '', codigo)
                    codigo = codigo.strip()
                    
                    st.session_state.current_script = codigo
                    use_generation()
                    
                    st.success("✅ Código gerado!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    # Mostrar código gerado
    if st.session_state.current_script:
        st.markdown("---")
        st.markdown("### 📄 Código Gerado:")
        
        lang, ext = detect_language(st.session_state.current_script)
        st.code(st.session_state.current_script, language=lang)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "📥 Download",
                st.session_state.current_script,
                f"script{ext}",
                use_container_width=True,
                key="btn_download_gen"
            )
        
        with col2:
            if st.button("💾 Salvar", use_container_width=True, key="btn_save_gen"):
                script_id = generate_unique_id()
                st.session_state.saved_scripts.append({
                    "id": script_id,
                    "name": f"Script_{script_id}{ext}",
                    "code": st.session_state.current_script,
                    "date": datetime.now().strftime("%d/%m %H:%M")
                })
                save_session()
                st.success("Salvo!")
        
        with col3:
            if st.button("⭐ Favoritar", use_container_width=True, key="btn_fav_gen"):
                fav_id = generate_unique_id()
                st.session_state.favorites.append({
                    "id": fav_id,
                    "name": f"Fav_{fav_id}{ext}",
                    "code": st.session_state.current_script,
                    "date": datetime.now().strftime("%d/%m %H:%M")
                })
                save_session()
                st.success("Favoritado!")

# ====== TAB CHAT ======
with tab2:
    st.markdown("### 💬 Chat com IA")
    
    # Histórico
    for idx, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
                <strong>👤 Você:</strong><br>{msg["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🗑️", key=f"del_user_msg_{idx}"):
                st.session_state.chat_history.pop(idx)
                save_session()
                st.rerun()
        else:
            st.markdown(f"""
            <div class="chat-assistant">
                <strong>🤖 IA:</strong><br>{msg["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 10])
            with col1:
                if st.button("📋", key=f"copy_ai_msg_{idx}"):
                    st.code(msg["content"])
            with col2:
                if st.button("🗑️", key=f"del_ai_msg_{idx}"):
                    st.session_state.chat_history.pop(idx)
                    save_session()
                    st.rerun()
    
    st.markdown("---")
    
    can_ch, _ = can_chat()
    
    if not can_ch:
        st.warning("⚠️ Limite de chat atingido!")
    
    user_input = st.text_input("💭 Mensagem:", key="chat_input_field", disabled=not can_ch)
    
    if st.button("📤 Enviar", disabled=not can_ch or not user_input, key="btn_send_chat"):
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            with st.spinner("Pensando..."):
                try:
                    model = get_model()
                    
                    context = "\n".join([
                        f"{'Usuário' if m['role']=='user' else 'IA'}: {m['content']}"
                        for m in st.session_state.chat_history[-10:]
                    ])
                    
                    response = model.generate_content(f"""Você é um assistente de programação.
Responda de forma clara e útil em português.

Conversa:
{context}

Responda à última mensagem.""")
                    
                    ai_response = response.text
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    use_chat()
                    save_session()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    if st.button("🧹 Limpar Chat", key="btn_clear_chat"):
        st.session_state.chat_history = []
        save_session()
        st.rerun()

# ====== TAB EDITOR ======
with tab3:
    st.markdown("### 💻 Editor de Código")
    
    if st.session_state.current_script:
        lang, ext = detect_language(st.session_state.current_script)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            filename = st.text_input("📄 Nome", value=f"script{ext}", key="editor_filename")
        with col2:
            st.download_button(
                "📥 Download",
                st.session_state.current_script,
                filename,
                use_container_width=True,
                key="btn_download_editor"
            )
        
        new_code = st.text_area(
            "✏️ Código:",
            st.session_state.current_script,
            height=400,
            key="editor_code_area"
        )
        st.session_state.current_script = new_code
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Salvar", use_container_width=True, key="btn_save_editor"):
                script_id = generate_unique_id()
                st.session_state.saved_scripts.append({
                    "id": script_id,
                    "name": filename,
                    "code": new_code,
                    "date": datetime.now().strftime("%d/%m %H:%M")
                })
                save_session()
                st.success("Salvo!")
        
        with col2:
            if st.button("⭐ Favoritar", use_container_width=True, key="btn_fav_editor"):
                fav_id = generate_unique_id()
                st.session_state.favorites.append({
                    "id": fav_id,
                    "name": filename,
                    "code": new_code,
                    "date": datetime.now().strftime("%d/%m %H:%M")
                })
                save_session()
                st.success("Favoritado!")
        
        with col3:
            if st.button("🗑️ Limpar", use_container_width=True, key="btn_clear_editor"):
                st.session_state.current_script = ""
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 👁️ Preview")
        st.code(new_code, language=lang)
    else:
        st.info("📝 Nenhum código no editor. Gere um código ou selecione um template!")

# ====== TAB BIBLIOTECA ======
with tab4:
    st.markdown("### 📚 Biblioteca")
    
    tab_saved, tab_favs = st.tabs(["📄 Salvos", "⭐ Favoritos"])
    
    with tab_saved:
        if st.session_state.saved_scripts:
            for idx, script in enumerate(reversed(st.session_state.saved_scripts)):
                script_id = script.get("id", f"old_{idx}")
                with st.expander(f"📄 {script['name']} - {script.get('date', '')}"):
                    st.code(script['code'][:500] + "..." if len(script['code']) > 500 else script['code'])
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📋 Carregar", key=f"load_saved_{script_id}"):
                            st.session_state.current_script = script['code']
                            st.success("Carregado!")
                            st.rerun()
                    
                    with col2:
                        st.download_button(
                            "📥 Download",
                            script['code'],
                            script['name'],
                            key=f"dl_saved_{script_id}"
                        )
                    
                    with col3:
                        if st.button("🗑️ Deletar", key=f"del_saved_{script_id}"):
                            real_idx = len(st.session_state.saved_scripts) - 1 - idx
                            st.session_state.saved_scripts.pop(real_idx)
                            save_session()
                            st.rerun()
        else:
            st.info("Nenhum script salvo!")
    
    with tab_favs:
        if st.session_state.favorites:
            for idx, fav in enumerate(reversed(st.session_state.favorites)):
                fav_id = fav.get("id", f"oldfav_{idx}")
                with st.expander(f"⭐ {fav['name']} - {fav.get('date', '')}"):
                    st.code(fav['code'][:500] + "..." if len(fav['code']) > 500 else fav['code'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📋 Carregar", key=f"load_fav_{fav_id}"):
                            st.session_state.current_script = fav['code']
                            st.success("Carregado!")
                            st.rerun()
                    
                    with col2:
                        if st.button("🗑️ Remover", key=f"del_fav_{fav_id}"):
                            real_idx = len(st.session_state.favorites) - 1 - idx
                            st.session_state.favorites.pop(real_idx)
                            save_session()
                            st.rerun()
        else:
            st.info("Nenhum favorito!")

# ====== TAB STATS ======
with tab5:
    st.markdown("### 📊 Estatísticas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Salvos", len(st.session_state.saved_scripts))
    with col2:
        st.metric("⭐ Favoritos", len(st.session_state.favorites))
    with col3:
        st.metric("💬 Mensagens", len(st.session_state.chat_history))
    with col4:
        total = sum(len(s.get('code', '').split('\n')) for s in st.session_state.saved_scripts)
        st.metric("📏 Linhas", total)
    
    st.markdown("---")
    
    if is_vip():
        st.success("👑 Você é VIP! Uso ilimitado.")
    else:
        st.info(f"""
        📊 **Uso de Hoje:**
        - Gerações: {st.session_state.usage_count}/{DAILY_LIMIT_FREE}
        - Chat: {st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}
        
        🔄 Os limites renovam à meia-noite!
        """)

# ====== RODAPÉ ======
st.markdown("---")
st.caption("💡 ScriptMaster AI Pro v3.0 | Desenvolvido por Guizinhs")
