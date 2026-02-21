import streamlit as st
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
    """Gera uma key única para evitar duplicação"""
    if "key_counter" not in st.session_state:
        st.session_state.key_counter = 0
    st.session_state.key_counter += 1
    return f"{prefix}_{st.session_state.key_counter}_{random.randint(1000, 9999)}"

# ====== CSS PREMIUM ======
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@400;500;600;700&display=swap');
    
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
        font-family: 'Orbitron', sans-serif;
        color: white;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        position: relative;
        z-index: 1;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.8);
    }
    
    .header-premium p {
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
        font-size: 1.1rem;
    }
    
    .master-badge {
        background: linear-gradient(135deg, #ff0844, #ffb199);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 20px rgba(255, 8, 68, 0.5);
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        color: #000;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 20px rgba(247, 151, 30, 0.5);
    }
    
    .free-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 4px 20px rgba(255, 8, 68, 0.5); }
        50% { transform: scale(1.05); box-shadow: 0 6px 30px rgba(255, 8, 68, 0.7); }
    }
    
    .chat-user {
        background: linear-gradient(135deg, #7b2ff7, #f107a3);
        color: white;
        padding: 1rem 1.2rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.75rem 0;
        margin-left: 15%;
        box-shadow: 0 4px 15px rgba(123, 47, 247, 0.4);
    }
    
    .chat-assistant {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: #e2e8f0;
        padding: 1rem 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.75rem 0;
        margin-right: 15%;
        border: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .usage-box {
        background: linear-gradient(135deg, rgba(123, 47, 247, 0.2), rgba(241, 7, 163, 0.2));
        border: 1px solid rgba(123, 47, 247, 0.4);
        border-radius: 15px;
        padding: 1.2rem;
        margin: 1rem 0;
    }
    
    .welcome-box {
        background: linear-gradient(135deg, #7b2ff7, #f107a3);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(123, 47, 247, 0.4);
    }
    
    .api-selector {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 47, 247, 0.1));
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .vip-feature {
        background: linear-gradient(135deg, rgba(247, 151, 30, 0.15), rgba(255, 210, 0, 0.15));
        border: 1px solid rgba(247, 151, 30, 0.4);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .free-feature {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(123, 47, 247, 0.15), rgba(241, 7, 163, 0.15));
        border: 1px solid rgba(123, 47, 247, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .model-badge {
        background: linear-gradient(135deg, #00d4ff, #0099ff);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .deepseek-badge {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .gemini-badge {
        background: linear-gradient(135deg, #4285f4, #34a853);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
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
            "api": st.session_state.get("selected_api", "gemini"),
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
                st.session_state.selected_api = data.get("api", "gemini")
                
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
    "selected_api": "gemini",
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

# ====== CONFIGURAÇÃO DAS APIs ======
GEMINI_AVAILABLE = False
DEEPSEEK_AVAILABLE = False

# Verificar Gemini
try:
    import google.generativeai as genai
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
except:
    pass

# Verificar DeepSeek
try:
    from openai import OpenAI
    DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")
    if DEEPSEEK_API_KEY:
        DEEPSEEK_AVAILABLE = True
except:
    pass

# Master Code
MASTER_CODE = st.secrets.get("MASTER_CODE", "GuizinhsDono")

# Verificar se alguma API está disponível
if not GEMINI_AVAILABLE and not DEEPSEEK_AVAILABLE:
    st.error("❌ Nenhuma API configurada!")
    st.code("""
# Adicione em Settings > Secrets:

# Para Gemini:
GEMINI_API_KEY = "sua_chave_gemini"

# Para DeepSeek:
DEEPSEEK_API_KEY = "sua_chave_deepseek"

# Código Master:
MASTER_CODE = "seu_codigo"
    """)
    st.info("🔗 Obtenha sua chave DeepSeek em: https://platform.deepseek.com/")
    st.info("🔗 Obtenha sua chave Gemini em: https://makersuite.google.com/app/apikey")
    st.stop()

# ====== FUNÇÕES DE IA ======
def get_available_apis():
    """Retorna lista de APIs disponíveis"""
    apis = []
    if GEMINI_AVAILABLE:
        apis.append(("gemini", "🌟 Gemini (Google)"))
    if DEEPSEEK_AVAILABLE:
        apis.append(("deepseek", "🧠 DeepSeek"))
    return apis

def generate_with_gemini(prompt):
    """Gera texto com Gemini"""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not models:
            return None, "Nenhum modelo Gemini disponível"
        
        model = genai.GenerativeModel(models[0])
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, str(e)

def generate_with_deepseek(prompt):
    """Gera texto com DeepSeek"""
    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Você é um programador expert. Responda em português."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

def generate_code(prompt, api="gemini"):
    """Gera código usando a API selecionada"""
    if api == "deepseek" and DEEPSEEK_AVAILABLE:
        return generate_with_deepseek(prompt)
    elif api == "gemini" and GEMINI_AVAILABLE:
        return generate_with_gemini(prompt)
    elif DEEPSEEK_AVAILABLE:
        return generate_with_deepseek(prompt)
    elif GEMINI_AVAILABLE:
        return generate_with_gemini(prompt)
    else:
        return None, "Nenhuma API disponível"

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
    elif '@bot' in code_lower or 'discord' in code_lower:
        return 'python', '.py'
    return 'text', '.txt'

# ====== TEMPLATES ======
TEMPLATES = {
    "🎮 Jogos Android HTML5": {
        "Jogo de Coleta Touch": """<!DOCTYPE html>
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
        #ui { position: fixed; top: 15px; left: 15px; right: 15px; display: flex; justify-content: space-between; color: #fff; font: bold 22px Arial; text-shadow: 0 0 10px #7b2ff7; z-index: 100; }
        #gameOver { position: fixed; inset: 0; background: rgba(0,0,0,0.95); display: none; flex-direction: column; align-items: center; justify-content: center; color: #fff; z-index: 200; }
        #gameOver.show { display: flex; }
        #gameOver h1 { font-size: 42px; background: linear-gradient(135deg, #00d4ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; }
        #gameOver button { margin-top: 30px; padding: 18px 50px; font-size: 20px; background: linear-gradient(135deg, #7b2ff7, #f107a3); border: none; border-radius: 30px; color: #fff; font-weight: bold; }
    </style>
</head>
<body>
    <canvas id="game"></canvas>
    <div id="ui">
        <span>🪙 <span id="score">0</span></span>
        <span>⏱️ <span id="time">30</span>s</span>
    </div>
    <div id="gameOver">
        <h1>🎮 Fim de Jogo!</h1>
        <p style="font-size:24px;">Pontos: <span id="finalScore">0</span></p>
        <button onclick="startGame()">🔄 Jogar Novamente</button>
    </div>
    <script>
        const canvas = document.getElementById('game');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        let score = 0, timeLeft = 30, gameRunning = false;
        const player = { x: canvas.width/2, y: canvas.height/2, size: 60 };
        let coins = [];
        let particles = [];
        
        function spawnCoin() {
            coins.push({
                x: Math.random() * (canvas.width - 50) + 25,
                y: Math.random() * (canvas.height - 150) + 80,
                size: 20 + Math.random() * 15,
                hue: Math.random() * 60 + 30
            });
        }
        
        function createParticles(x, y) {
            for (let i = 0; i < 12; i++) {
                particles.push({
                    x, y,
                    vx: (Math.random() - 0.5) * 10,
                    vy: (Math.random() - 0.5) * 10,
                    life: 25,
                    hue: Math.random() * 60 + 280
                });
            }
        }
        
        function startGame() {
            score = 0; timeLeft = 30; coins = []; particles = [];
            gameRunning = true;
            document.getElementById('gameOver').classList.remove('show');
            for (let i = 0; i < 6; i++) spawnCoin();
        }
        
        function endGame() {
            gameRunning = false;
            document.getElementById('finalScore').textContent = score;
            document.getElementById('gameOver').classList.add('show');
        }
        
        function update() {
            if (!gameRunning) return;
            
            for (let i = coins.length - 1; i >= 0; i--) {
                const c = coins[i];
                const dist = Math.hypot(player.x - c.x, player.y - c.y);
                if (dist < player.size/2 + c.size) {
                    coins.splice(i, 1);
                    score += Math.floor(c.size);
                    document.getElementById('score').textContent = score;
                    createParticles(c.x, c.y);
                    spawnCoin();
                }
            }
            
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx; p.y += p.vy; p.life--;
                if (p.life <= 0) particles.splice(i, 1);
            }
        }
        
        function draw() {
            ctx.fillStyle = '#0a0a1a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Grid
            ctx.strokeStyle = 'rgba(123, 47, 247, 0.1)';
            for (let x = 0; x < canvas.width; x += 50) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }
            
            // Coins
            const time = Date.now() / 200;
            coins.forEach(c => {
                const wobble = Math.sin(time + c.x) * 4;
                ctx.fillStyle = `hsl(${c.hue}, 100%, 60%)`;
                ctx.shadowColor = `hsl(${c.hue}, 100%, 50%)`;
                ctx.shadowBlur = 15;
                ctx.beginPath();
                ctx.arc(c.x, c.y + wobble, c.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            });
            
            // Particles
            particles.forEach(p => {
                ctx.globalAlpha = p.life / 25;
                ctx.fillStyle = `hsl(${p.hue}, 100%, 60%)`;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1;
            
            // Player
            const gradient = ctx.createRadialGradient(player.x, player.y, 0, player.x, player.y, player.size/2);
            gradient.addColorStop(0, '#00d4ff');
            gradient.addColorStop(1, '#7b2ff7');
            ctx.fillStyle = gradient;
            ctx.shadowColor = '#7b2ff7';
            ctx.shadowBlur = 20;
            ctx.beginPath();
            ctx.arc(player.x, player.y, player.size/2, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
            
            // Eyes
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(player.x - 12, player.y - 5, 10, 0, Math.PI * 2);
            ctx.arc(player.x + 12, player.y - 5, 10, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#0a0a1a';
            ctx.beginPath();
            ctx.arc(player.x - 10, player.y - 3, 5, 0, Math.PI * 2);
            ctx.arc(player.x + 14, player.y - 3, 5, 0, Math.PI * 2);
            ctx.fill();
        }
        
        function gameLoop() { update(); draw(); requestAnimationFrame(gameLoop); }
        
        setInterval(() => {
            if (gameRunning && timeLeft > 0) {
                timeLeft--;
                document.getElementById('time').textContent = timeLeft;
                if (timeLeft <= 0) endGame();
            }
        }, 1000);
        
        function movePlayer(x, y) {
            player.x = Math.max(30, Math.min(canvas.width - 30, x));
            player.y = Math.max(80, Math.min(canvas.height - 30, y));
        }
        
        canvas.addEventListener('touchstart', e => { e.preventDefault(); if (!gameRunning) startGame(); else movePlayer(e.touches[0].clientX, e.touches[0].clientY); });
        canvas.addEventListener('touchmove', e => { e.preventDefault(); if (gameRunning) movePlayer(e.touches[0].clientX, e.touches[0].clientY); });
        canvas.addEventListener('mousemove', e => { if (gameRunning) movePlayer(e.clientX, e.clientY); });
        canvas.addEventListener('click', () => { if (!gameRunning) startGame(); });
        
        gameLoop();
    </script>
</body>
</html>""",

        "Endless Runner Neon": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Neon Runner</title>
    <style>
        * { margin: 0; padding: 0; touch-action: manipulation; user-select: none; }
        body { background: #0a0a1a; overflow: hidden; }
        canvas { display: block; }
        #ui { position: fixed; top: 15px; left: 15px; right: 15px; display: flex; justify-content: space-between; color: #0ff; font: bold 24px 'Courier New'; text-shadow: 0 0 15px #0ff; z-index: 10; }
        #overlay { position: fixed; inset: 0; background: rgba(10,10,26,0.95); display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; z-index: 100; }
        #overlay.hidden { display: none; }
        #overlay h1 { font-size: 52px; background: linear-gradient(135deg, #0ff, #f0f); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        #overlay button { margin-top: 40px; padding: 20px 60px; font-size: 22px; background: linear-gradient(135deg, #0ff, #7b2ff7); border: none; border-radius: 30px; color: #fff; font-weight: bold; box-shadow: 0 0 30px rgba(0,255,255,0.5); }
        .hint { position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); color: rgba(255,255,255,0.6); font: 18px Arial; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.3; } }
    </style>
</head>
<body>
    <canvas id="c"></canvas>
    <div id="ui"><span>🏃 <span id="score">0</span>m</span><span>🏆 <span id="best">0</span>m</span></div>
    <div class="hint" id="hint">👆 Toque para pular</div>
    <div id="overlay">
        <h1 id="title">⚡ NEON RUNNER</h1>
        <p id="text" style="font-size:24px;margin-top:20px;color:#aaa;">Corra o máximo que puder!</p>
        <button onclick="startGame()">▶️ JOGAR</button>
    </div>
    <script>
        const c = document.getElementById('c'), ctx = c.getContext('2d');
        c.width = innerWidth; c.height = innerHeight;
        
        let score = 0, speed = 7, playing = false;
        let best = parseInt(localStorage.getItem('neonBest') || '0');
        document.getElementById('best').textContent = best;
        
        const ground = c.height - 100;
        const player = { x: 100, y: ground - 60, w: 50, h: 60, vy: 0, jumping: false, doubleJump: false };
        
        let obstacles = [];
        let particles = [];
        let bgHue = 0;
        let frame = 0;
        
        function addObstacle() {
            obstacles.push({
                x: c.width + 50,
                y: ground - 50 - Math.random() * 30,
                w: 30 + Math.random() * 20,
                h: 50 + Math.random() * 30,
                hue: Math.random() * 360
            });
        }
        
        function addParticle(x, y, hue) {
            for (let i = 0; i < 8; i++) {
                particles.push({
                    x, y,
                    vx: (Math.random() - 0.5) * 8,
                    vy: Math.random() * -10,
                    life: 30,
                    hue
                });
            }
        }
        
        function jump() {
            if (!playing) return;
            if (!player.jumping) {
                player.vy = -20;
                player.jumping = true;
                addParticle(player.x + player.w/2, player.y + player.h, 180);
            } else if (!player.doubleJump) {
                player.vy = -18;
                player.doubleJump = true;
                addParticle(player.x + player.w/2, player.y + player.h, 60);
            }
        }
        
        function startGame() {
            score = 0; speed = 7; obstacles = []; particles = [];
            player.y = ground - player.h; player.vy = 0;
            player.jumping = false; player.doubleJump = false;
            playing = true;
            document.getElementById('overlay').classList.add('hidden');
            document.getElementById('hint').style.display = 'block';
        }
        
        function gameOver() {
            playing = false;
            if (score > best) {
                best = score;
                localStorage.setItem('neonBest', best);
                document.getElementById('best').textContent = best;
            }
            document.getElementById('title').textContent = '💀 GAME OVER';
            document.getElementById('text').innerHTML = `Distância: ${score}m<br>Recorde: ${best}m`;
            document.getElementById('overlay').classList.remove('hidden');
            document.getElementById('hint').style.display = 'none';
        }
        
        function update() {
            if (!playing) return;
            frame++;
            bgHue = (bgHue + 0.2) % 360;
            
            player.vy += 1;
            player.y += player.vy;
            
            if (player.y + player.h >= ground) {
                player.y = ground - player.h;
                player.vy = 0;
                player.jumping = false;
                player.doubleJump = false;
            }
            
            if (frame % Math.max(50, 80 - score/3) === 0) addObstacle();
            
            for (let i = obstacles.length - 1; i >= 0; i--) {
                obstacles[i].x -= speed;
                
                if (player.x < obstacles[i].x + obstacles[i].w &&
                    player.x + player.w > obstacles[i].x &&
                    player.y < obstacles[i].y + obstacles[i].h &&
                    player.y + player.h > obstacles[i].y) {
                    addParticle(player.x + player.w/2, player.y + player.h/2, 0);
                    gameOver();
                    return;
                }
                
                if (obstacles[i].x + obstacles[i].w < 0) {
                    obstacles.splice(i, 1);
                    score++;
                    document.getElementById('score').textContent = score;
                    if (score % 10 === 0) speed += 0.4;
                }
            }
            
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].x += particles[i].vx;
                particles[i].y += particles[i].vy;
                particles[i].vy += 0.3;
                particles[i].life--;
                if (particles[i].life <= 0) particles.splice(i, 1);
            }
        }
        
        function draw() {
            // Background
            ctx.fillStyle = '#0a0a1a';
            ctx.fillRect(0, 0, c.width, c.height);
            
            // Neon grid
            ctx.strokeStyle = `hsla(${bgHue}, 100%, 50%, 0.1)`;
            for (let x = 0; x < c.width; x += 80) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, c.height); ctx.stroke();
            }
            for (let y = 0; y < c.height; y += 80) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(c.width, y); ctx.stroke();
            }
            
            // Ground
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, ground, c.width, c.height - ground);
            ctx.fillStyle = `hsl(${bgHue}, 100%, 50%)`;
            ctx.shadowColor = `hsl(${bgHue}, 100%, 50%)`;
            ctx.shadowBlur = 20;
            ctx.fillRect(0, ground, c.width, 4);
            ctx.shadowBlur = 0;
            
            // Particles
            particles.forEach(p => {
                ctx.globalAlpha = p.life / 30;
                ctx.fillStyle = `hsl(${p.hue}, 100%, 60%)`;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1;
            
            // Player
            const gradient = ctx.createLinearGradient(player.x, player.y, player.x + player.w, player.y + player.h);
            gradient.addColorStop(0, '#0ff');
            gradient.addColorStop(1, '#f0f');
            ctx.fillStyle = gradient;
            ctx.shadowColor = '#0ff';
            ctx.shadowBlur = 25;
            ctx.fillRect(player.x, player.y, player.w, player.h);
            ctx.shadowBlur = 0;
            
            // Player eyes
            ctx.fillStyle = '#fff';
            ctx.fillRect(player.x + 12, player.y + 15, 10, 12);
            ctx.fillRect(player.x + 28, player.y + 15, 10, 12);
            ctx.fillStyle = '#0a0a1a';
            ctx.fillRect(player.x + 17, player.y + 20, 4, 5);
            ctx.fillRect(player.x + 33, player.y + 20, 4, 5);
            
            // Jump trail
            if (player.jumping) {
                ctx.globalAlpha = 0.3;
                for (let i = 1; i <= 4; i++) {
                    ctx.fillStyle = `hsla(180, 100%, 50%, ${0.3 - i * 0.06})`;
                    ctx.fillRect(player.x - i * 12, player.y + i * 6, player.w, player.h);
                }
                ctx.globalAlpha = 1;
            }
            
            // Double jump indicator
            if (!player.doubleJump && player.jumping) {
                ctx.fillStyle = 'rgba(255, 255, 0, 0.6)';
                ctx.beginPath();
                ctx.arc(player.x + player.w/2, player.y - 15, 10, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // Obstacles
            obstacles.forEach(o => {
                ctx.fillStyle = `hsl(${o.hue}, 100%, 50%)`;
                ctx.shadowColor = `hsl(${o.hue}, 100%, 50%)`;
                ctx.shadowBlur = 15;
                ctx.fillRect(o.x, o.y, o.w, o.h);
            });
            ctx.shadowBlur = 0;
        }
        
        function loop() { update(); draw(); requestAnimationFrame(loop); }
        
        c.addEventListener('touchstart', e => { e.preventDefault(); jump(); });
        c.addEventListener('click', jump);
        document.addEventListener('keydown', e => { if (e.code === 'Space') { e.preventDefault(); jump(); } });
        
        loop();
    </script>
</body>
</html>"""
    },
    
    "🛡️ Game Guardian": {
        "Script Completo": """--[[
    ╔══════════════════════════════════════════╗
    ║        Rynmaru GG Script Pro             ║
    ║        Versão: 2.0                       ║
    ╚══════════════════════════════════════════╝
    
    ⚠️ APENAS PARA FINS EDUCACIONAIS!
]]

gg.setVisible(false)
gg.toast("🎮 Rynmaru Script carregado!")

local config = { version = "2.0", safeMode = true }
local running = true

-- Utilitários
local function toast(msg) gg.toast(msg) end
local function alert(msg, title) gg.alert(msg, "OK", nil, title or "Info") end
local function confirm(msg) return gg.alert(msg, "Sim", "Não") == 1 end
local function input(prompts, defaults, types) return gg.prompt(prompts, defaults, types) end

-- Funções de memória
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
    if count == 0 then toast("❌ Nenhum resultado!") return false end
    if count > maxResults then toast("⚠️ Muitos resultados: " .. count) return false end
    
    local results = gg.getResults(count)
    for i, v in ipairs(results) do results[i].value = newValue end
    gg.setValues(results)
    toast("✅ " .. count .. " valores alterados!")
    return true
end

-- Hacks
local function hackGenerico()
    local tipos = {"💰 Dinheiro", "💎 Gemas", "⚡ Energia", "❤️ Vida", "⚔️ Ataque", "🛡️ Defesa"}
    local choice = gg.choice(tipos, nil, "Tipo de Valor")
    if not choice then return end
    
    local inp = input({tipos[choice] .. " atual:", "Novo valor:"}, {"0", "999999"}, {"number", "number"})
    if not inp then return end
    
    local oldVal, newVal = tonumber(inp[1]), tonumber(inp[2])
    
    toast("🔍 Buscando...")
    local count = searchValue(oldVal, gg.TYPE_DWORD, gg.REGION_ANONYMOUS | gg.REGION_OTHER)
    
    if count > 0 and count < 500 then
        editResults(newVal)
    elseif count == 0 or count >= 500 then
        toast("🔍 Tentando FLOAT...")
        count = searchValue(oldVal, gg.TYPE_FLOAT, gg.REGION_ANONYMOUS | gg.REGION_OTHER)
        if count > 0 and count < 500 then editResults(newVal)
        else toast("❌ Não encontrado") end
    end
end

local function speedHack()
    local speeds = {0.25, 0.5, 1, 1.5, 2, 3, 5, 10}
    local labels = {"🐌 0.25x", "🐢 0.5x", "⏺️ 1x Normal", "🏃 1.5x", "🚀 2x", "⚡ 3x", "💨 5x", "🔥 10x"}
    local choice = gg.choice(labels, nil, "⚡ Velocidade")
    if choice then
        gg.setSpeed(speeds[choice])
        toast("Velocidade: " .. labels[choice])
    end
end

local function buscaAvancada()
    local menu = gg.choice({
        "🔍 Busca Simples",
        "📊 Busca por Faixa",
        "🔗 Busca Grupo",
        "🎯 Refinar",
        "✏️ Editar Resultados",
        "❄️ Congelar",
        "🔥 Descongelar",
        "🗑️ Limpar"
    }, nil, "🔍 Busca Avançada")
    
    if menu == 1 then
        local inp = input({"Valor:", "Tipo (1=INT, 2=FLOAT):"}, {"0", "1"}, {"text", "number"})
        if inp then
            local types = {gg.TYPE_DWORD, gg.TYPE_FLOAT}
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
        local inp = input({"Novo valor:"}, {"0"}, {"text"})
        if inp then
            gg.refineNumber(inp[1], gg.TYPE_DWORD)
            toast("Refinado: " .. gg.getResultsCount())
        end
    elseif menu == 5 then
        local inp = input({"Novo valor:"}, {"999999"}, {"text"})
        if inp then editResults(inp[1]) end
    elseif menu == 6 then
        local count = gg.getResultsCount()
        if count > 0 then
            local results = gg.getResults(count)
            for i, v in ipairs(results) do results[i].freeze = true end
            gg.addListItems(results)
            toast("❄️ " .. count .. " congelados!")
        else toast("Faça uma busca primeiro!") end
    elseif menu == 7 then
        local list = gg.getListItems()
        if #list > 0 then
            for i, v in ipairs(list) do list[i].freeze = false end
            gg.setValues(list)
            gg.clearList()
            toast("🔥 Descongelado!")
        end
    elseif menu == 8 then
        gg.clearResults()
        toast("🗑️ Limpo!")
    end
end

-- Menu Principal
local function mainMenu()
    local menu = gg.choice({
        "💰 Hack Genérico",
        "⚡ Speed Hack",
        "🔍 Busca Avançada",
        "🧹 Limpar Tudo",
        "ℹ️ Sobre",
        "❌ Sair"
    }, nil, "🎮 Rynmaru v" .. config.version)
    
    if menu == 1 then hackGenerico()
    elseif menu == 2 then speedHack()
    elseif menu == 3 then buscaAvancada()
    elseif menu == 4 then
        gg.clearResults()
        gg.clearList()
        gg.setSpeed(1)
        toast("🧹 Tudo limpo!")
    elseif menu == 5 then
        alert("🎮 Rynmaru GG Script\\n📌 Versão: " .. config.version .. "\\n\\n⚠️ Uso educacional apenas!", "ℹ️ Sobre")
    elseif menu == 6 then
        if confirm("Deseja sair?") then
            running = false
            gg.setSpeed(1)
            toast("👋 Até logo!")
        end
    end
end

toast("✅ Abra o menu do GG!")

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
        "Player 2D Completo": """extends CharacterBody2D
## Player 2D - Rynmaru Engine
## Godot 4.x

@export_group("Movimento")
@export var speed: float = 320.0
@export var acceleration: float = 2200.0
@export var friction: float = 1800.0

@export_group("Pulo")
@export var jump_velocity: float = -480.0
@export var max_jumps: int = 2
@export var coyote_time: float = 0.12
@export var jump_buffer: float = 0.1

@export_group("Dash")
@export var dash_speed: float = 650.0
@export var dash_duration: float = 0.12
@export var dash_cooldown: float = 0.4

var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")
var jumps_left: int = 0
var coyote_timer: float = 0.0
var buffer_timer: float = 0.0
var is_dashing: bool = false
var dash_timer: float = 0.0
var dash_cd_timer: float = 0.0
var dash_dir: Vector2 = Vector2.ZERO
var facing: int = 1

@onready var sprite = $AnimatedSprite2D
@onready var particles = $Particles

signal jumped
signal dashed
signal landed

func _ready():
    jumps_left = max_jumps

func _physics_process(delta):
    update_timers(delta)
    
    if is_dashing:
        process_dash(delta)
    else:
        apply_gravity(delta)
        handle_jump()
        handle_movement(delta)
        check_dash()
    
    update_animation()
    move_and_slide()

func update_timers(delta):
    if is_on_floor():
        coyote_timer = coyote_time
        jumps_left = max_jumps
    else:
        coyote_timer = max(0, coyote_timer - delta)
    
    if Input.is_action_just_pressed("jump"):
        buffer_timer = jump_buffer
    else:
        buffer_timer = max(0, buffer_timer - delta)
    
    dash_cd_timer = max(0, dash_cd_timer - delta)

func apply_gravity(delta):
    if not is_on_floor():
        velocity.y += gravity * delta

func handle_jump():
    var can_jump = is_on_floor() or coyote_timer > 0 or jumps_left > 0
    var wants_jump = Input.is_action_just_pressed("jump") or buffer_timer > 0
    
    if wants_jump and can_jump:
        velocity.y = jump_velocity
        jumps_left -= 1
        coyote_timer = 0
        buffer_timer = 0
        emit_signal("jumped")
        if particles: particles.emitting = true
    
    if Input.is_action_just_released("jump") and velocity.y < 0:
        velocity.y *= 0.5

func handle_movement(delta):
    var dir = Input.get_axis("move_left", "move_right")
    
    if dir != 0:
        velocity.x = move_toward(velocity.x, dir * speed, acceleration * delta)
        facing = sign(dir) as int
        sprite.flip_h = dir < 0
    else:
        velocity.x = move_toward(velocity.x, 0, friction * delta)

func check_dash():
    if Input.is_action_just_pressed("dash") and dash_cd_timer <= 0:
        start_dash()

func start_dash():
    is_dashing = true
    dash_timer = dash_duration
    dash_dir = Vector2(facing, 0)
    
    var input_dir = Input.get_vector("move_left", "move_right", "move_up", "move_down")
    if input_dir != Vector2.ZERO:
        dash_dir = input_dir.normalized()
    
    emit_signal("dashed")

func process_dash(delta):
    velocity = dash_dir * dash_speed
    dash_timer -= delta
    
    if dash_timer <= 0:
        is_dashing = false
        dash_cd_timer = dash_cooldown

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
"""
    },
    
    "🤖 Discord Bot": {
        "Bot Completo": """import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Database
DB_FILE = "rynmaru_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"users": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

db = load_db()

def get_user(user_id):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"balance": 0, "daily": None, "xp": 0, "level": 1}
        save_db(db)
    return db["users"][uid]

@bot.event
async def on_ready():
    print(f"✅ {bot.user} online!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos sincronizados")
    except Exception as e:
        print(f"❌ Erro: {e}")

@bot.tree.command(name="ping", description="Latência do bot")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: **{round(bot.latency * 1000)}ms**",
        color=0x7b2ff7
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="Mostra avatar")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"Avatar de {user.name}", color=0x7b2ff7)
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Info do servidor")
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=f"📊 {g.name}", color=0x7b2ff7)
    if g.icon: embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="👑 Dono", value=g.owner.mention if g.owner else "N/A")
    embed.add_field(name="👥 Membros", value=g.member_count)
    embed.add_field(name="💬 Canais", value=len(g.channels))
    embed.add_field(name="🎭 Cargos", value=len(g.roles))
    embed.add_field(name="📅 Criado", value=g.created_at.strftime("%d/%m/%Y"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="balance", description="Ver saldo")
async def balance(interaction: discord.Interaction):
    data = get_user(interaction.user.id)
    embed = discord.Embed(
        title="💰 Seu Saldo",
        description=f"**{data['balance']:,}** moedas\\nNível: **{data['level']}** | XP: **{data['xp']}**",
        color=0xffd700
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="Recompensa diária")
async def daily(interaction: discord.Interaction):
    data = get_user(interaction.user.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if data.get("daily") == today:
        embed = discord.Embed(title="⏰ Já Resgatado!", description="Volte amanhã!", color=0xff4444)
    else:
        reward = 100 + (data['level'] * 10)
        data["balance"] += reward
        data["daily"] = today
        data["xp"] += 25
        
        if data["xp"] >= data["level"] * 100:
            data["level"] += 1
            data["xp"] = 0
        
        save_db(db)
        embed = discord.Embed(
            title="🎁 Recompensa Diária!",
            description=f"Você ganhou **{reward}** moedas!\\nSaldo: **{data['balance']:,}**",
            color=0x00ff88
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="coinflip", description="Cara ou coroa")
async def coinflip(interaction: discord.Interaction, aposta: int = 0):
    import random
    data = get_user(interaction.user.id)
    
    if aposta > 0:
        if data["balance"] < aposta:
            await interaction.response.send_message("❌ Saldo insuficiente!", ephemeral=True)
            return
        
        won = random.choice([True, False])
        result = "Cara" if random.choice([True, False]) else "Coroa"
        
        if won:
            data["balance"] += aposta
            msg = f"🎉 Você ganhou! +{aposta} moedas"
        else:
            data["balance"] -= aposta
            msg = f"😢 Você perdeu! -{aposta} moedas"
        
        save_db(db)
        await interaction.response.send_message(f"🪙 **{result}**\\n{msg}\\nSaldo: {data['balance']:,}")
    else:
        result = random.choice(["🪙 Cara!", "🎭 Coroa!"])
        await interaction.response.send_message(result)

# bot.run("SEU_TOKEN")
"""
    },
    
    "🐍 Python Scripts": {
        "Web Scraper": """import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class RynmaruScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.data = []
    
    def fetch(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Erro: {e}")
            return None
    
    def scrape(self, url):
        html = self.fetch(url)
        if not html: return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            'url': url,
            'title': soup.title.string.strip() if soup.title else '',
            'headings': [h.text.strip() for h in soup.find_all(['h1','h2','h3'])[:10]],
            'links': [a.get('href') for a in soup.find_all('a', href=True)[:20]],
            'images': [img.get('src') for img in soup.find_all('img', src=True)[:10]],
            'timestamp': datetime.now().isoformat()
        }
    
    def save_json(self, filename='scrape.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"Salvo: {filename}")

if __name__ == "__main__":
    scraper = RynmaruScraper()
    result = scraper.scrape("https://example.com")
    if result:
        print(f"Título: {result['title']}")
        print(f"Links: {len(result['links'])}")
        scraper.data.append(result)
        scraper.save_json()
""",

        "API Flask": """from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

db = {"users": [], "items": []}

@app.route('/')
def home():
    return jsonify({"name": "Rynmaru API", "version": "1.0"})

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({"data": db["users"]})

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Nome obrigatório"}), 400
    
    user = {
        "id": len(db["users"]) + 1,
        "name": data["name"],
        "email": data.get("email", ""),
        "created": datetime.now().isoformat()
    }
    db["users"].append(user)
    return jsonify({"data": user}), 201

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    db["users"] = [u for u in db["users"] if u["id"] != id]
    return jsonify({"message": "Deletado"})

if __name__ == '__main__':
    print("🚀 Rynmaru API em http://localhost:5000")
    app.run(debug=True)
"""
    }
}

# ====== TELA DE LOGIN ======
if not st.session_state.authenticated:
    st.markdown("""
    <div class="header-premium">
        <h1>🎮 RYNMARU IA</h1>
        <p>Gerador Profissional de Scripts e Jogos com Inteligência Artificial</p>
    </div>
    """, unsafe_allow_html=True)
    
    # APIs disponíveis
    apis = get_available_apis()
    api_info = []
    if GEMINI_AVAILABLE:
        api_info.append("✅ Gemini")
    if DEEPSEEK_AVAILABLE:
        api_info.append("✅ DeepSeek")
    
    st.success(f"🤖 APIs disponíveis: {' | '.join(api_info)}")
    
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
                        st.success("VIP ativado!")
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
                <li>✅ 10 mensagens chat/dia</li>
                <li>✅ Templates básicos</li>
                <li>❌ Salvar scripts</li>
                <li>❌ Escolher API</li>
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
                <li>✅ Escolher API (Gemini/DeepSeek)</li>
                <li>✅ Salvar 15 scripts</li>
                <li>✅ 10 favoritos</li>
                <li>✅ Histórico na nuvem</li>
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
    
    # Seletor de API (VIP only)
    if is_vip():
        st.markdown("### 🤖 Escolher IA")
        apis = get_available_apis()
        api_options = {name: key for key, name in apis}
        selected = st.radio(
            "Modelo:",
            options=[name for _, name in apis],
            key=get_unique_key("api_select"),
            horizontal=True
        )
        st.session_state.selected_api = api_options.get(selected, "gemini")
        
        # Badge da API
        if st.session_state.selected_api == "deepseek":
            st.markdown('<span class="deepseek-badge">🧠 DeepSeek Ativo</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="gemini-badge">🌟 Gemini Ativo</span>', unsafe_allow_html=True)
    else:
        st.info("🔒 Escolha de API: VIP apenas")
    
    st.markdown("---")
    
    # Uso
    if is_vip():
        st.success("✨ Uso ILIMITADO!")
    else:
        st.markdown(f"""
        <div class="usage-box">
            <p style="margin:0;color:#fff;">⚡ Gerações: <strong>{st.session_state.usage_count}/{DAILY_LIMIT_FREE}</strong></p>
            <p style="margin:5px 0 0 0;color:#fff;">💬 Chat: <strong>{st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}</strong></p>
            <p style="margin:10px 0 0 0;font-size:12px;color:#aaa;">🔄 Renova à meia-noite</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Admin
    if st.session_state.is_master:
        st.markdown("---")
        with st.expander("🎫 Criar Código VIP"):
            new_code = st.text_input("Código", key=get_unique_key("new_code"))
            code_days = st.selectbox("Duração", ["1 dia", "7 dias", "30 dias", "Ilimitado"], key=get_unique_key("code_days"))
            
            if st.button("✨ Criar", key=get_unique_key("btn_create")):
                if new_code and new_code not in st.session_state.created_codes:
                    days_map = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                    st.session_state.created_codes[new_code] = {"days": days_map[code_days], "used": False}
                    st.success("✅ Criado!")
                    st.code(new_code)
    
    # Templates
    st.markdown("---")
    st.markdown("### 📚 Templates")
    
    for category, templates in TEMPLATES.items():
        with st.expander(category):
            for name, code in templates.items():
                if st.button(f"📄 {name}", key=get_unique_key(f"tmpl_{name[:8]}"), use_container_width=True):
                    st.session_state.current_script = code
                    st.toast(f"✅ '{name}' carregado!")
                    st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True, key=get_unique_key("logout")):
        clear_session()
        st.rerun()

# ====== ÁREA PRINCIPAL ======
st.markdown("""
<div class="header-premium">
    <h1>🎮 RYNMARU IA</h1>
    <p>Gerador de Scripts e Jogos com Inteligência Artificial</p>
</div>
""", unsafe_allow_html=True)

# Mostrar API ativa
current_api = st.session_state.get("selected_api", "gemini")
if current_api == "deepseek":
    st.markdown('<span class="deepseek-badge">🧠 Usando DeepSeek</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="gemini-badge">🌟 Usando Gemini</span>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 Gerar", "💬 Chat", "💻 Editor", "📚 Biblioteca", "📊 Stats"])

# ====== TAB GERAR ======
with tab1:
    st.markdown("### 🎯 Descreva o que você quer criar")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_area(
            "📝 Descrição:",
            placeholder="Ex: Crie um jogo de plataforma 2D em HTML5 para Android...",
            height=120,
            key=get_unique_key("prompt")
        )
    
    with col2:
        tipos = [
            "HTML5 Android (Jogo)",
            "Godot 4.x (GDScript)",
            "Unity (C#)",
            "Discord Bot (Python)",
            "Game Guardian (Lua)",
            "Python Script",
            "JavaScript",
            "Flask API",
            "React Component"
        ]
        tipo = st.selectbox("🔤 Tipo", tipos, key=get_unique_key("tipo"))
        nivel = st.select_slider("📊 Nível", ["Básico", "Médio", "Avançado"], key=get_unique_key("nivel"))
    
    can_gen, remaining = can_generate()
    
    if not can_gen:
        st.warning("⚠️ Limite atingido! Seja VIP para uso ilimitado.")
    
    if st.button("⚡ GERAR CÓDIGO", use_container_width=True, type="primary", disabled=not can_gen, key=get_unique_key("btn_gen")):
        if not prompt:
            st.error("❌ Descreva o que quer criar!")
        else:
            with st.spinner(f"🔮 Gerando com {current_api.upper()}..."):
                system_prompt = f"""Você é um programador expert em {tipo}. 
Crie código COMPLETO e 100% FUNCIONAL.

TAREFA: {prompt}
NÍVEL: {nivel}

REGRAS:
1. Código completo e pronto para usar
2. Comentários em português
3. Melhores práticas
4. Se for jogo mobile HTML5: use touch events, viewport correto, meta tags PWA
5. Se for Game Guardian: use gg.* API corretamente

IMPORTANTE: Retorne APENAS o código, sem markdown."""

                result, error = generate_code(system_prompt, current_api)
                
                if error:
                    st.error(f"❌ Erro: {error}")
                elif result:
                    # Limpar markdown
                    codigo = re.sub(r'^```[\w]*\n?', '', result)
                    codigo = re.sub(r'\n?```$', '', codigo)
                    codigo = codigo.strip()
                    
                    st.session_state.current_script = codigo
                    use_generation()
                    st.success("✅ Código gerado!")
                    st.rerun()
    
    # Mostrar código
    if st.session_state.current_script:
        st.markdown("---")
        st.markdown("### 📄 Código Gerado:")
        
        lang, ext = detect_language(st.session_state.current_script)
        lines = len(st.session_state.current_script.split('\n'))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📏 Linhas", lines)
        with col2:
            st.metric("🔤 Caracteres", f"{len(st.session_state.current_script):,}")
        with col3:
            st.metric("💾 Tipo", lang.upper())
        
        st.code(st.session_state.current_script, language=lang)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.download_button(
                "📥 Download",
                st.session_state.current_script,
                f"rynmaru_{generate_id()}{ext}",
                use_container_width=True,
                key=get_unique_key("dl_gen")
            )
        
        with col2:
            if is_vip():
                if st.button("💾 Salvar", use_container_width=True, key=get_unique_key("save_gen")):
                    if len(st.session_state.saved_scripts) >= 15:
                        st.warning("Limite de 15 scripts!")
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
                st.button("💾 Salvar 🔒", use_container_width=True, disabled=True, key=get_unique_key("save_lock"))
        
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
                st.button("⭐ Favoritar 🔒", use_container_width=True, disabled=True, key=get_unique_key("fav_lock"))
        
        with col4:
            if st.button("🗑️ Limpar", use_container_width=True, key=get_unique_key("clear_gen")):
                st.session_state.current_script = ""
                st.rerun()

# ====== TAB CHAT ======
with tab2:
    st.markdown("### 💬 Chat com IA")
    
    for idx, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
                <strong>👤 Você:</strong><br>{msg["content"][:1000]}
            </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️", key=get_unique_key(f"del_u_{idx}")):
                st.session_state.chat_history.pop(idx)
                save_session()
                st.rerun()
        else:
            st.markdown(f"""
            <div class="chat-assistant">
                <strong>🤖 IA:</strong><br>{msg["content"][:2000]}
            </div>
            """, unsafe_allow_html=True)
            col1, col2 = st.columns([1, 10])
            with col1:
                if st.button("📋", key=get_unique_key(f"copy_{idx}")):
                    st.code(msg["content"])
            with col2:
                if st.button("🗑️", key=get_unique_key(f"del_a_{idx}")):
                    st.session_state.chat_history.pop(idx)
                    save_session()
                    st.rerun()
    
    st.markdown("---")
    
    can_ch, _ = can_chat()
    if not can_ch:
        st.warning("⚠️ Limite de chat atingido!")
    
    user_input = st.text_input("💭 Mensagem:", key=get_unique_key("chat_in"), disabled=not can_ch)
    
    if st.button("📤 Enviar", disabled=not can_ch or not user_input, key=get_unique_key("btn_send")):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("🤔 Pensando..."):
            context = "\n".join([
                f"{'Usuário' if m['role']=='user' else 'IA'}: {m['content'][:500]}"
                for m in st.session_state.chat_history[-8:]
            ])
            
            prompt = f"""Você é um assistente de programação expert e amigável.
Responda em português de forma clara e útil.

Conversa:
{context}

Responda à última mensagem:"""

            result, error = generate_code(prompt, current_api)
            
            if error:
                st.error(f"Erro: {error}")
            elif result:
                st.session_state.chat_history.append({"role": "assistant", "content": result})
                use_chat()
                save_session()
                st.rerun()
    
    if st.button("🧹 Limpar Chat", key=get_unique_key("clear_chat")):
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
            filename = st.text_input("📄 Nome", value=f"script{ext}", key=get_unique_key("fname"))
        with col2:
            st.download_button("📥", st.session_state.current_script, filename, key=get_unique_key("dl_ed"))
        
        new_code = st.text_area("✏️ Código:", st.session_state.current_script, height=400, key=get_unique_key("editor"))
        st.session_state.current_script = new_code
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if is_vip():
                if st.button("💾 Salvar", use_container_width=True, key=get_unique_key("save_ed")):
                    st.session_state.saved_scripts.append({
                        "id": generate_id(), "name": filename, "code": new_code,
                        "lang": lang, "date": datetime.now().strftime("%d/%m %H:%M")
                    })
                    save_session()
                    st.success("✅ Salvo!")
        with col2:
            if st.button("📋 Copiar", use_container_width=True, key=get_unique_key("copy_ed")):
                st.code(new_code)
        with col3:
            if st.button("🗑️ Limpar", use_container_width=True, key=get_unique_key("clear_ed")):
                st.session_state.current_script = ""
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 👁️ Preview")
        st.code(new_code, language=lang)
    else:
        st.info("📝 Nenhum código no editor. Gere ou selecione um template!")

# ====== TAB BIBLIOTECA ======
with tab4:
    st.markdown("### 📚 Biblioteca")
    
    if not is_vip():
        st.warning("🔒 Biblioteca disponível apenas para VIP!")
    else:
        tab_s, tab_f = st.tabs(["📄 Salvos", "⭐ Favoritos"])
        
        with tab_s:
            if st.session_state.saved_scripts:
                for idx, s in enumerate(reversed(st.session_state.saved_scripts)):
                    with st.expander(f"📄 {s['name']} - {s.get('date', '')}"):
                        st.code(s['code'][:500] + "..." if len(s['code']) > 500 else s['code'], language=s.get('lang', 'text'))
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if st.button("📋 Carregar", key=get_unique_key(f"load_s_{s['id']}")):
                                st.session_state.current_script = s['code']
                                st.rerun()
                        with c2:
                            st.download_button("📥", s['code'], s['name'], key=get_unique_key(f"dl_s_{s['id']}"))
                        with c3:
                            if st.button("🗑️", key=get_unique_key(f"del_s_{s['id']}")):
                                real_idx = len(st.session_state.saved_scripts) - 1 - idx
                                st.session_state.saved_scripts.pop(real_idx)
                                save_session()
                                st.rerun()
            else:
                st.info("Nenhum script salvo.")
        
        with tab_f:
            if st.session_state.favorites:
                for idx, f in enumerate(reversed(st.session_state.favorites)):
                    with st.expander(f"⭐ {f['name']} - {f.get('date', '')}"):
                        st.code(f['code'][:500], language=f.get('lang', 'text'))
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("📋 Carregar", key=get_unique_key(f"load_f_{f['id']}")):
                                st.session_state.current_script = f['code']
                                st.rerun()
                        with c2:
                            if st.button("🗑️", key=get_unique_key(f"del_f_{f['id']}")):
                                real_idx = len(st.session_state.favorites) - 1 - idx
                                st.session_state.favorites.pop(real_idx)
                                save_session()
                                st.rerun()
            else:
                st.info("Nenhum favorito.")

# ====== TAB STATS ======
with tab5:
    st.markdown("### 📊 Estatísticas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""<div class="stat-card"><h2>📄</h2><h3>{len(st.session_state.saved_scripts)}</h3><p>Salvos</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-card"><h2>⭐</h2><h3>{len(st.session_state.favorites)}</h3><p>Favoritos</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-card"><h2>💬</h2><h3>{len(st.session_state.chat_history)}</h3><p>Mensagens</p></div>""", unsafe_allow_html=True)
    with col4:
        total = sum(len(s.get('code', '').split('\n')) for s in st.session_state.saved_scripts)
        st.markdown(f"""<div class="stat-card"><h2>📏</h2><h3>{total}</h3><p>Linhas</p></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.is_master:
        st.success("🔥 ADMINISTRADOR - Acesso total!")
    elif is_vip():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.success(f"👑 VIP ATIVO - {dias} dias restantes")
    else:
        st.info(f"""
        🆓 **GRATUITO**
        - Gerações: {st.session_state.usage_count}/{DAILY_LIMIT_FREE}
        - Chat: {st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}
        """)

# Rodapé
st.markdown("---")
st.caption("🎮 Rynmaru IA v1.0 | Criado por Guizinhs | Gemini + DeepSeek")
