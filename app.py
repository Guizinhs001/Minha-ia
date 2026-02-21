import streamlit as st
from openai import OpenAI
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
    page_title="Rynmaru IA 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CONSTANTES ======
DAILY_LIMIT_FREE = 4
DAILY_LIMIT_CHAT_FREE = 10

# ====== GERADOR DE KEY ÚNICA ======
def get_unique_key(prefix="key"):
    if "key_counter" not in st.session_state:
        st.session_state.key_counter = 0
    st.session_state.key_counter += 1
    return f"{prefix}_{st.session_state.key_counter}_{random.randint(1000, 9999)}"

# ====== CSS ======
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0a1a2e 100%);
    }
    
    .header-premium {
        background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 50%, #f107a3 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(123, 47, 247, 0.4);
    }
    
    .header-premium h1 {
        font-family: 'Orbitron', sans-serif;
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.8);
    }
    
    .header-premium p {
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
    }
    
    .master-badge {
        background: linear-gradient(135deg, #ff0844, #ffb199);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        color: #000;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .free-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    
    .deepseek-badge {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .chat-user {
        background: linear-gradient(135deg, #7b2ff7, #f107a3);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 15%;
    }
    
    .chat-assistant {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 15%;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    .usage-box {
        background: rgba(123, 47, 247, 0.2);
        border: 1px solid rgba(123, 47, 247, 0.4);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .welcome-box {
        background: linear-gradient(135deg, #7b2ff7, #f107a3);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .stat-card {
        background: rgba(123, 47, 247, 0.15);
        border: 1px solid rgba(123, 47, 247, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ====== FUNÇÕES DE PERSISTÊNCIA ======
def compress_data(data):
    try:
        json_str = json.dumps(data, separators=(',', ':'), default=str)
        compressed = zlib.compress(json_str.encode(), 9)
        return base64.urlsafe_b64encode(compressed).decode()
    except:
        return ""

def decompress_data(encoded):
    try:
        compressed = base64.urlsafe_b64decode(encoded.encode())
        json_str = zlib.decompress(compressed).decode()
        return json.loads(json_str)
    except:
        return None

def generate_token(username, is_master):
    data = f"{username}|{is_master}|rynmaru_v1"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def generate_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def save_session():
    try:
        data = {
            "u": st.session_state.get("username", ""),
            "m": 1 if st.session_state.get("is_master", False) else 0,
            "v": 0,
            "uc": st.session_state.get("usage_count", 0),
            "cc": st.session_state.get("chat_count", 0),
            "lr": st.session_state.get("last_reset", ""),
            "ss": st.session_state.get("saved_scripts", [])[-15:],
            "fv": st.session_state.get("favorites", [])[-10:],
            "ch": st.session_state.get("chat_history", [])[-30:],
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
    today = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.get("last_reset") != today:
        st.session_state.usage_count = 0
        st.session_state.chat_count = 0
        st.session_state.last_reset = today

def clear_session():
    st.query_params.clear()
    for key in list(st.session_state.keys()):
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
    "key_counter": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Auto-login
if not st.session_state.authenticated and not st.session_state.login_checked:
    st.session_state.login_checked = True
    if load_session():
        st.toast(f"✅ Bem-vindo de volta, {st.session_state.username}!")

# ====== CONFIGURAÇÃO DEEPSEEK (ÚNICA API) ======
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")
MASTER_CODE = st.secrets.get("MASTER_CODE", "GuizinhsDono")

# Verificação da API DeepSeek
if not DEEPSEEK_API_KEY:
    st.markdown("""
    <div class="header-premium">
        <h1>🎮 RYNMARU IA</h1>
        <p>Configuração Necessária</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.error("❌ Configure a chave API do DeepSeek!")
    
    st.markdown("### 📋 Como configurar:")
    
    st.markdown("""
    1. Acesse [platform.deepseek.com](https://platform.deepseek.com/)
    2. Crie uma conta ou faça login
    3. Vá em **API Keys** e crie uma nova chave
    4. No Streamlit Cloud, vá em **Settings > Secrets**
    5. Adicione:
    """)
    
    st.code("""DEEPSEEK_API_KEY = "sk-sua-chave-deepseek-aqui"
MASTER_CODE = "GuizinhsDono"
    """, language="toml")
    
    st.info("💡 A DeepSeek oferece créditos gratuitos para novos usuários!")
    
    st.stop()

# Cliente DeepSeek
try:
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
except Exception as e:
    st.error(f"❌ Erro ao conectar com DeepSeek: {e}")
    st.stop()

# ====== FUNÇÃO DE GERAÇÃO COM DEEPSEEK ======
def generate_with_deepseek(prompt, system_prompt=None):
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "Você é um programador expert. Responda em português."})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=4000,
            temperature=0.7
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

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
    save_session()

def use_chat():
    st.session_state.chat_count += 1
    save_session()

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
    "🎮 Jogos HTML5 Android": {
        "Jogo de Coleta": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <title>Jogo de Coleta</title>
    <style>
        * { margin: 0; padding: 0; touch-action: manipulation; user-select: none; }
        body { background: #0a0a1a; overflow: hidden; }
        canvas { display: block; }
        #ui { position: fixed; top: 15px; left: 15px; right: 15px; display: flex; justify-content: space-between; color: #fff; font: bold 20px Arial; z-index: 100; }
        #gameOver { position: fixed; inset: 0; background: rgba(0,0,0,0.9); display: none; flex-direction: column; align-items: center; justify-content: center; color: #fff; z-index: 200; }
        #gameOver.show { display: flex; }
        #gameOver h1 { font-size: 36px; color: #7b2ff7; }
        #gameOver button { margin-top: 30px; padding: 15px 40px; font-size: 18px; background: #7b2ff7; border: none; border-radius: 25px; color: #fff; font-weight: bold; }
    </style>
</head>
<body>
    <canvas id="game"></canvas>
    <div id="ui">
        <span>🪙 <span id="score">0</span></span>
        <span>⏱️ <span id="time">30</span>s</span>
    </div>
    <div id="gameOver">
        <h1>🎮 Fim!</h1>
        <p style="font-size:20px;margin-top:15px;">Pontos: <span id="finalScore">0</span></p>
        <button onclick="startGame()">🔄 Jogar</button>
    </div>
    <script>
        const canvas = document.getElementById('game');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        let score = 0, timeLeft = 30, running = false;
        const player = { x: canvas.width/2, y: canvas.height/2, size: 50 };
        let coins = [];
        
        function spawnCoin() {
            coins.push({
                x: Math.random() * (canvas.width - 40) + 20,
                y: Math.random() * (canvas.height - 120) + 60,
                size: 20 + Math.random() * 10
            });
        }
        
        function startGame() {
            score = 0; timeLeft = 30; coins = []; running = true;
            document.getElementById('gameOver').classList.remove('show');
            for (let i = 0; i < 5; i++) spawnCoin();
        }
        
        function endGame() {
            running = false;
            document.getElementById('finalScore').textContent = score;
            document.getElementById('gameOver').classList.add('show');
        }
        
        function update() {
            if (!running) return;
            for (let i = coins.length - 1; i >= 0; i--) {
                const dist = Math.hypot(player.x - coins[i].x, player.y - coins[i].y);
                if (dist < player.size/2 + coins[i].size) {
                    coins.splice(i, 1);
                    score++;
                    document.getElementById('score').textContent = score;
                    spawnCoin();
                }
            }
        }
        
        function draw() {
            ctx.fillStyle = '#0a0a1a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            coins.forEach(c => {
                ctx.fillStyle = '#ffd700';
                ctx.beginPath();
                ctx.arc(c.x, c.y, c.size, 0, Math.PI * 2);
                ctx.fill();
            });
            
            ctx.fillStyle = '#7b2ff7';
            ctx.beginPath();
            ctx.arc(player.x, player.y, player.size/2, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(player.x - 10, player.y - 5, 8, 0, Math.PI * 2);
            ctx.arc(player.x + 10, player.y - 5, 8, 0, Math.PI * 2);
            ctx.fill();
        }
        
        function loop() { update(); draw(); requestAnimationFrame(loop); }
        
        setInterval(() => {
            if (running && timeLeft > 0) {
                timeLeft--;
                document.getElementById('time').textContent = timeLeft;
                if (timeLeft <= 0) endGame();
            }
        }, 1000);
        
        function move(x, y) {
            player.x = Math.max(25, Math.min(canvas.width - 25, x));
            player.y = Math.max(60, Math.min(canvas.height - 25, y));
        }
        
        canvas.addEventListener('touchstart', e => { e.preventDefault(); if (!running) startGame(); else move(e.touches[0].clientX, e.touches[0].clientY); });
        canvas.addEventListener('touchmove', e => { e.preventDefault(); if (running) move(e.touches[0].clientX, e.touches[0].clientY); });
        canvas.addEventListener('mousemove', e => { if (running) move(e.clientX, e.clientY); });
        canvas.addEventListener('click', () => { if (!running) startGame(); });
        
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
        body { background: #0a0a1a; overflow: hidden; }
        canvas { display: block; }
        #ui { position: fixed; top: 10px; left: 10px; color: #0ff; font: bold 20px Arial; z-index: 10; }
        #overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; z-index: 100; }
        #overlay.hidden { display: none; }
        #overlay h1 { font-size: 40px; color: #0ff; }
        #overlay button { margin-top: 30px; padding: 15px 50px; font-size: 20px; background: #0ff; border: none; border-radius: 25px; font-weight: bold; }
    </style>
</head>
<body>
    <canvas id="c"></canvas>
    <div id="ui">🏃 <span id="score">0</span>m</div>
    <div id="overlay">
        <h1 id="title">⚡ RUNNER</h1>
        <p id="text" style="margin-top:15px;font-size:18px;">Toque para pular!</p>
        <button onclick="start()">▶️ JOGAR</button>
    </div>
    <script>
        const c = document.getElementById('c'), ctx = c.getContext('2d');
        c.width = innerWidth; c.height = innerHeight;
        
        let score = 0, speed = 6, playing = false;
        const ground = c.height - 80;
        const player = { x: 80, y: ground - 50, w: 40, h: 50, vy: 0, jump: false };
        let obs = [];
        let frame = 0;
        
        function addObs() {
            obs.push({ x: c.width, y: ground - 40, w: 25, h: 40 });
        }
        
        function jump() {
            if (!playing) return;
            if (!player.jump) {
                player.vy = -16;
                player.jump = true;
            }
        }
        
        function start() {
            score = 0; speed = 6; obs = []; frame = 0;
            player.y = ground - player.h; player.vy = 0; player.jump = false;
            playing = true;
            document.getElementById('overlay').classList.add('hidden');
        }
        
        function gameOver() {
            playing = false;
            document.getElementById('title').textContent = '💀 FIM';
            document.getElementById('text').textContent = 'Pontos: ' + score;
            document.getElementById('overlay').classList.remove('hidden');
        }
        
        function update() {
            if (!playing) return;
            frame++;
            
            player.vy += 0.8;
            player.y += player.vy;
            if (player.y + player.h >= ground) {
                player.y = ground - player.h;
                player.vy = 0;
                player.jump = false;
            }
            
            if (frame % 80 === 0) addObs();
            
            for (let i = obs.length - 1; i >= 0; i--) {
                obs[i].x -= speed;
                
                if (player.x < obs[i].x + obs[i].w && player.x + player.w > obs[i].x &&
                    player.y + player.h > obs[i].y) {
                    gameOver();
                    return;
                }
                
                if (obs[i].x + obs[i].w < 0) {
                    obs.splice(i, 1);
                    score++;
                    document.getElementById('score').textContent = score;
                    if (score % 10 === 0) speed += 0.3;
                }
            }
        }
        
        function draw() {
            ctx.fillStyle = '#0a0a1a';
            ctx.fillRect(0, 0, c.width, c.height);
            
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, ground, c.width, c.height - ground);
            ctx.fillStyle = '#0ff';
            ctx.fillRect(0, ground, c.width, 3);
            
            ctx.fillStyle = '#0ff';
            ctx.fillRect(player.x, player.y, player.w, player.h);
            
            ctx.fillStyle = '#f00';
            obs.forEach(o => ctx.fillRect(o.x, o.y, o.w, o.h));
        }
        
        function loop() { update(); draw(); requestAnimationFrame(loop); }
        
        c.addEventListener('touchstart', e => { e.preventDefault(); jump(); });
        c.addEventListener('click', jump);
        
        loop();
    </script>
</body>
</html>"""
    },
    
    "🛡️ Game Guardian": {
        "Script Básico": """--[[
    Rynmaru GG Script
    ⚠️ Uso educacional apenas!
]]

gg.setVisible(false)
gg.toast("🎮 Script carregado!")

local running = true

local function toast(msg) gg.toast(msg) end

local function hackValor()
    local inp = gg.prompt({"Valor atual:", "Novo valor:"}, {"0", "999999"}, {"number", "number"})
    if not inp then return end
    
    gg.clearResults()
    gg.setRanges(gg.REGION_ANONYMOUS)
    gg.searchNumber(inp[1], gg.TYPE_DWORD)
    
    local count = gg.getResultsCount()
    if count > 0 and count < 500 then
        local r = gg.getResults(count)
        for i, v in ipairs(r) do r[i].value = inp[2] end
        gg.setValues(r)
        toast("✅ " .. count .. " valores alterados!")
    else
        gg.searchNumber(inp[1], gg.TYPE_FLOAT)
        count = gg.getResultsCount()
        if count > 0 and count < 500 then
            local r = gg.getResults(count)
            for i, v in ipairs(r) do r[i].value = inp[2] end
            gg.setValues(r)
            toast("✅ Alterado!")
        else
            toast("❌ Não encontrado")
        end
    end
end

local function speedHack()
    local speeds = {0.5, 1, 2, 3, 5}
    local choice = gg.choice({"0.5x", "1x", "2x", "3x", "5x"}, nil, "Velocidade")
    if choice then
        gg.setSpeed(speeds[choice])
        toast("⚡ " .. speeds[choice] .. "x")
    end
end

local function menu()
    local m = gg.choice({
        "💰 Hack Valor",
        "⚡ Speed Hack",
        "🧹 Limpar",
        "❌ Sair"
    }, nil, "🎮 Rynmaru GG")
    
    if m == 1 then hackValor()
    elseif m == 2 then speedHack()
    elseif m == 3 then gg.clearResults() gg.clearList() gg.setSpeed(1) toast("Limpo!")
    elseif m == 4 then running = false gg.setSpeed(1) toast("Bye!")
    end
end

while running do
    if gg.isVisible() then
        gg.setVisible(false)
        menu()
    end
    gg.sleep(100)
end
os.exit()"""
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
    
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity
    
    var dir = Input.get_axis("move_left", "move_right")
    
    if dir:
        velocity.x = dir * speed
        sprite.flip_h = dir < 0
        sprite.play("run")
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        sprite.play("idle")
    
    move_and_slide()
"""
    },
    
    "🐍 Python": {
        "Web Scraper": """import requests
from bs4 import BeautifulSoup
import json

def scrape(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        return {
            'title': soup.title.string if soup.title else '',
            'links': [a.get('href') for a in soup.find_all('a', href=True)[:10]]
        }
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    print(json.dumps(scrape('https://example.com'), indent=2))
""",

        "API Flask": """from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db = {"items": []}

@app.route('/')
def home():
    return jsonify({"api": "Rynmaru API", "version": "1.0"})

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(db["items"])

@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    if data:
        db["items"].append(data)
        return jsonify({"ok": True}), 201
    return jsonify({"error": "Dados inválidos"}), 400

if __name__ == '__main__':
    app.run(debug=True)
"""
    }
}

# ====== TELA DE LOGIN ======
if not st.session_state.authenticated:
    st.markdown("""
    <div class="header-premium">
        <h1>🎮 RYNMARU IA</h1>
        <p>Gerador de Scripts e Jogos com IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<span class="deepseek-badge">🧠 Powered by DeepSeek</span>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Entrar")
        username = st.text_input("👤 Nome", key=get_unique_key("user"))
        access_code = st.text_input("🎫 Código VIP", type="password", key=get_unique_key("code"))
        remember = st.checkbox("🔒 Lembrar", value=True, key=get_unique_key("rem"))
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 ENTRAR", use_container_width=True, type="primary", key=get_unique_key("login")):
                if not username:
                    st.error("Digite seu nome!")
                elif access_code == MASTER_CODE:
                    st.session_state.authenticated = True
                    st.session_state.is_master = True
                    st.session_state.username = username
                    if remember: save_session()
                    st.balloons()
                    st.rerun()
                elif access_code and access_code in st.session_state.created_codes:
                    info = st.session_state.created_codes[access_code]
                    if not info.get("used"):
                        st.session_state.created_codes[access_code]["used"] = True
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.vip_until = datetime.now() + timedelta(days=info["days"] if info["days"] != 999 else 3650)
                        if remember: save_session()
                        st.success("VIP ativado!")
                        st.rerun()
                    else:
                        st.error("Código já usado!")
                elif access_code:
                    st.error("Código inválido!")
                else:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    if remember: save_session()
                    st.rerun()
        
        with c2:
            if st.button("🆓 Grátis", use_container_width=True, key=get_unique_key("free")):
                st.session_state.authenticated = True
                st.session_state.username = username if username else "Visitante"
                if remember: save_session()
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 Planos")
        st.markdown("""
        **🆓 Gratuito:** 4 gerações/dia, 10 chats/dia
        
        **👑 VIP:** Ilimitado + Salvar scripts + Favoritos
        """)
    
    st.stop()

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown(f'<div class="welcome-box"><h3>👋 {st.session_state.username}</h3></div>', unsafe_allow_html=True)
    
    if st.session_state.is_master:
        st.markdown('<span class="master-badge">🔥 ADMIN</span>', unsafe_allow_html=True)
    elif is_vip():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<span class="vip-badge">👑 VIP {dias}d</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="free-badge">🆓 Free</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<span class="deepseek-badge">🧠 DeepSeek AI</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if is_vip():
        st.success("✨ Ilimitado!")
    else:
        st.markdown(f"""
        <div class="usage-box">
            ⚡ Gerações: {st.session_state.usage_count}/{DAILY_LIMIT_FREE}<br>
            💬 Chat: {st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.is_master:
        st.markdown("---")
        with st.expander("🎫 Criar VIP"):
            code = st.text_input("Código", key=get_unique_key("nc"))
            days = st.selectbox("Dias", ["1 dia", "7 dias", "30 dias", "Ilimitado"], key=get_unique_key("nd"))
            if st.button("✨ Criar", key=get_unique_key("bc")):
                if code:
                    dm = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                    st.session_state.created_codes[code] = {"days": dm[days], "used": False}
                    st.success("✅ Criado!")
                    st.code(code)
    
    st.markdown("---")
    st.markdown("### 📚 Templates")
    
    for cat, temps in TEMPLATES.items():
        with st.expander(cat):
            for name, code in temps.items():
                if st.button(f"📄 {name}", key=get_unique_key(f"t{name[:5]}"), use_container_width=True):
                    st.session_state.current_script = code
                    st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True, key=get_unique_key("out")):
        clear_session()
        st.rerun()

# ====== PRINCIPAL ======
st.markdown("""
<div class="header-premium">
    <h1>🎮 RYNMARU IA</h1>
    <p>Gerador de Scripts com DeepSeek</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 Gerar", "💬 Chat", "💻 Editor", "📚 Biblioteca", "📊 Stats"])

# TAB GERAR
with tab1:
    st.markdown("### 🎯 O que você quer criar?")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        prompt = st.text_area("📝 Descrição:", height=100, key=get_unique_key("pr"))
    with col2:
        tipo = st.selectbox("Tipo", ["HTML5 Android", "Godot 4.x", "Unity C#", "Discord Bot", "Game Guardian", "Python", "JavaScript"], key=get_unique_key("tp"))
        nivel = st.select_slider("Nível", ["Básico", "Médio", "Avançado"], key=get_unique_key("nv"))
    
    can_gen, _ = can_generate()
    
    if not can_gen:
        st.warning("⚠️ Limite atingido! Seja VIP.")
    
    if st.button("⚡ GERAR", use_container_width=True, type="primary", disabled=not can_gen, key=get_unique_key("gen")):
        if not prompt:
            st.error("Descreva o que quer!")
        else:
            with st.spinner("🧠 DeepSeek gerando..."):
                sys = f"Você é expert em {tipo}. Crie código COMPLETO e FUNCIONAL. Nível: {nivel}. APENAS código, sem markdown."
                result, err = generate_with_deepseek(prompt, sys)
                
                if err:
                    st.error(f"Erro: {err}")
                elif result:
                    code = re.sub(r'^```[\w]*\n?', '', result)
                    code = re.sub(r'\n?```$', '', code).strip()
                    st.session_state.current_script = code
                    use_generation()
                    st.success("✅ Gerado!")
                    st.rerun()
    
    if st.session_state.current_script:
        st.markdown("---")
        lang, ext = detect_language(st.session_state.current_script)
        st.code(st.session_state.current_script, language=lang)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("📥 Download", st.session_state.current_script, f"code{ext}", key=get_unique_key("dl"))
        with c2:
            if is_vip() and st.button("💾 Salvar", key=get_unique_key("sv")):
                st.session_state.saved_scripts.append({"id": generate_id(), "name": f"Script{ext}", "code": st.session_state.current_script, "date": datetime.now().strftime("%d/%m %H:%M")})
                save_session()
                st.success("Salvo!")
        with c3:
            if st.button("🗑️ Limpar", key=get_unique_key("cl")):
                st.session_state.current_script = ""
                st.rerun()

# TAB CHAT
with tab2:
    st.markdown("### 💬 Chat com DeepSeek")
    
    for i, m in enumerate(st.session_state.chat_history):
        if m["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {m["content"][:500]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-assistant">🧠 {m["content"][:1000]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    can_ch, _ = can_chat()
    msg = st.text_input("💭 Mensagem:", key=get_unique_key("msg"), disabled=not can_ch)
    
    if st.button("📤 Enviar", disabled=not can_ch or not msg, key=get_unique_key("snd")):
        st.session_state.chat_history.append({"role": "user", "content": msg})
        
        with st.spinner("🧠 Pensando..."):
            ctx = "\n".join([f"{'User' if m['role']=='user' else 'AI'}: {m['content'][:300]}" for m in st.session_state.chat_history[-6:]])
            result, _ = generate_with_deepseek(f"Conversa:\n{ctx}\n\nResponda:", "Você é Rynmaru, assistente de programação. Responda em português.")
            
            if result:
                st.session_state.chat_history.append({"role": "assistant", "content": result})
                use_chat()
                save_session()
                st.rerun()
    
    if st.button("🧹 Limpar", key=get_unique_key("clc")):
        st.session_state.chat_history = []
        save_session()
        st.rerun()

# TAB EDITOR
with tab3:
    st.markdown("### 💻 Editor")
    
    if st.session_state.current_script:
        lang, ext = detect_language(st.session_state.current_script)
        
        c1, c2 = st.columns([3, 1])
        with c1:
            fname = st.text_input("Nome", value=f"script{ext}", key=get_unique_key("fn"))
        with c2:
            st.download_button("📥", st.session_state.current_script, fname, key=get_unique_key("dle"))
        
        code = st.text_area("Código:", st.session_state.current_script, height=350, key=get_unique_key("ed"))
        st.session_state.current_script = code
        
        st.code(code, language=lang)
    else:
        st.info("Gere ou carregue um código!")

# TAB BIBLIOTECA
with tab4:
    st.markdown("### 📚 Biblioteca")
    
    if not is_vip():
        st.warning("🔒 VIP apenas!")
    else:
        if st.session_state.saved_scripts:
            for i, s in enumerate(reversed(st.session_state.saved_scripts)):
                with st.expander(f"📄 {s['name']} - {s.get('date', '')}"):
                    st.code(s['code'][:300], language=detect_language(s['code'])[0])
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("📋 Carregar", key=get_unique_key(f"ld{s['id']}")):
                            st.session_state.current_script = s['code']
                            st.rerun()
                    with c2:
                        if st.button("🗑️", key=get_unique_key(f"rm{s['id']}")):
                            idx = len(st.session_state.saved_scripts) - 1 - i
                            st.session_state.saved_scripts.pop(idx)
                            save_session()
                            st.rerun()
        else:
            st.info("Nenhum script salvo.")

# TAB STATS
with tab5:
    st.markdown("### 📊 Stats")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><h2>📄</h2><h3>{len(st.session_state.saved_scripts)}</h3><p>Salvos</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><h2>💬</h2><h3>{len(st.session_state.chat_history)}</h3><p>Msgs</p></div>', unsafe_allow_html=True)
    with c3:
        total = sum(len(s.get('code', '').split('\n')) for s in st.session_state.saved_scripts)
        st.markdown(f'<div class="stat-card"><h2>📏</h2><h3>{total}</h3><p>Linhas</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.is_master:
        st.success("🔥 ADMIN - Acesso Total")
    elif is_vip():
        st.success(f"👑 VIP - {(st.session_state.vip_until - datetime.now()).days} dias restantes")
    else:
        st.info(f"🆓 Free | Gerações: {st.session_state.usage_count}/{DAILY_LIMIT_FREE} | Chat: {st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}")

st.markdown("---")
st.caption("🎮 Rynmaru IA v1.0 | Powered by DeepSeek 🧠")