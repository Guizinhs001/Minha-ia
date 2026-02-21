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
import time

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

# ====== GERADOR DE KEY ÚNICA ======
def get_unique_key(prefix="key"):
    """Gera uma key única para evitar duplicação"""
    if "key_counter" not in st.session_state:
        st.session_state.key_counter = 0
    st.session_state.key_counter += 1
    return f"{prefix}_{st.session_state.key_counter}_{random.randint(1000, 9999)}"

# ====== CSS PREMIUM ======
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
        position: relative;
        overflow: hidden;
    }
    
    .header-premium::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    .header-premium h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        position: relative;
        z-index: 1;
    }
    
    .header-premium p {
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .master-badge {
        background: linear-gradient(135deg, #dc2626, #991b1b);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4);
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
    }
    
    .free-badge {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4); }
        50% { transform: scale(1.05); box-shadow: 0 6px 20px rgba(220, 38, 38, 0.6); }
    }
    
    .chat-user {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 1rem 1.2rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.75rem 0;
        margin-left: 15%;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .chat-assistant {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: #e2e8f0;
        padding: 1rem 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.75rem 0;
        margin-right: 15%;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .usage-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 15px;
        padding: 1.2rem;
        margin: 1rem 0;
    }
    
    .welcome-box {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    }
    
    .vip-feature {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1));
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .free-feature {
        background: rgba(107, 114, 128, 0.1);
        border: 1px solid rgba(107, 114, 128, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .code-container {
        background: #0d1117;
        border-radius: 12px;
        border: 1px solid #30363d;
        overflow: hidden;
    }
    
    .locked-feature {
        opacity: 0.6;
        position: relative;
    }
    
    .locked-feature::after {
        content: '🔒 VIP';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(245, 158, 11, 0.9);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ====== FUNÇÕES DE PERSISTÊNCIA ======
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
    data = f"{username}|{is_master}|scriptmaster_v4"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def generate_id():
    """Gera ID único"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

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
            "ss": st.session_state.get("saved_scripts", [])[-15:],
            "fv": st.session_state.get("favorites", [])[-10:],
            "ch": st.session_state.get("chat_history", [])[-30:],
            "th": st.session_state.get("theme", "dark"),
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
                st.session_state.theme = data.get("th", "dark")
                
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
    keys = list(st.session_state.keys())
    for key in keys:
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
    "theme": "dark",
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

# ====== SECRETS ======
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    MASTER_CODE = st.secrets.get("MASTER_CODE", "GuizinhsDono")
except:
    st.error("❌ Configure os secrets!")
    st.code('GEMINI_API_KEY = "sua_chave"\nMASTER_CODE = "seu_codigo"')
    st.stop()

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
    elif 'using unityengine' in code_lower or 'monobehaviour' in code_lower:
        return 'csharp', '.cs'
    elif '<!doctype' in code_lower or '<html' in code_lower:
        return 'html', '.html'
    elif 'gg.' in code_lower and ('function' in code_lower or 'local' in code_lower):
        return 'lua', '.lua'
    elif 'def ' in code_lower and 'import' in code_lower:
        return 'python', '.py'
    elif 'function' in code_lower or 'const ' in code_lower or 'let ' in code_lower:
        return 'javascript', '.js'
    elif 'select' in code_lower and 'from' in code_lower:
        return 'sql', '.sql'
    elif '@bot' in code_lower or 'discord' in code_lower:
        return 'python', '.py'
    return 'text', '.txt'

# ====== TEMPLATES EXPANDIDOS ======
TEMPLATES = {
    "🎮 Jogos Android HTML5": {
        "Coletor de Moedas": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <title>Coletor de Moedas</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; touch-action: manipulation; user-select: none; }
        body { background: #1a1a2e; overflow: hidden; font-family: Arial, sans-serif; }
        canvas { display: block; }
        #ui { position: fixed; top: 15px; left: 15px; right: 15px; display: flex; justify-content: space-between; color: #fff; font-size: 20px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); z-index: 100; }
        #gameOver { position: fixed; inset: 0; background: rgba(0,0,0,0.9); display: none; flex-direction: column; align-items: center; justify-content: center; color: #fff; z-index: 200; }
        #gameOver.show { display: flex; }
        #gameOver h1 { font-size: 42px; color: #ffd700; margin-bottom: 20px; }
        #gameOver p { font-size: 22px; margin: 10px 0; }
        #gameOver button { margin-top: 30px; padding: 15px 50px; font-size: 20px; background: linear-gradient(135deg, #00ff88, #00cc6a); border: none; border-radius: 30px; color: #000; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <canvas id="game"></canvas>
    <div id="ui">
        <span>🪙 <span id="score">0</span></span>
        <span>⏱️ <span id="time">30</span>s</span>
        <span>🏆 <span id="high">0</span></span>
    </div>
    <div id="gameOver">
        <h1>🎮 Fim de Jogo!</h1>
        <p>Moedas: <span id="finalScore">0</span></p>
        <p>Recorde: <span id="finalHigh">0</span></p>
        <button onclick="startGame()">🔄 Jogar Novamente</button>
    </div>
    <script>
        const canvas = document.getElementById('game');
        const ctx = canvas.getContext('2d');
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);
        
        let score = 0, timeLeft = 30, gameRunning = false;
        let highScore = parseInt(localStorage.getItem('coinHighScore') || '0');
        document.getElementById('high').textContent = highScore;
        
        const player = { x: 0, y: 0, size: 50, color: '#00ff88' };
        let coins = [];
        let particles = [];
        
        function spawnCoin() {
            coins.push({
                x: Math.random() * (canvas.width - 40) + 20,
                y: Math.random() * (canvas.height - 150) + 80,
                size: 25,
                wobble: Math.random() * Math.PI * 2
            });
        }
        
        function createParticles(x, y, color) {
            for (let i = 0; i < 8; i++) {
                particles.push({
                    x, y,
                    vx: (Math.random() - 0.5) * 8,
                    vy: (Math.random() - 0.5) * 8,
                    life: 20,
                    color
                });
            }
        }
        
        function startGame() {
            score = 0;
            timeLeft = 30;
            coins = [];
            particles = [];
            gameRunning = true;
            document.getElementById('gameOver').classList.remove('show');
            for (let i = 0; i < 5; i++) spawnCoin();
        }
        
        function endGame() {
            gameRunning = false;
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('coinHighScore', highScore);
            }
            document.getElementById('finalScore').textContent = score;
            document.getElementById('finalHigh').textContent = highScore;
            document.getElementById('high').textContent = highScore;
            document.getElementById('gameOver').classList.add('show');
        }
        
        function update() {
            if (!gameRunning) return;
            
            // Verificar colisão com moedas
            for (let i = coins.length - 1; i >= 0; i--) {
                const c = coins[i];
                const dist = Math.hypot(player.x - c.x, player.y - c.y);
                if (dist < player.size/2 + c.size) {
                    coins.splice(i, 1);
                    score++;
                    document.getElementById('score').textContent = score;
                    createParticles(c.x, c.y, '#ffd700');
                    spawnCoin();
                }
            }
            
            // Atualizar partículas
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.life--;
                if (p.life <= 0) particles.splice(i, 1);
            }
        }
        
        function draw() {
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Grid
            ctx.strokeStyle = 'rgba(255,255,255,0.03)';
            for (let x = 0; x < canvas.width; x += 50) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }
            
            // Moedas
            const time = Date.now() / 200;
            coins.forEach(c => {
                const wobble = Math.sin(time + c.wobble) * 3;
                ctx.fillStyle = '#ffd700';
                ctx.beginPath();
                ctx.arc(c.x, c.y + wobble, c.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.arc(c.x - 8, c.y + wobble - 8, 6, 0, Math.PI * 2);
                ctx.fill();
            });
            
            // Partículas
            particles.forEach(p => {
                ctx.globalAlpha = p.life / 20;
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1;
            
            // Player
            ctx.fillStyle = player.color;
            ctx.beginPath();
            ctx.arc(player.x, player.y, player.size/2, 0, Math.PI * 2);
            ctx.fill();
            
            // Olhos
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(player.x - 10, player.y - 5, 8, 0, Math.PI * 2);
            ctx.arc(player.x + 10, player.y - 5, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(player.x - 8, player.y - 3, 4, 0, Math.PI * 2);
            ctx.arc(player.x + 12, player.y - 3, 4, 0, Math.PI * 2);
            ctx.fill();
        }
        
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // Timer
        setInterval(() => {
            if (gameRunning && timeLeft > 0) {
                timeLeft--;
                document.getElementById('time').textContent = timeLeft;
                if (timeLeft <= 0) endGame();
            }
        }, 1000);
        
        // Controles
        function movePlayer(x, y) {
            player.x = Math.max(player.size/2, Math.min(canvas.width - player.size/2, x));
            player.y = Math.max(player.size/2 + 60, Math.min(canvas.height - player.size/2, y));
        }
        
        canvas.addEventListener('touchstart', e => {
            e.preventDefault();
            if (!gameRunning) { startGame(); return; }
            movePlayer(e.touches[0].clientX, e.touches[0].clientY);
        });
        
        canvas.addEventListener('touchmove', e => {
            e.preventDefault();
            if (gameRunning) movePlayer(e.touches[0].clientX, e.touches[0].clientY);
        });
        
        canvas.addEventListener('mousemove', e => {
            if (gameRunning) movePlayer(e.clientX, e.clientY);
        });
        
        canvas.addEventListener('click', () => {
            if (!gameRunning) startGame();
        });
        
        // Inicializar
        player.x = canvas.width / 2;
        player.y = canvas.height / 2;
        gameLoop();
    </script>
</body>
</html>""",

        "Endless Runner Completo": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <title>Endless Runner</title>
    <style>
        * { margin: 0; padding: 0; touch-action: manipulation; user-select: none; }
        body { background: #000; overflow: hidden; }
        canvas { display: block; }
        #hud { position: fixed; top: 15px; left: 15px; right: 15px; display: flex; justify-content: space-between; color: #fff; font: bold 22px Arial; text-shadow: 2px 2px 4px #000; z-index: 10; }
        #pause { position: fixed; top: 15px; right: 15px; width: 50px; height: 50px; background: rgba(255,255,255,0.2); border: none; border-radius: 50%; color: #fff; font-size: 24px; z-index: 10; }
        #overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; z-index: 100; }
        #overlay.hidden { display: none; }
        #overlay h1 { font-size: 48px; margin-bottom: 20px; }
        #overlay p { font-size: 24px; margin: 10px 0; }
        #overlay button { margin-top: 30px; padding: 18px 60px; font-size: 22px; background: linear-gradient(135deg, #00ff88, #00cc6a); border: none; border-radius: 35px; font-weight: bold; }
        .tap-hint { position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%); color: rgba(255,255,255,0.7); font: 18px Arial; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.3; } }
    </style>
</head>
<body>
    <canvas id="c"></canvas>
    <div id="hud">
        <span>🏃 <span id="score">0</span>m</span>
        <span>🏆 <span id="best">0</span>m</span>
    </div>
    <button id="pause" onclick="togglePause()">⏸️</button>
    <div class="tap-hint" id="hint">👆 Toque para pular</div>
    
    <div id="overlay">
        <h1 id="overlayTitle">🎮 Endless Runner</h1>
        <p id="overlayText">Toque para começar!</p>
        <button id="overlayBtn" onclick="startGame()">▶️ JOGAR</button>
    </div>
    
    <script>
        const c = document.getElementById('c'), ctx = c.getContext('2d');
        c.width = innerWidth; c.height = innerHeight;
        window.addEventListener('resize', () => { c.width = innerWidth; c.height = innerHeight; });
        
        let score = 0, speed = 6, playing = false, paused = false;
        let best = parseInt(localStorage.getItem('runnerBest') || '0');
        document.getElementById('best').textContent = best;
        
        const ground = c.height - 100;
        const player = { x: 80, y: ground - 60, w: 50, h: 60, vy: 0, jumping: false, doubleJump: false };
        
        let obstacles = [];
        let clouds = [];
        let particles = [];
        let bgX = 0;
        let frame = 0;
        
        // Gerar nuvens iniciais
        for (let i = 0; i < 5; i++) {
            clouds.push({ x: Math.random() * c.width, y: Math.random() * 200 + 50, size: Math.random() * 40 + 30 });
        }
        
        function addObstacle() {
            const types = [
                { w: 30, h: 50, color: '#e74c3c' },
                { w: 50, h: 35, color: '#9b59b6' },
                { w: 25, h: 70, color: '#e67e22' },
            ];
            const t = types[Math.floor(Math.random() * types.length)];
            obstacles.push({ x: c.width + 50, y: ground - t.h, ...t });
        }
        
        function addParticle(x, y, color) {
            for (let i = 0; i < 5; i++) {
                particles.push({
                    x, y,
                    vx: (Math.random() - 0.5) * 6,
                    vy: Math.random() * -8,
                    life: 25,
                    color
                });
            }
        }
        
        function jump() {
            if (paused || !playing) return;
            
            if (!player.jumping) {
                player.vy = -18;
                player.jumping = true;
                addParticle(player.x + player.w/2, player.y + player.h, '#00ff88');
            } else if (!player.doubleJump) {
                player.vy = -15;
                player.doubleJump = true;
                addParticle(player.x + player.w/2, player.y + player.h, '#ffd700');
            }
        }
        
        function startGame() {
            score = 0;
            speed = 6;
            obstacles = [];
            particles = [];
            player.y = ground - player.h;
            player.vy = 0;
            player.jumping = false;
            player.doubleJump = false;
            playing = true;
            paused = false;
            document.getElementById('overlay').classList.add('hidden');
            document.getElementById('hint').style.display = 'block';
        }
        
        function gameOver() {
            playing = false;
            if (score > best) {
                best = score;
                localStorage.setItem('runnerBest', best);
                document.getElementById('best').textContent = best;
            }
            document.getElementById('overlayTitle').textContent = '💀 Game Over';
            document.getElementById('overlayText').innerHTML = `Distância: ${score}m<br>Recorde: ${best}m`;
            document.getElementById('overlayBtn').textContent = '🔄 Tentar Novamente';
            document.getElementById('overlay').classList.remove('hidden');
            document.getElementById('hint').style.display = 'none';
        }
        
        function togglePause() {
            if (!playing) return;
            paused = !paused;
            document.getElementById('pause').textContent = paused ? '▶️' : '⏸️';
        }
        
        function update() {
            if (!playing || paused) return;
            
            frame++;
            
            // Física do player
            player.vy += 0.9;
            player.y += player.vy;
            
            if (player.y + player.h >= ground) {
                player.y = ground - player.h;
                player.vy = 0;
                player.jumping = false;
                player.doubleJump = false;
            }
            
            // Spawnar obstáculos
            if (frame % Math.max(60, 100 - score/2) === 0) {
                addObstacle();
            }
            
            // Atualizar obstáculos
            for (let i = obstacles.length - 1; i >= 0; i--) {
                obstacles[i].x -= speed;
                
                // Colisão
                if (player.x < obstacles[i].x + obstacles[i].w &&
                    player.x + player.w > obstacles[i].x &&
                    player.y < obstacles[i].y + obstacles[i].h &&
                    player.y + player.h > obstacles[i].y) {
                    addParticle(player.x + player.w/2, player.y + player.h/2, '#ff0000');
                    gameOver();
                    return;
                }
                
                // Remover fora da tela
                if (obstacles[i].x + obstacles[i].w < 0) {
                    obstacles.splice(i, 1);
                    score++;
                    document.getElementById('score').textContent = score;
                    
                    // Aumentar velocidade
                    if (score % 10 === 0) speed += 0.3;
                }
            }
            
            // Atualizar nuvens
            clouds.forEach(cloud => {
                cloud.x -= speed * 0.2;
                if (cloud.x + cloud.size < 0) {
                    cloud.x = c.width + cloud.size;
                    cloud.y = Math.random() * 200 + 50;
                }
            });
            
            // Atualizar partículas
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].x += particles[i].vx;
                particles[i].y += particles[i].vy;
                particles[i].vy += 0.3;
                particles[i].life--;
                if (particles[i].life <= 0) particles.splice(i, 1);
            }
            
            bgX = (bgX + speed * 0.5) % 100;
        }
        
        function draw() {
            // Céu gradiente
            const grad = ctx.createLinearGradient(0, 0, 0, c.height);
            grad.addColorStop(0, '#1a1a2e');
            grad.addColorStop(1, '#16213e');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, c.width, c.height);
            
            // Estrelas/Grid
            ctx.strokeStyle = 'rgba(255,255,255,0.03)';
            for (let x = -bgX; x < c.width; x += 100) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, c.height);
                ctx.stroke();
            }
            
            // Nuvens
            ctx.fillStyle = 'rgba(255,255,255,0.1)';
            clouds.forEach(cloud => {
                ctx.beginPath();
                ctx.arc(cloud.x, cloud.y, cloud.size, 0, Math.PI * 2);
                ctx.arc(cloud.x + cloud.size * 0.5, cloud.y - cloud.size * 0.3, cloud.size * 0.7, 0, Math.PI * 2);
                ctx.arc(cloud.x - cloud.size * 0.5, cloud.y - cloud.size * 0.2, cloud.size * 0.6, 0, Math.PI * 2);
                ctx.fill();
            });
            
            // Chão
            ctx.fillStyle = '#2d3436';
            ctx.fillRect(0, ground, c.width, c.height - ground);
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(0, ground, c.width, 4);
            
            // Linhas do chão
            ctx.strokeStyle = 'rgba(0,255,136,0.3)';
            for (let x = -bgX * 2; x < c.width; x += 60) {
                ctx.beginPath();
                ctx.moveTo(x, ground + 20);
                ctx.lineTo(x + 40, ground + 20);
                ctx.stroke();
            }
            
            // Partículas
            particles.forEach(p => {
                ctx.globalAlpha = p.life / 25;
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1;
            
            // Player
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(player.x, player.y, player.w, player.h);
            
            // Olhos
            ctx.fillStyle = '#fff';
            ctx.fillRect(player.x + 12, player.y + 15, 10, 12);
            ctx.fillRect(player.x + 28, player.y + 15, 10, 12);
            ctx.fillStyle = '#000';
            ctx.fillRect(player.x + 17, player.y + 20, 4, 5);
            ctx.fillRect(player.x + 33, player.y + 20, 4, 5);
            
            // Boca
            ctx.fillStyle = '#000';
            ctx.fillRect(player.x + 15, player.y + 40, 20, 4);
            
            // Efeito de salto
            if (player.jumping) {
                ctx.fillStyle = 'rgba(0,255,136,0.3)';
                for (let i = 1; i <= 3; i++) {
                    ctx.fillRect(player.x - i * 10, player.y + i * 8, player.w, player.h);
                }
            }
            
            // Obstáculos
            obstacles.forEach(o => {
                ctx.fillStyle = o.color;
                ctx.fillRect(o.x, o.y, o.w, o.h);
                ctx.fillStyle = 'rgba(255,255,255,0.3)';
                ctx.fillRect(o.x, o.y, o.w, 4);
            });
            
            // Indicador de pulo duplo
            if (!player.doubleJump && player.jumping) {
                ctx.fillStyle = 'rgba(255,215,0,0.5)';
                ctx.beginPath();
                ctx.arc(player.x + player.w/2, player.y - 15, 8, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // Controles
        c.addEventListener('touchstart', e => { e.preventDefault(); jump(); });
        c.addEventListener('click', jump);
        document.addEventListener('keydown', e => { if (e.code === 'Space') { e.preventDefault(); jump(); } });
        
        gameLoop();
    </script>
</body>
</html>""",

        "Flappy Bird Clone": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Flappy Clone</title>
    <style>
        * { margin: 0; padding: 0; touch-action: manipulation; }
        body { background: #000; overflow: hidden; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        canvas { display: block; max-width: 100%; max-height: 100vh; }
    </style>
</head>
<body>
    <canvas id="game" width="400" height="600"></canvas>
    <script>
        const canvas = document.getElementById('game');
        const ctx = canvas.getContext('2d');
        
        let playing = false, score = 0, best = parseInt(localStorage.getItem('flappyBest') || '0');
        
        const bird = { x: 80, y: 250, vy: 0, size: 25 };
        let pipes = [];
        const gravity = 0.5, jump = -9, pipeGap = 150, pipeWidth = 60;
        
        function addPipe() {
            const minH = 80, maxH = canvas.height - pipeGap - 80;
            const h = Math.random() * (maxH - minH) + minH;
            pipes.push({ x: canvas.width, topH: h, passed: false });
        }
        
        function start() {
            playing = true;
            score = 0;
            bird.y = 250;
            bird.vy = 0;
            pipes = [];
            addPipe();
        }
        
        function flap() {
            if (!playing) { start(); return; }
            bird.vy = jump;
        }
        
        function update() {
            if (!playing) return;
            
            bird.vy += gravity;
            bird.y += bird.vy;
            
            // Colisão com bordas
            if (bird.y < 0 || bird.y + bird.size > canvas.height) {
                playing = false;
                if (score > best) { best = score; localStorage.setItem('flappyBest', best); }
            }
            
            // Spawnar tubos
            if (pipes.length === 0 || pipes[pipes.length - 1].x < canvas.width - 200) {
                addPipe();
            }
            
            // Atualizar tubos
            for (let i = pipes.length - 1; i >= 0; i--) {
                pipes[i].x -= 3;
                
                // Pontuação
                if (!pipes[i].passed && pipes[i].x + pipeWidth < bird.x) {
                    pipes[i].passed = true;
                    score++;
                }
                
                // Colisão
                if (bird.x + bird.size > pipes[i].x && bird.x < pipes[i].x + pipeWidth) {
                    if (bird.y < pipes[i].topH || bird.y + bird.size > pipes[i].topH + pipeGap) {
                        playing = false;
                        if (score > best) { best = score; localStorage.setItem('flappyBest', best); }
                    }
                }
                
                // Remover
                if (pipes[i].x + pipeWidth < 0) pipes.splice(i, 1);
            }
        }
        
        function draw() {
            // Fundo
            const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
            grad.addColorStop(0, '#87CEEB');
            grad.addColorStop(1, '#98D8C8');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Tubos
            ctx.fillStyle = '#2ecc71';
            pipes.forEach(p => {
                // Tubo superior
                ctx.fillRect(p.x, 0, pipeWidth, p.topH);
                ctx.fillRect(p.x - 5, p.topH - 30, pipeWidth + 10, 30);
                
                // Tubo inferior
                const bottomY = p.topH + pipeGap;
                ctx.fillRect(p.x, bottomY, pipeWidth, canvas.height - bottomY);
                ctx.fillRect(p.x - 5, bottomY, pipeWidth + 10, 30);
            });
            
            // Pássaro
            ctx.fillStyle = '#f1c40f';
            ctx.beginPath();
            ctx.arc(bird.x + bird.size/2, bird.y + bird.size/2, bird.size/2, 0, Math.PI * 2);
            ctx.fill();
            
            // Olho
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(bird.x + bird.size/2 + 5, bird.y + bird.size/2 - 3, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(bird.x + bird.size/2 + 7, bird.y + bird.size/2 - 3, 4, 0, Math.PI * 2);
            ctx.fill();
            
            // Bico
            ctx.fillStyle = '#e67e22';
            ctx.beginPath();
            ctx.moveTo(bird.x + bird.size, bird.y + bird.size/2);
            ctx.lineTo(bird.x + bird.size + 12, bird.y + bird.size/2 + 5);
            ctx.lineTo(bird.x + bird.size, bird.y + bird.size/2 + 10);
            ctx.fill();
            
            // Score
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 36px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(score, canvas.width/2, 60);
            
            // Game Over
            if (!playing) {
                ctx.fillStyle = 'rgba(0,0,0,0.7)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 42px Arial';
                ctx.fillText('Game Over', canvas.width/2, canvas.height/2 - 40);
                ctx.font = '28px Arial';
                ctx.fillText(`Score: ${score}`, canvas.width/2, canvas.height/2 + 10);
                ctx.fillText(`Best: ${best}`, canvas.width/2, canvas.height/2 + 50);
                ctx.font = '20px Arial';
                ctx.fillText('Tap to play', canvas.width/2, canvas.height/2 + 100);
            }
        }
        
        function loop() { update(); draw(); requestAnimationFrame(loop); }
        
        canvas.addEventListener('touchstart', e => { e.preventDefault(); flap(); });
        canvas.addEventListener('click', flap);
        
        loop();
    </script>
</body>
</html>"""
    },
    
    "🛡️ Game Guardian": {
        "Script Completo": """--[[
    ╔══════════════════════════════════════╗
    ║     Game Guardian Script Pro         ║
    ║     Versão: 2.0                      ║
    ║     Autor: ScriptMaster AI           ║
    ╚══════════════════════════════════════╝
    
    ⚠️ APENAS PARA FINS EDUCACIONAIS!
]]

gg.setVisible(false)
gg.toast("🎮 Script carregado!")

-- Configurações
local config = {
    version = "2.0",
    autoRefresh = false,
    safeMode = true
}

local running = true

-- ═══════════════════════════════════════
-- FUNÇÕES UTILITÁRIAS
-- ═══════════════════════════════════════

local function toast(msg)
    gg.toast(msg)
end

local function alert(msg, title)
    title = title or "Info"
    gg.alert(msg, "OK", nil, title)
end

local function confirm(msg)
    return gg.alert(msg, "Sim", "Não") == 1
end

local function input(prompts, defaults, types)
    return gg.prompt(prompts, defaults, types)
end

-- ═══════════════════════════════════════
-- FUNÇÕES DE MEMÓRIA
-- ═══════════════════════════════════════

local function searchValue(value, dataType, ranges)
    dataType = dataType or gg.TYPE_DWORD
    ranges = ranges or gg.REGION_ANONYMOUS
    
    gg.clearResults()
    gg.setRanges(ranges)
    gg.searchNumber(value, dataType)
    
    return gg.getResultsCount()
end

local function editResults(newValue, maxResults)
    maxResults = maxResults or 1000
    local count = gg.getResultsCount()
    
    if count == 0 then
        toast("❌ Nenhum resultado!")
        return false
    end
    
    if count > maxResults then
        toast("⚠️ Muitos resultados: " .. count)
        return false
    end
    
    local results = gg.getResults(count)
    for i, v in ipairs(results) do
        results[i].value = newValue
    end
    gg.setValues(results)
    
    toast("✅ " .. count .. " valores alterados!")
    return true
end

local function freezeResults()
    local count = gg.getResultsCount()
    if count == 0 then
        toast("❌ Nenhum resultado!")
        return
    end
    
    local results = gg.getResults(count)
    for i, v in ipairs(results) do
        results[i].freeze = true
    end
    gg.addListItems(results)
    toast("❄️ " .. count .. " valores congelados!")
end

local function unfreezeAll()
    local list = gg.getListItems()
    if #list == 0 then
        toast("Lista vazia!")
        return
    end
    
    for i, v in ipairs(list) do
        list[i].freeze = false
    end
    gg.setValues(list)
    gg.clearList()
    toast("🔥 Valores descongelados!")
end

-- ═══════════════════════════════════════
-- FUNÇÕES DE HACK
-- ═══════════════════════════════════════

local function hackGenerico()
    local tipos = {"Dinheiro/Gold", "Gemas/Diamantes", "Energia", "Vida/HP", "Ataque", "Defesa", "Outro"}
    local choice = gg.choice(tipos, nil, "📦 Tipo de Valor")
    if not choice then return end
    
    local nome = tipos[choice]
    
    local inp = input(
        {nome .. " atual:", "Novo valor:"},
        {"0", "999999"},
        {"number", "number"}
    )
    
    if not inp then return end
    
    local oldVal = tonumber(inp[1])
    local newVal = tonumber(inp[2])
    
    -- Tentar como DWORD primeiro
    toast("🔍 Buscando como INT...")
    local count = searchValue(oldVal, gg.TYPE_DWORD, gg.REGION_ANONYMOUS | gg.REGION_OTHER)
    
    if count > 0 and count < 500 then
        editResults(newVal)
    elseif count == 0 or count >= 500 then
        -- Tentar como FLOAT
        toast("🔍 Tentando como FLOAT...")
        count = searchValue(oldVal, gg.TYPE_FLOAT, gg.REGION_ANONYMOUS | gg.REGION_OTHER)
        
        if count > 0 and count < 500 then
            editResults(newVal)
        else
            toast("❌ Não encontrado ou muitos resultados")
        end
    end
end

local function speedHack()
    local speeds = {0.25, 0.5, 1, 1.5, 2, 3, 5, 10}
    local labels = {"🐌 0.25x", "🐢 0.5x", "⏺️ 1x Normal", "🏃 1.5x", "🚀 2x", "⚡ 3x", "💨 5x", "🔥 10x"}
    
    local choice = gg.choice(labels, nil, "⚡ Velocidade do Jogo")
    if choice then
        gg.setSpeed(speeds[choice])
        toast("Velocidade: " .. labels[choice])
    end
end

local function buscaAvancada()
    local menu = gg.choice({
        "🔍 Busca Simples",
        "📊 Busca por Faixa",
        "🔗 Busca por Grupo",
        "🎯 Refinar Busca",
        "✏️ Editar Resultados",
        "❄️ Congelar Resultados",
        "🔥 Descongelar Tudo",
        "🗑️ Limpar Resultados"
    }, nil, "🔍 Busca Avançada")
    
    if menu == 1 then
        local inp = input(
            {"Valor:", "Tipo (1=INT, 2=FLOAT, 3=DOUBLE):"},
            {"0", "1"},
            {"text", "number"}
        )
        if inp then
            local types = {gg.TYPE_DWORD, gg.TYPE_FLOAT, gg.TYPE_DOUBLE}
            local count = searchValue(inp[1], types[tonumber(inp[2])] or gg.TYPE_DWORD, gg.REGION_ANONYMOUS | gg.REGION_OTHER)
            toast("Encontrados: " .. count)
        end
        
    elseif menu == 2 then
        local inp = input({"Mínimo:", "Máximo:"}, {"0", "1000"}, {"number", "number"})
        if inp then
            gg.clearResults()
            gg.setRanges(gg.REGION_ANONYMOUS)
            gg.searchNumber(inp[1] .. "~" .. inp[2], gg.TYPE_DWORD)
            toast("Encontrados: " .. gg.getResultsCount())
        end
        
    elseif menu == 3 then
        local inp = input({"Valores (separados por ';'):"}, {"100;200;300"}, {"text"})
        if inp then
            gg.clearResults()
            gg.setRanges(gg.REGION_ANONYMOUS)
            gg.searchNumber(inp[1], gg.TYPE_DWORD)
            toast("Grupos: " .. gg.getResultsCount())
        end
        
    elseif menu == 4 then
        local inp = input({"Novo valor para refinar:"}, {"0"}, {"text"})
        if inp then
            gg.refineNumber(inp[1], gg.TYPE_DWORD)
            toast("Refinado: " .. gg.getResultsCount())
        end
        
    elseif menu == 5 then
        local count = gg.getResultsCount()
        if count == 0 then
            toast("Faça uma busca primeiro!")
        else
            local inp = input({"Novo valor:"}, {"999999"}, {"text"})
            if inp then
                editResults(inp[1])
            end
        end
        
    elseif menu == 6 then
        freezeResults()
        
    elseif menu == 7 then
        unfreezeAll()
        
    elseif menu == 8 then
        gg.clearResults()
        toast("🗑️ Resultados limpos!")
    end
end

local function hackRapido()
    local hacks = {
        "💰 999999 Dinheiro",
        "💎 999999 Gemas",
        "❤️ 999999 Vida",
        "⚔️ 999999 Ataque",
        "🛡️ 999999 Defesa"
    }
    
    local choice = gg.choice(hacks, nil, "⚡ Hack Rápido")
    if not choice then return end
    
    local inp = input({"Valor atual:"}, {"0"}, {"number"})
    if not inp then return end
    
    local oldVal = tonumber(inp[1])
    
    -- Buscar e editar
    gg.clearResults()
    gg.setRanges(gg.REGION_ANONYMOUS | gg.REGION_OTHER)
    gg.searchNumber(oldVal, gg.TYPE_DWORD)
    
    local count = gg.getResultsCount()
    if count > 0 and count < 200 then
        local results = gg.getResults(count)
        for i, v in ipairs(results) do
            results[i].value = 999999
        end
        gg.setValues(results)
        toast("✅ Hack aplicado!")
    else
        -- Tentar FLOAT
        gg.clearResults()
        gg.searchNumber(oldVal, gg.TYPE_FLOAT)
        count = gg.getResultsCount()
        if count > 0 and count < 200 then
            local results = gg.getResults(count)
            for i, v in ipairs(results) do
                results[i].value = 999999
            end
            gg.setValues(results)
            toast("✅ Hack aplicado!")
        else
            toast("❌ Não encontrado")
        end
    end
end

-- ═══════════════════════════════════════
-- MENU PRINCIPAL
-- ═══════════════════════════════════════

local function mainMenu()
    local menu = gg.choice({
        "💰 Hack Genérico",
        "⚡ Hack Rápido (999999)",
        "🚀 Speed Hack",
        "🔍 Busca Avançada",
        "🧹 Limpar Tudo",
        "⚙️ Configurações",
        "ℹ️ Sobre",
        "❌ Sair"
    }, nil, "🎮 ScriptMaster v" .. config.version)
    
    if menu == 1 then
        hackGenerico()
        
    elseif menu == 2 then
        hackRapido()
        
    elseif menu == 3 then
        speedHack()
        
    elseif menu == 4 then
        buscaAvancada()
        
    elseif menu == 5 then
        gg.clearResults()
        gg.clearList()
        gg.setSpeed(1)
        toast("🧹 Tudo limpo!")
        
    elseif menu == 6 then
        local configMenu = gg.choice({
            "Safe Mode: " .. (config.safeMode and "ON" or "OFF"),
            "Reset Speed"
        }, nil, "⚙️ Configurações")
        
        if configMenu == 1 then
            config.safeMode = not config.safeMode
            toast("Safe Mode: " .. (config.safeMode and "ON" or "OFF"))
        elseif configMenu == 2 then
            gg.setSpeed(1)
            toast("Velocidade resetada!")
        end
        
    elseif menu == 7 then
        alert(
            "📱 ScriptMaster GG\\n" ..
            "📌 Versão: " .. config.version .. "\\n\\n" ..
            "🛠️ Criado com ScriptMaster AI\\n\\n" ..
            "⚠️ Use com responsabilidade!\\n" ..
            "Apenas para fins educacionais."
        , "ℹ️ Sobre")
        
    elseif menu == 8 then
        if confirm("Deseja realmente sair?") then
            running = false
            gg.setSpeed(1)
            gg.clearResults()
            gg.clearList()
            toast("👋 Até logo!")
        end
    end
end

-- ═══════════════════════════════════════
-- LOOP PRINCIPAL
-- ═══════════════════════════════════════

toast("✅ Script pronto! Abra o menu do GG.")

while running do
    if gg.isVisible() then
        gg.setVisible(false)
        mainMenu()
    end
    gg.sleep(100)
end

os.exit()"""
    },
    
    "🎮 Godot 4.x": {
        "Player 2D Avançado": """extends CharacterBody2D
## Player 2D Completo - Godot 4.x
## Com dash, pulo duplo e wall jump

# === Exportações ===
@export_group("Movimento")
@export var speed: float = 300.0
@export var acceleration: float = 2000.0
@export var friction: float = 1500.0

@export_group("Pulo")
@export var jump_velocity: float = -450.0
@export var max_jumps: int = 2
@export var coyote_time: float = 0.15
@export var jump_buffer_time: float = 0.1

@export_group("Dash")
@export var dash_speed: float = 600.0
@export var dash_duration: float = 0.15
@export var dash_cooldown: float = 0.5

# === Variáveis ===
var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")
var jumps_remaining: int = 0
var coyote_timer: float = 0.0
var jump_buffer_timer: float = 0.0
var is_dashing: bool = false
var dash_timer: float = 0.0
var dash_cooldown_timer: float = 0.0
var dash_direction: Vector2 = Vector2.ZERO
var facing: int = 1

# === Referências ===
@onready var sprite = $AnimatedSprite2D
@onready var dash_particles = $DashParticles

# === Signals ===
signal jumped
signal dashed
signal landed

func _ready():
    jumps_remaining = max_jumps

func _physics_process(delta):
    handle_timers(delta)
    
    if is_dashing:
        handle_dash(delta)
    else:
        handle_gravity(delta)
        handle_jump()
        handle_movement(delta)
        handle_dash_input()
    
    update_animation()
    move_and_slide()

func handle_timers(delta):
    # Coyote time
    if is_on_floor():
        coyote_timer = coyote_time
        jumps_remaining = max_jumps
    else:
        coyote_timer -= delta
    
    # Jump buffer
    if Input.is_action_just_pressed("jump"):
        jump_buffer_timer = jump_buffer_time
    else:
        jump_buffer_timer -= delta
    
    # Dash cooldown
    if dash_cooldown_timer > 0:
        dash_cooldown_timer -= delta

func handle_gravity(delta):
    if not is_on_floor():
        velocity.y += gravity * delta

func handle_jump():
    var can_jump = is_on_floor() or coyote_timer > 0 or jumps_remaining > 0
    var wants_jump = Input.is_action_just_pressed("jump") or jump_buffer_timer > 0
    
    if wants_jump and can_jump:
        velocity.y = jump_velocity
        jumps_remaining -= 1
        coyote_timer = 0
        jump_buffer_timer = 0
        emit_signal("jumped")
    
    # Corte do pulo
    if Input.is_action_just_released("jump") and velocity.y < 0:
        velocity.y *= 0.5

func handle_movement(delta):
    var direction = Input.get_axis("move_left", "move_right")
    
    if direction != 0:
        velocity.x = move_toward(velocity.x, direction * speed, acceleration * delta)
        facing = sign(direction) as int
        sprite.flip_h = direction < 0
    else:
        velocity.x = move_toward(velocity.x, 0, friction * delta)

func handle_dash_input():
    if Input.is_action_just_pressed("dash") and dash_cooldown_timer <= 0:
        start_dash()

func start_dash():
    is_dashing = true
    dash_timer = dash_duration
    dash_direction = Vector2(facing, 0)
    
    var input_dir = Input.get_vector("move_left", "move_right", "move_up", "move_down")
    if input_dir != Vector2.ZERO:
        dash_direction = input_dir.normalized()
    
    if dash_particles:
        dash_particles.emitting = true
    
    emit_signal("dashed")

func handle_dash(delta):
    velocity = dash_direction * dash_speed
    dash_timer -= delta
    
    if dash_timer <= 0:
        is_dashing = false
        dash_cooldown_timer = dash_cooldown
        if dash_particles:
            dash_particles.emitting = false

func update_animation():
    if is_dashing:
        sprite.play("dash")
    elif not is_on_floor():
        sprite.play("jump" if velocity.y < 0 else "fall")
    elif abs(velocity.x) > 10:
        sprite.play("run")
    else:
        sprite.play("idle")

func take_damage(amount: int, knockback: Vector2 = Vector2.ZERO):
    velocity = knockback
    sprite.play("hurt")
    # Adicione lógica de dano aqui
""",

        "Sistema de Inventário": """extends Node
class_name InventorySystem
## Sistema de Inventário para Godot 4.x

signal item_added(item_id: String, quantity: int)
signal item_removed(item_id: String, quantity: int)
signal item_used(item_id: String)
signal inventory_full
signal inventory_changed

@export var max_slots: int = 20
@export var max_stack: int = 99

var items: Dictionary = {}

func add_item(item_id: String, quantity: int = 1) -> int:
    \"\"\"Adiciona item. Retorna quantidade não adicionada.\"\"\"
    var remaining = quantity
    
    # Se já tem o item, adiciona ao stack
    if items.has(item_id):
        var space = max_stack - items[item_id]
        var to_add = min(remaining, space)
        items[item_id] += to_add
        remaining -= to_add
        
        if to_add > 0:
            emit_signal("item_added", item_id, to_add)
    
    # Se ainda sobrou e tem espaço
    while remaining > 0 and items.size() < max_slots:
        if not items.has(item_id):
            var to_add = min(remaining, max_stack)
            items[item_id] = to_add
            remaining -= to_add
            emit_signal("item_added", item_id, to_add)
        else:
            break
    
    if remaining > 0:
        emit_signal("inventory_full")
    
    emit_signal("inventory_changed")
    return remaining

func remove_item(item_id: String, quantity: int = 1) -> bool:
    \"\"\"Remove item. Retorna true se conseguiu.\"\"\"
    if not has_item(item_id, quantity):
        return false
    
    items[item_id] -= quantity
    
    if items[item_id] <= 0:
        items.erase(item_id)
    
    emit_signal("item_removed", item_id, quantity)
    emit_signal("inventory_changed")
    return true

func use_item(item_id: String) -> bool:
    \"\"\"Usa um item.\"\"\"
    if not has_item(item_id):
        return false
    
    emit_signal("item_used", item_id)
    remove_item(item_id, 1)
    return true

func has_item(item_id: String, quantity: int = 1) -> bool:
    return items.get(item_id, 0) >= quantity

func get_quantity(item_id: String) -> int:
    return items.get(item_id, 0)

func get_all_items() -> Dictionary:
    return items.duplicate()

func clear():
    items.clear()
    emit_signal("inventory_changed")

func is_full() -> bool:
    return items.size() >= max_slots

func get_used_slots() -> int:
    return items.size()

func get_free_slots() -> int:
    return max_slots - items.size()

# Salvar/Carregar
func save_data() -> Dictionary:
    return {"items": items.duplicate()}

func load_data(data: Dictionary):
    items = data.get("items", {}).duplicate()
    emit_signal("inventory_changed")
"""
    },
    
    "🤖 Discord Bot": {
        "Bot Completo": """import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from datetime import datetime
import json
import os

# Configuração
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Banco de dados simples
DB_FILE = "bot_data.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"users": {}, "settings": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

db = load_db()

# ═══════════════════════════════════════
# EVENTOS
# ═══════════════════════════════════════

@bot.event
async def on_ready():
    print(f"✅ {bot.user} está online!")
    print(f"📊 Servidores: {len(bot.guilds)}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidores | /help"
        )
    )
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos sincronizados")
    except Exception as e:
        print(f"❌ Erro: {e}")

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title="👋 Bem-vindo!",
            description=f"Olá {member.mention}!\\nBem-vindo ao **{member.guild.name}**!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📅 Conta", value=member.created_at.strftime("%d/%m/%Y"))
        embed.add_field(name="👥 Membro #", value=str(member.guild.member_count))
        await channel.send(embed=embed)

# ═══════════════════════════════════════
# COMANDOS BÁSICOS
# ═══════════════════════════════════════

@bot.tree.command(name="ping", description="Mostra a latência do bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: **{latency}ms**",
        color=discord.Color.green() if latency < 100 else discord.Color.yellow()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="Mostra o avatar de um usuário")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"Avatar de {user.name}", color=user.color)
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Informações do servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.blue())
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="👑 Dono", value=guild.owner.mention if guild.owner else "N/A")
    embed.add_field(name="👥 Membros", value=guild.member_count)
    embed.add_field(name="💬 Canais", value=len(guild.channels))
    embed.add_field(name="🎭 Cargos", value=len(guild.roles))
    embed.add_field(name="📅 Criado", value=guild.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="🔒 Verificação", value=str(guild.verification_level))
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Informações de um usuário")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"👤 {user.name}", color=user.color)
    embed.set_thumbnail(url=user.display_avatar.url)
    
    embed.add_field(name="🆔 ID", value=user.id)
    embed.add_field(name="📛 Nick", value=user.display_name)
    embed.add_field(name="🤖 Bot?", value="Sim" if user.bot else "Não")
    embed.add_field(name="📅 Conta", value=user.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="📥 Entrou", value=user.joined_at.strftime("%d/%m/%Y") if user.joined_at else "N/A")
    embed.add_field(name="🎭 Cargos", value=len(user.roles) - 1)
    
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════
# ECONOMIA
# ═══════════════════════════════════════

def get_user_data(user_id):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"balance": 0, "daily": None}
        save_db(db)
    return db["users"][uid]

@bot.tree.command(name="balance", description="Ver seu saldo")
async def balance(interaction: discord.Interaction):
    data = get_user_data(interaction.user.id)
    embed = discord.Embed(
        title="💰 Seu Saldo",
        description=f"**{data['balance']:,}** moedas",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="Resgatar recompensa diária")
async def daily(interaction: discord.Interaction):
    data = get_user_data(interaction.user.id)
    
    today = datetime.now().strftime("%Y-%m-%d")
    if data.get("daily") == today:
        embed = discord.Embed(
            title="⏰ Já Resgatado",
            description="Volte amanhã!",
            color=discord.Color.red()
        )
    else:
        reward = 100
        data["balance"] += reward
        data["daily"] = today
        save_db(db)
        
        embed = discord.Embed(
            title="🎁 Recompensa Diária",
            description=f"Você ganhou **{reward}** moedas!\\nSaldo: **{data['balance']:,}**",
            color=discord.Color.green()
        )
    
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════
# MODERAÇÃO
# ═══════════════════════════════════════

@bot.tree.command(name="clear", description="Limpa mensagens")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount > 100:
        amount = 100
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ {len(deleted)} mensagens deletadas!", ephemeral=True)

@bot.tree.command(name="kick", description="Expulsa um membro")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Sem motivo"):
    await member.kick(reason=reason)
    embed = discord.Embed(
        title="👢 Membro Expulso",
        description=f"{member.mention} foi expulso!\\n**Motivo:** {reason}",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════
# DIVERSÃO
# ═══════════════════════════════════════

@bot.tree.command(name="coinflip", description="Cara ou coroa")
async def coinflip(interaction: discord.Interaction):
    import random
    result = random.choice(["🪙 Cara!", "🎭 Coroa!"])
    await interaction.response.send_message(result)

@bot.tree.command(name="dice", description="Rola um dado")
async def dice(interaction: discord.Interaction, sides: int = 6):
    import random
    result = random.randint(1, sides)
    await interaction.response.send_message(f"🎲 Você tirou **{result}**!")

# Rodar
# bot.run("SEU_TOKEN_AQUI")
"""
    },
    
    "🐍 Python": {
        "Web Scraper Avançado": """import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, delay=1):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        self.delay = delay
        self.data = []
    
    def fetch(self, url, retries=3):
        \"\"\"Faz requisição com retry\"\"\"
        for attempt in range(retries):
            try:
                logger.info(f"Buscando: {url}")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None
    
    def parse_html(self, html):
        \"\"\"Parse HTML\"\"\"
        return BeautifulSoup(html, 'html.parser')
    
    def scrape_page(self, url):
        \"\"\"Scrape uma página\"\"\"
        response = self.fetch(url)
        if not response:
            return None
        
        soup = self.parse_html(response.content)
        
        page_data = {
            'url': url,
            'title': soup.title.string.strip() if soup.title else '',
            'meta_description': '',
            'headings': [],
            'paragraphs': [],
            'links': [],
            'images': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Meta description
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            page_data['meta_description'] = meta.get('content', '')
        
        # Headings
        for tag in ['h1', 'h2', 'h3']:
            for h in soup.find_all(tag):
                page_data['headings'].append({
                    'tag': tag,
                    'text': h.get_text(strip=True)
                })
        
        # Parágrafos
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 50:
                page_data['paragraphs'].append(text[:500])
        
        # Links
        for a in soup.find_all('a', href=True):
            page_data['links'].append({
                'text': a.get_text(strip=True)[:100],
                'href': a['href']
            })
        
        # Imagens
        for img in soup.find_all('img', src=True):
            page_data['images'].append({
                'src': img['src'],
                'alt': img.get('alt', '')
            })
        
        return page_data
    
    def scrape_multiple(self, urls):
        \"\"\"Scrape múltiplas URLs\"\"\"
        for url in urls:
            data = self.scrape_page(url)
            if data:
                self.data.append(data)
            time.sleep(self.delay)
        
        return self.data
    
    def save_json(self, filename=None):
        \"\"\"Salva em JSON\"\"\"
        filename = filename or f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        logger.info(f"Salvo: {filename}")
        return filename
    
    def save_csv(self, filename=None):
        \"\"\"Salva em CSV\"\"\"
        filename = filename or f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Título', 'Descrição', 'Headings', 'Links', 'Timestamp'])
            
            for item in self.data:
                writer.writerow([
                    item['url'],
                    item['title'],
                    item['meta_description'],
                    len(item['headings']),
                    len(item['links']),
                    item['timestamp']
                ])
        
        logger.info(f"Salvo: {filename}")
        return filename
    
    def get_stats(self):
        \"\"\"Retorna estatísticas\"\"\"
        if not self.data:
            return "Nenhum dado coletado"
        
        total_links = sum(len(d['links']) for d in self.data)
        total_images = sum(len(d['images']) for d in self.data)
        
        return {
            'pages': len(self.data),
            'total_links': total_links,
            'total_images': total_images,
            'avg_links': total_links / len(self.data),
        }

# Exemplo de uso
if __name__ == "__main__":
    scraper = WebScraper(delay=1)
    
    urls = [
        "https://example.com",
        # Adicione mais URLs aqui
    ]
    
    scraper.scrape_multiple(urls)
    
    print("\\n📊 Estatísticas:")
    print(scraper.get_stats())
    
    scraper.save_json()
    scraper.save_csv()
""",

        "API Flask REST": """from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from functools import wraps
import json
import os
import hashlib
import secrets

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════
# BANCO DE DADOS (JSON simples)
# ═══════════════════════════════════════

DB_FILE = "api_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"users": [], "items": [], "tokens": {}}

def save_db():
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

db = load_db()

# ═══════════════════════════════════════
# AUTENTICAÇÃO
# ═══════════════════════════════════════

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return secrets.token_hex(32)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token or token not in db['tokens']:
            return jsonify({"error": "Não autorizado"}), 401
        return f(*args, **kwargs)
    return decorated

# ═══════════════════════════════════════
# ROTAS PRINCIPAIS
# ═══════════════════════════════════════

@app.route('/')
def home():
    return jsonify({
        "message": "API REST Flask",
        "version": "1.0",
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "items": "/api/items",
        }
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "users": len(db['users']),
        "items": len(db['items'])
    })

# ═══════════════════════════════════════
# AUTENTICAÇÃO
# ═══════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username e password obrigatórios"}), 400
    
    # Verificar se já existe
    if any(u['username'] == data['username'] for u in db['users']):
        return jsonify({"error": "Username já existe"}), 400
    
    user = {
        "id": len(db['users']) + 1,
        "username": data['username'],
        "password": hash_password(data['password']),
        "created_at": datetime.now().isoformat()
    }
    
    db['users'].append(user)
    save_db()
    
    return jsonify({"message": "Usuário criado!", "id": user['id']}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username e password obrigatórios"}), 400
    
    user = next((u for u in db['users'] 
                 if u['username'] == data['username'] 
                 and u['password'] == hash_password(data['password'])), None)
    
    if not user:
        return jsonify({"error": "Credenciais inválidas"}), 401
    
    token = generate_token()
    db['tokens'][token] = user['id']
    save_db()
    
    return jsonify({"token": token, "user_id": user['id']})

# ═══════════════════════════════════════
# CRUD USERS
# ═══════════════════════════════════════

@app.route('/api/users', methods=['GET'])
def get_users():
    users = [{k: v for k, v in u.items() if k != 'password'} for u in db['users']]
    return jsonify({"data": users, "total": len(users)})

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in db['users'] if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    return jsonify({k: v for k, v in user.items() if k != 'password'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    user = next((u for u in db['users'] if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    db['users'] = [u for u in db['users'] if u['id'] != user_id]
    save_db()
    
    return jsonify({"message": "Usuário deletado"})

# ═══════════════════════════════════════
# CRUD ITEMS
# ═══════════════════════════════════════

@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify({"data": db['items'], "total": len(db['items'])})

@app.route('/api/items', methods=['POST'])
@require_auth
def create_item():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({"error": "Nome obrigatório"}), 400
    
    item = {
        "id": len(db['items']) + 1,
        "name": data['name'],
        "description": data.get('description', ''),
        "price": data.get('price', 0),
        "created_at": datetime.now().isoformat()
    }
    
    db['items'].append(item)
    save_db()
    
    return jsonify({"message": "Item criado!", "data": item}), 201

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((i for i in db['items'] if i['id'] == item_id), None)
    if not item:
        return jsonify({"error": "Item não encontrado"}), 404
    return jsonify(item)

@app.route('/api/items/<int:item_id>', methods=['PUT'])
@require_auth
def update_item(item_id):
    item = next((i for i in db['items'] if i['id'] == item_id), None)
    if not item:
        return jsonify({"error": "Item não encontrado"}), 404
    
    data = request.get_json()
    if 'name' in data:
        item['name'] = data['name']
    if 'description' in data:
        item['description'] = data['description']
    if 'price' in data:
        item['price'] = data['price']
    
    item['updated_at'] = datetime.now().isoformat()
    save_db()
    
    return jsonify({"message": "Item atualizado!", "data": item})

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@require_auth
def delete_item(item_id):
    item = next((i for i in db['items'] if i['id'] == item_id), None)
    if not item:
        return jsonify({"error": "Item não encontrado"}), 404
    
    db['items'] = [i for i in db['items'] if i['id'] != item_id]
    save_db()
    
    return jsonify({"message": "Item deletado"})

# ═══════════════════════════════════════
# BUSCA
# ═══════════════════════════════════════

@app.route('/api/search')
def search():
    q = request.args.get('q', '').lower()
    
    if not q:
        return jsonify({"error": "Parâmetro 'q' obrigatório"}), 400
    
    users = [u for u in db['users'] if q in u['username'].lower()]
    items = [i for i in db['items'] if q in i['name'].lower()]
    
    return jsonify({
        "query": q,
        "users": [{k: v for k, v in u.items() if k != 'password'} for u in users],
        "items": items
    })

# ═══════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint não encontrado"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Erro interno"}), 500

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

if __name__ == '__main__':
    print("🚀 API rodando em http://localhost:5000")
    print("\\nEndpoints:")
    print("  POST /api/auth/register - Criar conta")
    print("  POST /api/auth/login - Login")
    print("  GET  /api/users - Listar usuários")
    print("  GET  /api/items - Listar items")
    print("  POST /api/items - Criar item (auth)")
    
    app.run(debug=True, port=5000)
"""
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
        username = st.text_input("👤 Seu nome", key=get_unique_key("login_user"))
        access_code = st.text_input("🎫 Código VIP (opcional)", type="password", key=get_unique_key("login_code"))
        remember = st.checkbox("🔒 Manter conectado", value=True, key=get_unique_key("remember"))
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 ENTRAR", use_container_width=True, type="primary", key=get_unique_key("btn_login")):
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
            if st.button("🆓 Modo Grátis", use_container_width=True, key=get_unique_key("btn_free")):
                st.session_state.authenticated = True
                st.session_state.username = username if username else "Visitante"
                if remember:
                    save_session()
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 Planos")
        
        st.markdown("""
        <div class="free-feature">
            <h4>🆓 GRATUITO</h4>
            <ul>
                <li>✅ 4 gerações/dia</li>
                <li>✅ 10 mensagens de chat/dia</li>
                <li>✅ Templates básicos</li>
                <li>✅ Download de código</li>
                <li>❌ Salvar scripts</li>
                <li>❌ Favoritos</li>
                <li>❌ Histórico persistente</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="vip-feature">
            <h4>👑 VIP</h4>
            <ul>
                <li>✅ Gerações ILIMITADAS</li>
                <li>✅ Chat ILIMITADO</li>
                <li>✅ TODOS os templates</li>
                <li>✅ Salvar até 15 scripts</li>
                <li>✅ 10 favoritos</li>
                <li>✅ Histórico salvo na nuvem</li>
                <li>✅ Suporte prioritário</li>
                <li>✅ Sem anúncios</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown(f"""
    <div class="welcome-box">
        <h3>👋 Olá, {st.session_state.username}!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Badge
    if st.session_state.is_master:
        st.markdown('<span class="master-badge">🔥 ADMIN</span>', unsafe_allow_html=True)
    elif is_vip():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<span class="vip-badge">👑 VIP - {dias}d</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="free-badge">🆓 Gratuito</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Contador de uso
    if is_vip():
        st.success("✨ Uso ILIMITADO!")
    else:
        can_gen, rem_gen = can_generate()
        can_ch, rem_ch = can_chat()
        
        st.markdown(f"""
        <div class="usage-box">
            <p style="margin:0;color:#fff;">⚡ Gerações: <strong>{st.session_state.usage_count}/{DAILY_LIMIT_FREE}</strong></p>
            <p style="margin:5px 0 0 0;color:#fff;">💬 Chat: <strong>{st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}</strong></p>
            <p style="margin:10px 0 0 0;font-size:12px;color:#94a3b8;">🔄 Renova à meia-noite</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not can_gen or not can_ch:
            st.warning("⚠️ Faça upgrade para VIP!")
    
    # Admin - Códigos VIP
    if st.session_state.is_master:
        st.markdown("---")
        with st.expander("🎫 Criar Código VIP"):
            new_code = st.text_input("Nome do código", key=get_unique_key("new_code"))
            code_days = st.selectbox("Duração", ["1 dia", "7 dias", "30 dias", "Ilimitado"], key=get_unique_key("code_days"))
            
            if st.button("✨ Criar Código", key=get_unique_key("btn_create_code")):
                if new_code and new_code not in st.session_state.created_codes:
                    days_map = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                    st.session_state.created_codes[new_code] = {
                        "days": days_map[code_days],
                        "used": False,
                        "created": datetime.now().isoformat()
                    }
                    st.success(f"✅ Código criado!")
                    st.code(new_code)
                elif new_code in st.session_state.created_codes:
                    st.error("Código já existe!")
        
        # Listar códigos
        if st.session_state.created_codes:
            with st.expander("📋 Códigos Criados"):
                for code, info in list(st.session_state.created_codes.items())[:10]:
                    status = "✅ Usado" if info.get("used") else "🎫 Ativo"
                    st.text(f"{status} | {code} | {info['days']}d")
    
    # Templates
    st.markdown("---")
    st.markdown("### 📚 Templates")
    
    for category, templates in TEMPLATES.items():
        with st.expander(category):
            for name, code in templates.items():
                btn_key = get_unique_key(f"tmpl_{name[:10]}")
                if st.button(f"📄 {name}", key=btn_key, use_container_width=True):
                    st.session_state.current_script = code
                    st.toast(f"✅ Template '{name}' carregado!")
                    st.rerun()
    
    # Sair
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True, key=get_unique_key("btn_logout")):
        clear_session()
        st.rerun()

# ====== ÁREA PRINCIPAL ======
st.markdown("""
<div class="header-premium">
    <h1>🎮 ScriptMaster AI Pro</h1>
    <p>Gerador de Scripts e Jogos com Inteligência Artificial</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 Gerar", "💬 Chat", "💻 Editor", "📚 Biblioteca", "📊 Stats"])

# ====== TAB 1: GERAR ======
with tab1:
    st.markdown("### 🎯 Descreva o que você quer criar")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_area(
            "📝 Descrição:",
            placeholder="Ex: Crie um jogo de plataforma 2D em HTML5 para Android com controles touch, sistema de score e 3 vidas...",
            height=120,
            key=get_unique_key("gen_prompt")
        )
    
    with col2:
        tipos = [
            "HTML5 Android (Jogo Mobile)",
            "Godot 4.x (GDScript)",
            "Unity (C#)",
            "Discord Bot (Python)",
            "Telegram Bot (Python)",
            "Game Guardian (Lua)",
            "Python Script",
            "JavaScript/Node.js",
            "Flask API",
            "FastAPI",
            "React Component",
            "SQL Database"
        ]
        tipo = st.selectbox("🔤 Tipo", tipos, key=get_unique_key("gen_type"))
        nivel = st.select_slider("📊 Nível", ["Básico", "Médio", "Avançado", "Expert"], key=get_unique_key("gen_level"))
    
    # Verificar limite
    can_gen, remaining = can_generate()
    
    if not can_gen:
        st.warning("⚠️ Limite diário atingido! Faça upgrade para VIP ou volte amanhã.")
    
    # Botão de gerar
    if st.button("⚡ GERAR CÓDIGO", use_container_width=True, type="primary", disabled=not can_gen, key=get_unique_key("btn_generate")):
        if not prompt:
            st.error("❌ Descreva o que você quer criar!")
        else:
            with st.spinner("🔮 Gerando código profissional..."):
                try:
                    model = get_model()
                    if not model:
                        st.error("❌ API indisponível!")
                        st.stop()
                    
                    system_prompt = f"""Você é um programador expert em {tipo}. 
Crie código COMPLETO e 100% FUNCIONAL.

TAREFA: {prompt}
NÍVEL: {nivel}

REGRAS OBRIGATÓRIAS:
1. Código completo e pronto para usar
2. Comentários em português explicando as partes importantes
3. Seguir as melhores práticas da linguagem
4. Incluir tratamento de erros

REGRAS ESPECÍFICAS POR TIPO:
- HTML5 Android: Use touch events, viewport correto, meta tags PWA, fullscreen
- Godot: Use a sintaxe do Godot 4.x com typed GDScript
- Discord Bot: Use slash commands com discord.py
- Game Guardian: Use a API gg.* corretamente com menus
- Python: Use type hints e docstrings
- Flask/FastAPI: Inclua rotas CRUD, validação, erros

IMPORTANTE: Retorne APENAS o código, sem markdown, sem explicações."""

                    response = model.generate_content(system_prompt)
                    codigo = response.text
                    
                    # Limpar markdown
                    codigo = re.sub(r'^```[\w]*\n?', '', codigo)
                    codigo = re.sub(r'\n?```$', '', codigo)
                    codigo = codigo.strip()
                    
                    st.session_state.current_script = codigo
                    use_generation()
                    
                    st.success("✅ Código gerado com sucesso!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
    
    # Mostrar código gerado
    if st.session_state.current_script:
        st.markdown("---")
        st.markdown("### 📄 Código Gerado:")
        
        lang, ext = detect_language(st.session_state.current_script)
        
        # Info do código
        lines = len(st.session_state.current_script.split('\n'))
        chars = len(st.session_state.current_script)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📏 Linhas", lines)
        with col2:
            st.metric("🔤 Caracteres", f"{chars:,}")
        with col3:
            st.metric("💾 Tipo", lang.upper())
        
        # Código
        st.code(st.session_state.current_script, language=lang)
        
        # Botões de ação
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.download_button(
                "📥 Download",
                st.session_state.current_script,
                f"script_{generate_id()}{ext}",
                use_container_width=True,
                key=get_unique_key("dl_gen")
            )
        
        with col2:
            if is_vip():
                if st.button("💾 Salvar", use_container_width=True, key=get_unique_key("save_gen")):
                    if len(st.session_state.saved_scripts) >= 15:
                        st.warning("Limite de 15 scripts! Delete algum.")
                    else:
                        st.session_state.saved_scripts.append({
                            "id": generate_id(),
                            "name": f"Script_{len(st.session_state.saved_scripts)+1}{ext}",
                            "code": st.session_state.current_script,
                            "lang": lang,
                            "date": datetime.now().strftime("%d/%m %H:%M")
                        })
                        save_session()
                        st.success("✅ Salvo!")
            else:
                st.button("💾 Salvar 🔒", use_container_width=True, disabled=True, key=get_unique_key("save_gen_locked"))
                st.caption("VIP apenas")
        
        with col3:
            if is_vip():
                if st.button("⭐ Favoritar", use_container_width=True, key=get_unique_key("fav_gen")):
                    if len(st.session_state.favorites) >= 10:
                        st.warning("Limite de 10 favoritos!")
                    else:
                        st.session_state.favorites.append({
                            "id": generate_id(),
                            "name": f"Fav_{len(st.session_state.favorites)+1}{ext}",
                            "code": st.session_state.current_script,
                            "lang": lang,
                            "date": datetime.now().strftime("%d/%m %H:%M")
                        })
                        save_session()
                        st.success("⭐ Favoritado!")
            else:
                st.button("⭐ Favoritar 🔒", use_container_width=True, disabled=True, key=get_unique_key("fav_gen_locked"))
        
        with col4:
            if st.button("🗑️ Limpar", use_container_width=True, key=get_unique_key("clear_gen")):
                st.session_state.current_script = ""
                st.rerun()

# ====== TAB 2: CHAT ======
with tab2:
    st.markdown("### 💬 Chat com IA")
    
    # Container do chat
    chat_container = st.container()
    
    with chat_container:
        for idx, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <strong>👤 Você:</strong><br>{msg["content"][:1000]}
                </div>
                """, unsafe_allow_html=True)
                
                # Botão deletar
                if st.button("🗑️", key=get_unique_key(f"del_user_{idx}")):
                    st.session_state.chat_history.pop(idx)
                    save_session()
                    st.rerun()
            else:
                st.markdown(f"""
                <div class="chat-assistant">
                    <strong>🤖 IA:</strong><br>{msg["content"][:2000]}
                </div>
                """, unsafe_allow_html=True)
                
                # Botões de ação
                col1, col2, col3 = st.columns([1, 1, 8])
                with col1:
                    if st.button("📋", key=get_unique_key(f"copy_ai_{idx}"), help="Copiar"):
                        st.code(msg["content"])
                with col2:
                    if st.button("🗑️", key=get_unique_key(f"del_ai_{idx}"), help="Deletar"):
                        st.session_state.chat_history.pop(idx)
                        save_session()
                        st.rerun()
    
    st.markdown("---")
    
    # Input
    can_ch, remaining_ch = can_chat()
    
    if not can_ch:
        st.warning("⚠️ Limite de chat atingido! Faça upgrade para VIP.")
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "💭 Digite sua mensagem:",
            key=get_unique_key("chat_input"),
            disabled=not can_ch,
            placeholder="Pergunte sobre código, peça ajuda, tire dúvidas..."
        )
    with col2:
        send_btn = st.button("📤", disabled=not can_ch or not user_input, key=get_unique_key("btn_send"), type="primary")
    
    if send_btn and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("🤔 Pensando..."):
            try:
                model = get_model()
                
                # Contexto
                context = "\n".join([
                    f"{'Usuário' if m['role']=='user' else 'IA'}: {m['content'][:500]}"
                    for m in st.session_state.chat_history[-8:]
                ])
                
                response = model.generate_content(f"""Você é um assistente de programação expert e amigável.
Responda de forma clara, útil e em português.
Se o usuário pedir código, forneça código completo e funcional.

Conversa:
{context}

Responda à última mensagem do usuário de forma completa e útil.""")
                
                ai_response = response.text
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                use_chat()
                save_session()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    
    # Limpar chat
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🧹 Limpar Chat", key=get_unique_key("btn_clear_chat")):
            st.session_state.chat_history = []
            save_session()
            st.rerun()

# ====== TAB 3: EDITOR ======
with tab3:
    st.markdown("### 💻 Editor de Código")
    
    if st.session_state.current_script:
        lang, ext = detect_language(st.session_state.current_script)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            filename = st.text_input("📄 Nome do arquivo", value=f"script{ext}", key=get_unique_key("editor_filename"))
        with col2:
            st.metric("📏 Linhas", len(st.session_state.current_script.split('\n')))
        with col3:
            st.download_button(
                "📥 Download",
                st.session_state.current_script,
                filename,
                use_container_width=True,
                key=get_unique_key("dl_editor")
            )
        
        # Editor
        new_code = st.text_area(
            "✏️ Edite o código:",
            st.session_state.current_script,
            height=400,
            key=get_unique_key("editor_code")
        )
        st.session_state.current_script = new_code
        
        # Botões
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if is_vip():
                if st.button("💾 Salvar", use_container_width=True, key=get_unique_key("save_editor")):
                    if len(st.session_state.saved_scripts) >= 15:
                        st.warning("Limite de 15 scripts!")
                    else:
                        st.session_state.saved_scripts.append({
                            "id": generate_id(),
                            "name": filename,
                            "code": new_code,
                            "lang": lang,
                            "date": datetime.now().strftime("%d/%m %H:%M")
                        })
                        save_session()
                        st.success("✅ Salvo!")
            else:
                st.button("💾 Salvar 🔒", use_container_width=True, disabled=True, key=get_unique_key("save_editor_locked"))
        
        with col2:
            if is_vip():
                if st.button("⭐ Favoritar", use_container_width=True, key=get_unique_key("fav_editor")):
                    if len(st.session_state.favorites) >= 10:
                        st.warning("Limite de 10 favoritos!")
                    else:
                        st.session_state.favorites.append({
                            "id": generate_id(),
                            "name": filename,
                            "code": new_code,
                            "lang": lang,
                            "date": datetime.now().strftime("%d/%m %H:%M")
                        })
                        save_session()
                        st.success("⭐ Favoritado!")
            else:
                st.button("⭐ Favoritar 🔒", use_container_width=True, disabled=True, key=get_unique_key("fav_editor_locked"))
        
        with col3:
            if st.button("📋 Copiar", use_container_width=True, key=get_unique_key("copy_editor")):
                st.code(new_code)
                st.info("👆 Selecione e copie o código acima")
        
        with col4:
            if st.button("🗑️ Limpar", use_container_width=True, key=get_unique_key("clear_editor")):
                st.session_state.current_script = ""
                st.rerun()
        
        # Preview
        st.markdown("---")
        st.markdown("### 👁️ Preview")
        st.code(new_code, language=lang)
    else:
        st.info("📝 Nenhum código no editor.")
        st.markdown("""
        **Como começar:**
        1. Vá para **🤖 Gerar** e crie um código
        2. Ou selecione um **📚 Template** na sidebar
        3. Ou abra um script da **📚 Biblioteca**
        """)

# ====== TAB 4: BIBLIOTECA ======
with tab4:
    st.markdown("### 📚 Biblioteca")
    
    if not is_vip():
        st.warning("🔒 Biblioteca disponível apenas para VIP!")
        st.info("Faça upgrade para salvar e organizar seus scripts.")
    else:
        tab_saved, tab_favs = st.tabs(["📄 Salvos", "⭐ Favoritos"])
        
        with tab_saved:
            if st.session_state.saved_scripts:
                st.caption(f"📊 {len(st.session_state.saved_scripts)}/15 scripts salvos")
                
                for idx, script in enumerate(reversed(st.session_state.saved_scripts)):
                    script_id = script.get("id", generate_id())
                    
                    with st.expander(f"📄 {script['name']} - {script.get('date', '')}"):
                        preview = script['code'][:500]
                        if len(script['code']) > 500:
                            preview += "\n..."
                        st.code(preview, language=script.get('lang', 'text'))
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("📋 Carregar", key=get_unique_key(f"load_s_{script_id}")):
                                st.session_state.current_script = script['code']
                                st.success("✅ Carregado no editor!")
                                st.rerun()
                        
                        with col2:
                            st.download_button(
                                "📥 Download",
                                script['code'],
                                script['name'],
                                key=get_unique_key(f"dl_s_{script_id}")
                            )
                        
                        with col3:
                            if st.button("🗑️ Deletar", key=get_unique_key(f"del_s_{script_id}")):
                                real_idx = len(st.session_state.saved_scripts) - 1 - idx
                                st.session_state.saved_scripts.pop(real_idx)
                                save_session()
                                st.rerun()
            else:
                st.info("📭 Nenhum script salvo ainda.")
        
        with tab_favs:
            if st.session_state.favorites:
                st.caption(f"⭐ {len(st.session_state.favorites)}/10 favoritos")
                
                for idx, fav in enumerate(reversed(st.session_state.favorites)):
                    fav_id = fav.get("id", generate_id())
                    
                    with st.expander(f"⭐ {fav['name']} - {fav.get('date', '')}"):
                        preview = fav['code'][:500]
                        if len(fav['code']) > 500:
                            preview += "\n..."
                        st.code(preview, language=fav.get('lang', 'text'))
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📋 Carregar", key=get_unique_key(f"load_f_{fav_id}")):
                                st.session_state.current_script = fav['code']
                                st.success("✅ Carregado!")
                                st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Remover", key=get_unique_key(f"del_f_{fav_id}")):
                                real_idx = len(st.session_state.favorites) - 1 - idx
                                st.session_state.favorites.pop(real_idx)
                                save_session()
                                st.rerun()
            else:
                st.info("⭐ Nenhum favorito ainda.")

# ====== TAB 5: STATS ======
with tab5:
    st.markdown("### 📊 Estatísticas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h2 style="color:#6366f1;">📄</h2>
            <h3>{}</h3>
            <p style="color:#94a3b8;">Salvos</p>
        </div>
        """.format(len(st.session_state.saved_scripts)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h2 style="color:#f59e0b;">⭐</h2>
            <h3>{}</h3>
            <p style="color:#94a3b8;">Favoritos</p>
        </div>
        """.format(len(st.session_state.favorites)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <h2 style="color:#10b981;">💬</h2>
            <h3>{}</h3>
            <p style="color:#94a3b8;">Mensagens</p>
        </div>
        """.format(len(st.session_state.chat_history)), unsafe_allow_html=True)
    
    with col4:
        total_lines = sum(len(s.get('code', '').split('\n')) for s in st.session_state.saved_scripts)
        st.markdown("""
        <div class="stat-card">
            <h2 style="color:#ec4899;">📏</h2>
            <h3>{}</h3>
            <p style="color:#94a3b8;">Linhas</p>
        </div>
        """.format(total_lines), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Info do plano
    st.markdown("### 👤 Seu Plano")
    
    if st.session_state.is_master:
        st.success("🔥 **ADMINISTRADOR** - Acesso total ao sistema!")
    elif is_vip():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.success(f"👑 **VIP ATIVO** - {dias} dias restantes")
        st.markdown("""
        **Seus benefícios:**
        - ✅ Gerações ilimitadas
        - ✅ Chat ilimitado
        - ✅ Até 15 scripts salvos
        - ✅ Até 10 favoritos
        - ✅ Histórico persistente
        """)
    else:
        st.info(f"""
        🆓 **GRATUITO**
        
        **Uso de hoje:**
        - Gerações: {st.session_state.usage_count}/{DAILY_LIMIT_FREE}
        - Chat: {st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}
        
        🔄 Os limites renovam à meia-noite!
        
        **Faça upgrade para VIP** e tenha acesso ilimitado!
        """)

# ====== RODAPÉ ======
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"👤 {st.session_state.username}")
with col2:
    status = "🔥 ADMIN" if st.session_state.is_master else ("👑 VIP" if is_vip() else "🆓 Free")
    st.caption(f"Status: {status}")
with col3:
    st.caption("v4.0 | ScriptMaster AI Pro")
