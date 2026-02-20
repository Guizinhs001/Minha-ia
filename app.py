import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
import re
import base64
import zlib

# ====== CONFIGURAÇÃO DA PÁGINA ======
st.set_page_config(
    page_title="ScriptMaster AI Pro 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CONSTANTES ======
MASTER_CODE = "GuizinhsDono"
DAILY_LIMIT_FREE = 4
DAILY_LIMIT_CHAT_FREE = 10

# ====== CSS PREMIUM ======
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --success: #10b981;
        --danger: #ef4444;
        --dark: #0f172a;
    }
    
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
        max-width: 80%;
        margin-left: auto;
    }
    
    .chat-assistant {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
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
    
    .template-btn {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        transition: all 0.3s;
    }
    
    .template-btn:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: #6366f1;
    }
</style>
""", unsafe_allow_html=True)

# ====== FUNÇÕES DE PERSISTÊNCIA ======
def compress_data(data):
    """Comprime dados para URL"""
    try:
        json_str = json.dumps(data, separators=(',', ':'))
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
        
        if len(encoded) < 2000:  # Limite de URL
            st.query_params["d"] = encoded
            st.query_params["t"] = token
    except Exception as e:
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
    "editing_msg_idx": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Auto-login
if not st.session_state.authenticated and not st.session_state.login_checked:
    st.session_state.login_checked = True
    if load_session():
        st.toast(f"✅ Bem-vindo de volta, {st.session_state.username}!")

# ====== CONFIGURAR API ======
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("❌ Configure a chave API em Settings > Secrets")
    st.code('GEMINI_API_KEY = "sua_chave_aqui"')
    st.stop()

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
    elif 'using unityengine' in code_lower:
        return 'csharp', '.cs'
    elif '<!doctype' in code_lower or '<html' in code_lower:
        return 'html', '.html'
    elif 'gg.' in code_lower or 'function(' in code_lower and 'end' in code_lower:
        return 'lua', '.lua'
    elif 'def ' in code_lower or 'import ' in code_lower:
        return 'python', '.py'
    elif 'function' in code_lower or 'const ' in code_lower:
        return 'javascript', '.js'
    return 'python', '.py'
	# ====== TEMPLATES ======
TEMPLATES = {
    "🎮 Android HTML5": {
        "Jogo Touch Completo": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <title>Mobile Game</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; touch-action: manipulation; user-select: none; }
        html, body { width: 100%; height: 100%; overflow: hidden; background: #1a1a2e; }
        canvas { display: block; width: 100%; height: 100%; }
        #ui { position: absolute; top: 10px; left: 10px; right: 10px; display: flex; justify-content: space-between; color: white; font-family: Arial; font-size: 20px; font-weight: bold; }
        #controls { position: absolute; bottom: 20px; left: 20px; right: 20px; display: flex; justify-content: space-between; }
        .btn { width: 70px; height: 70px; border-radius: 50%; background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.4); color: white; font-size: 24px; display: flex; align-items: center; justify-content: center; }
        .btn:active { background: rgba(0,255,136,0.4); }
        .btn-jump { width: 90px; height: 90px; background: linear-gradient(135deg, #00ff88, #00cc6a); }
        #joystick { width: 120px; height: 120px; position: relative; }
        #joystick-base { width: 100%; height: 100%; border-radius: 50%; background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.3); }
        #joystick-handle { width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }
    </style>
</head>
<body>
    <canvas id="game"></canvas>
    <div id="ui">
        <span>⭐ <span id="score">0</span></span>
        <span>❤️ <span id="lives">3</span></span>
    </div>
    <div id="controls">
        <div id="joystick">
            <div id="joystick-base"></div>
            <div id="joystick-handle"></div>
        </div>
        <button class="btn btn-jump" id="jumpBtn">⬆️</button>
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
        
        let score = 0, lives = 3;
        const player = { x: 100, y: 0, w: 50, h: 50, vy: 0, grounded: false };
        const gravity = 0.6, jumpPower = -15;
        let moveX = 0;
        let platforms = [], coins = [];
        
        function init() {
            const groundY = canvas.height - 100;
            player.y = groundY - player.h;
            platforms = [{ x: 0, y: groundY, w: canvas.width, h: 100 }];
            for (let i = 0; i < 5; i++) {
                platforms.push({
                    x: Math.random() * (canvas.width - 100),
                    y: groundY - 100 - i * 100,
                    w: 100 + Math.random() * 50,
                    h: 15
                });
            }
            for (let i = 0; i < 8; i++) {
                coins.push({
                    x: Math.random() * (canvas.width - 30) + 15,
                    y: Math.random() * (canvas.height - 300) + 100,
                    r: 12, collected: false
                });
            }
        }
        init();
        
        // Joystick
        const joystick = document.getElementById('joystick');
        const handle = document.getElementById('joystick-handle');
        let joyActive = false, joyStartX = 0, joyStartY = 0;
        
        joystick.addEventListener('touchstart', e => {
            e.preventDefault();
            joyActive = true;
            const rect = joystick.getBoundingClientRect();
            joyStartX = rect.left + rect.width / 2;
            joyStartY = rect.top + rect.height / 2;
        });
        
        document.addEventListener('touchmove', e => {
            if (!joyActive) return;
            const touch = e.touches[0];
            let dx = touch.clientX - joyStartX;
            let dy = touch.clientY - joyStartY;
            const dist = Math.min(Math.sqrt(dx*dx + dy*dy), 40);
            const angle = Math.atan2(dy, dx);
            dx = Math.cos(angle) * dist;
            dy = Math.sin(angle) * dist;
            handle.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
            moveX = dx / 40 * 8;
        });
        
        document.addEventListener('touchend', () => {
            joyActive = false;
            handle.style.transform = 'translate(-50%, -50%)';
            moveX = 0;
        });
        
        // Jump
        document.getElementById('jumpBtn').addEventListener('touchstart', e => {
            e.preventDefault();
            if (player.grounded) {
                player.vy = jumpPower;
                player.grounded = false;
            }
        });
        
        function update() {
            player.vy += gravity;
            player.y += player.vy;
            player.x += moveX;
            
            if (player.x < 0) player.x = 0;
            if (player.x + player.w > canvas.width) player.x = canvas.width - player.w;
            
            player.grounded = false;
            for (const p of platforms) {
                if (player.x < p.x + p.w && player.x + player.w > p.x &&
                    player.y + player.h > p.y && player.y + player.h < p.y + p.h + 15 &&
                    player.vy >= 0) {
                    player.y = p.y - player.h;
                    player.vy = 0;
                    player.grounded = true;
                }
            }
            
            for (const c of coins) {
                if (!c.collected) {
                    const dist = Math.hypot(player.x + player.w/2 - c.x, player.y + player.h/2 - c.y);
                    if (dist < player.w/2 + c.r) {
                        c.collected = true;
                        score += 10;
                        document.getElementById('score').textContent = score;
                    }
                }
            }
        }
        
        function draw() {
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = '#2d3436';
            for (const p of platforms) {
                ctx.fillRect(p.x, p.y, p.w, p.h);
                ctx.fillStyle = '#00ff88';
                ctx.fillRect(p.x, p.y, p.w, 3);
                ctx.fillStyle = '#2d3436';
            }
            
            const time = Date.now() / 200;
            for (const c of coins) {
                if (!c.collected) {
                    const by = Math.sin(time) * 3;
                    ctx.fillStyle = '#ffd700';
                    ctx.beginPath();
                    ctx.arc(c.x, c.y + by, c.r, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(player.x, player.y, player.w, player.h);
            ctx.fillStyle = '#fff';
            ctx.fillRect(player.x + 10, player.y + 12, 8, 8);
            ctx.fillRect(player.x + 32, player.y + 12, 8, 8);
        }
        
        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }
        loop();
    </script>
</body>
</html>''',
        
        "Endless Runner Mobile": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <title>Endless Runner</title>
    <style>
        * { margin: 0; padding: 0; touch-action: manipulation; user-select: none; }
        body { background: #1a1a2e; overflow: hidden; }
        canvas { display: block; }
        #ui { position: fixed; top: 20px; left: 20px; color: white; font: bold 24px Arial; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
        #gameOver { position: fixed; inset: 0; background: rgba(0,0,0,0.9); display: none; flex-direction: column; align-items: center; justify-content: center; color: white; font-family: Arial; }
        #gameOver.show { display: flex; }
        #gameOver h1 { font-size: 48px; color: #ff4757; margin-bottom: 20px; }
        #gameOver p { font-size: 24px; margin-bottom: 30px; }
        #gameOver button { padding: 15px 40px; font-size: 20px; background: #00ff88; border: none; border-radius: 30px; font-weight: bold; }
        #tap { position: fixed; bottom: 50px; left: 50%; transform: translateX(-50%); color: rgba(255,255,255,0.7); font: 18px Arial; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.3; } }
    </style>
</head>
<body>
    <canvas id="c"></canvas>
    <div id="ui">⭐ <span id="score">0</span></div>
    <div id="tap">👆 TOQUE PARA PULAR</div>
    <div id="gameOver">
        <h1>💀 GAME OVER</h1>
        <p>Pontos: <span id="finalScore">0</span></p>
        <button onclick="restart()">🔄 JOGAR</button>
    </div>
    <script>
        const c = document.getElementById('c'), ctx = c.getContext('2d');
        c.width = innerWidth; c.height = innerHeight;
        
        let score = 0, speed = 6, playing = true;
        const groundY = c.height - 80;
        const player = { x: 80, y: groundY - 50, w: 50, h: 50, vy: 0, grounded: true };
        let obstacles = [], bgX = 0;
        
        function jump() {
            if (player.grounded && playing) {
                player.vy = -16;
                player.grounded = false;
            }
        }
        
        c.addEventListener('touchstart', e => { e.preventDefault(); jump(); });
        c.addEventListener('click', jump);
        document.addEventListener('keydown', e => { if (e.code === 'Space') jump(); });
        
        function spawnObstacle() {
            obstacles.push({ x: c.width, y: groundY - 40 - Math.random() * 30, w: 30 + Math.random() * 20, h: 40 + Math.random() * 30 });
        }
        
        let obstacleTimer = 0;
        function update() {
            if (!playing) return;
            
            player.vy += 0.7;
            player.y += player.vy;
            if (player.y + player.h >= groundY) {
                player.y = groundY - player.h;
                player.vy = 0;
                player.grounded = true;
            }
            
            obstacleTimer++;
            if (obstacleTimer > 80 - Math.min(score/2, 40)) {
                spawnObstacle();
                obstacleTimer = 0;
            }
            
            for (let i = obstacles.length - 1; i >= 0; i--) {
                obstacles[i].x -= speed;
                
                if (obstacles[i].x + obstacles[i].w < 0) {
                    obstacles.splice(i, 1);
                    score++;
                    document.getElementById('score').textContent = score;
                    if (score % 10 === 0) speed += 0.5;
                    continue;
                }
                
                if (player.x < obstacles[i].x + obstacles[i].w &&
                    player.x + player.w > obstacles[i].x &&
                    player.y < obstacles[i].y + obstacles[i].h &&
                    player.y + player.h > obstacles[i].y) {
                    gameOver();
                }
            }
            
            bgX = (bgX + speed * 0.3) % 100;
        }
        
        function draw() {
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, c.width, c.height);
            
            ctx.strokeStyle = 'rgba(255,255,255,0.05)';
            for (let x = -bgX; x < c.width; x += 100) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, c.height); ctx.stroke();
            }
            
            ctx.fillStyle = '#2d3436';
            ctx.fillRect(0, groundY, c.width, c.height - groundY);
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(0, groundY, c.width, 3);
            
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(player.x, player.y, player.w, player.h);
            ctx.fillStyle = '#fff';
            ctx.fillRect(player.x + 10, player.y + 12, 8, 8);
            ctx.fillRect(player.x + 32, player.y + 12, 8, 8);
            
            ctx.fillStyle = '#e74c3c';
            for (const o of obstacles) {
                ctx.fillRect(o.x, o.y, o.w, o.h);
            }
        }
        
        function gameOver() {
            playing = false;
            document.getElementById('finalScore').textContent = score;
            document.getElementById('gameOver').classList.add('show');
            document.getElementById('tap').style.display = 'none';
        }
        
        function restart() {
            playing = true;
            score = 0;
            speed = 6;
            obstacles = [];
            player.y = groundY - player.h;
            player.vy = 0;
            document.getElementById('score').textContent = '0';
            document.getElementById('gameOver').classList.remove('show');
            document.getElementById('tap').style.display = 'block';
        }
        
        function loop() { update(); draw(); requestAnimationFrame(loop); }
        loop();
    </script>
</body>
</html>'''
    },
    
    "🛡️ Game Guardian": {
        "Script Básico com Menu": '''--[[
    Game Guardian Script Básico
    Use apenas para fins educacionais!
]]

gg.setVisible(false)
gg.toast("Script carregado!")

local running = true

function hack_money()
    local input = gg.prompt({"Dinheiro atual:", "Novo valor:"}, {0, 999999}, {"number", "number"})
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
            gg.toast("Não encontrado ou muitos resultados")
        end
    end
end

function hack_health()
    local input = gg.prompt({"Vida atual:", "Nova vida:"}, {100, 9999}, {"number", "number"})
    if input then
        gg.clearResults()
        gg.setRanges(gg.REGION_ANONYMOUS)
        gg.searchNumber(input[1], gg.TYPE_FLOAT)
        local count = gg.getResultsCount()
        if count > 0 and count < 500 then
            local r = gg.getResults(count)
            for i,v in ipairs(r) do r[i].value = input[2] end
            gg.setValues(r)
            gg.toast("Vida alterada!")
        end
    end
end

function speed_hack()
    local speeds = {0.5, 1, 2, 3, 5}
    local choice = gg.choice({"0.5x Lento", "1x Normal", "2x", "3x", "5x"}, nil, "Velocidade")
    if choice then
        gg.setSpeed(speeds[choice])
        gg.toast("Velocidade: " .. speeds[choice] .. "x")
    end
end

function freeze_values()
    local count = gg.getResultsCount()
    if count > 0 then
        local r = gg.getResults(count)
        for i,v in ipairs(r) do r[i].freeze = true end
        gg.addListItems(r)
        gg.toast("Valores congelados!")
    else
        gg.toast("Faça uma busca primeiro!")
    end
end

function main_menu()
    local menu = gg.choice({
        "💰 Hack Dinheiro",
        "❤️ Hack Vida", 
        "⚡ Speed Hack",
        "❄️ Congelar Valores",
        "🧹 Limpar",
        "❌ Sair"
    }, nil, "Menu Principal")
    
    if menu == 1 then hack_money()
    elseif menu == 2 then hack_health()
    elseif menu == 3 then speed_hack()
    elseif menu == 4 then freeze_values()
    elseif menu == 5 then gg.clearResults() gg.clearList() gg.toast("Limpo!")
    elseif menu == 6 then running = false gg.setSpeed(1) gg.toast("Até logo!")
    end
end

while running do
    if gg.isVisible() then
        gg.setVisible(false)
        main_menu()
    end
    gg.sleep(100)
end

os.exit()''',

        "Script Avançado Multi-função": '''--[[
    Game Guardian Script Avançado
    Autor: ScriptMaster AI
]]

gg.setVisible(false)

local Config = { version = "2.0", safeMode = true }

-- Utilitários
local function toast(msg) gg.toast(msg) end
local function alert(msg) gg.alert(msg, "OK") end
local function confirm(msg) return gg.alert(msg, "Sim", "Não") == 1 end

-- Busca genérica
local function search(value, type, ranges)
    ranges = ranges or gg.REGION_ANONYMOUS
    type = type or gg.TYPE_DWORD
    gg.clearResults()
    gg.setRanges(ranges)
    gg.searchNumber(value, type)
    return gg.getResultsCount()
end

-- Editar resultados
local function editResults(newValue, maxResults)
    maxResults = maxResults or 500
    local count = gg.getResultsCount()
    if count > 0 and count <= maxResults then
        local r = gg.getResults(count)
        for i,v in ipairs(r) do r[i].value = newValue end
        gg.setValues(r)
        return true, count
    end
    return false, count
end

-- Hacks
local function hackResources()
    local types = {"Dinheiro", "Gemas", "Energia", "Tickets"}
    local choice = gg.choice(types, nil, "Tipo de Recurso")
    if not choice then return end
    
    local input = gg.prompt({types[choice] .. " atual:", "Novo valor:"}, {"0", "999999"}, {"number", "number"})
    if input then
        if search(tonumber(input[1]), gg.TYPE_DWORD) > 0 then
            local ok, count = editResults(tonumber(input[2]))
            if ok then toast("Editados " .. count .. " valores!")
            else toast("Muitos resultados: " .. count) end
        else
            toast("Não encontrado!")
        end
    end
end

local function hackStats()
    local stats = {"Vida", "Mana", "Ataque", "Defesa", "Velocidade"}
    local choice = gg.choice(stats, nil, "Tipo de Stat")
    if not choice then return end
    
    local input = gg.prompt({stats[choice] .. " atual:", "Novo valor:"}, {"100", "9999"}, {"number", "number"})
    if input then
        -- Tenta como FLOAT primeiro (mais comum para stats)
        if search(tonumber(input[1]), gg.TYPE_FLOAT) > 0 then
            editResults(tonumber(input[2]))
            toast(stats[choice] .. " modificado!")
        elseif search(tonumber(input[1]), gg.TYPE_DWORD) > 0 then
            editResults(tonumber(input[2]))
            toast(stats[choice] .. " modificado!")
        else
            toast("Não encontrado!")
        end
    end
end

local function speedControl()
    local speeds = {0.5, 1, 1.5, 2, 3, 5, 10}
    local labels = {"0.5x", "1x Normal", "1.5x", "2x", "3x", "5x", "10x"}
    local choice = gg.choice(labels, nil, "Velocidade")
    if choice then
        gg.setSpeed(speeds[choice])
        toast("Velocidade: " .. labels[choice])
    end
end

local function advancedSearch()
    local menu = gg.choice({
        "Busca Simples",
        "Busca por Faixa",
        "Busca Grupo",
        "Refinar Busca",
        "Editar Resultados"
    }, nil, "Busca Avançada")
    
    if menu == 1 then
        local input = gg.prompt({"Valor:", "Tipo (1=INT, 2=FLOAT):"}, {"0", "1"}, {"text", "number"})
        if input then
            local types = {gg.TYPE_DWORD, gg.TYPE_FLOAT}
            local count = search(input[1], types[tonumber(input[2])] or gg.TYPE_DWORD, gg.REGION_ANONYMOUS | gg.REGION_OTHER)
            toast("Encontrados: " .. count)
        end
        
    elseif menu == 2 then
        local input = gg.prompt({"Mínimo:", "Máximo:"}, {"0", "1000"}, {"number", "number"})
        if input then
            local range = input[1] .. "~" .. input[2]
            local count = search(range, gg.TYPE_DWORD)
            toast("Encontrados: " .. count)
        end
        
    elseif menu == 3 then
        local input = gg.prompt({"Valores (separados por ;):"}, {"100;200;300"}, {"text"})
        if input then
            local count = search(input[1], gg.TYPE_DWORD)
            toast("Grupos encontrados: " .. count)
        end
        
    elseif menu == 4 then
        local input = gg.prompt({"Novo valor:"}, {"0"}, {"text"})
        if input then
            gg.refineNumber(input[1], gg.TYPE_DWORD)
            toast("Refinado: " .. gg.getResultsCount())
        end
        
    elseif menu == 5 then
        local count = gg.getResultsCount()
        if count == 0 then toast("Faça uma busca primeiro!") return end
        
        local input = gg.prompt({"Novo valor:"}, {"999999"}, {"text"})
        if input then
            editResults(input[1])
            toast("Valores editados!")
        end
    end
end

local function freezeMenu()
    local menu = gg.choice({
        "Congelar Resultados",
        "Descongelar Tudo",
        "Limpar Lista"
    }, nil, "Congelamento")
    
    if menu == 1 then
        local count = gg.getResultsCount()
        if count > 0 then
            local r = gg.getResults(count)
            for i,v in ipairs(r) do r[i].freeze = true end
            gg.addListItems(r)
            toast("Congelados: " .. count)
        end
        
    elseif menu == 2 then
        local list = gg.getListItems()
        for i,v in ipairs(list) do list[i].freeze = false end
        gg.setValues(list)
        gg.clearList()
        toast("Descongelado!")
        
    elseif menu == 3 then
        gg.clearList()
        toast("Lista limpa!")
    end
end

-- Menu Principal
local running = true

local function mainMenu()
    local menu = gg.choice({
        "💰 Hack Recursos",
        "📊 Hack Stats",
        "⚡ Speed Hack",
        "🔍 Busca Avançada",
        "❄️ Congelamento",
        "🧹 Limpar Tudo",
        "ℹ️ Sobre",
        "❌ Sair"
    }, nil, "ScriptMaster v" .. Config.version)
    
    if menu == 1 then hackResources()
    elseif menu == 2 then hackStats()
    elseif menu == 3 then speedControl()
    elseif menu == 4 then advancedSearch()
    elseif menu == 5 then freezeMenu()
    elseif menu == 6 then gg.clearResults() gg.clearList() gg.setSpeed(1) toast("Tudo limpo!")
    elseif menu == 7 then alert("ScriptMaster GG v" .. Config.version .. "\\n\\nCriado com ScriptMaster AI\\nUse com responsabilidade!")
    elseif menu == 8 then
        if confirm("Deseja sair?") then
            running = false
            gg.setSpeed(1)
            toast("Até logo!")
        end
    end
end

toast("Script iniciado!")
while running do
    if gg.isVisible() then
        gg.setVisible(false)
        mainMenu()
    end
    gg.sleep(100)
end
os.exit()'''
    },
    
    "🎮 Godot 4.x": {
        "Player 2D Completo": '''extends CharacterBody2D
## Player 2D para Godot 4.x

@export var speed: float = 300.0
@export var jump_velocity: float = -400.0
@export var acceleration: float = 1500.0
@export var friction: float = 1200.0

var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")
var jumps_left: int = 2
var max_jumps: int = 2

@onready var sprite = $AnimatedSprite2D

func _physics_process(delta):
    # Gravidade
    if not is_on_floor():
        velocity.y += gravity * delta
    else:
        jumps_left = max_jumps
    
    # Pulo
    if Input.is_action_just_pressed("ui_accept") and jumps_left > 0:
        velocity.y = jump_velocity
        jumps_left -= 1
    
    # Movimento
    var direction = Input.get_axis("ui_left", "ui_right")
    
    if direction:
        velocity.x = move_toward(velocity.x, direction * speed, acceleration * delta)
        sprite.flip_h = direction < 0
        if is_on_floor():
            sprite.play("run")
    else:
        velocity.x = move_toward(velocity.x, 0, friction * delta)
        if is_on_floor():
            sprite.play("idle")
    
    if not is_on_floor():
        if velocity.y < 0:
            sprite.play("jump")
        else:
            sprite.play("fall")
    
    move_and_slide()

func take_damage(amount: int):
    print("Dano: ", amount)
''',
        
        "Sistema de Inventário": '''extends Node
class_name InventorySystem

signal inventory_changed
signal item_used(item_id: String)

var items: Dictionary = {}
var max_slots: int = 20

func add_item(item_id: String, quantity: int = 1) -> bool:
    if items.has(item_id):
        items[item_id] += quantity
    elif items.size() < max_slots:
        items[item_id] = quantity
    else:
        return false
    
    inventory_changed.emit()
    return true

func remove_item(item_id: String, quantity: int = 1) -> bool:
    if not items.has(item_id):
        return false
    
    items[item_id] -= quantity
    
    if items[item_id] <= 0:
        items.erase(item_id)
    
    inventory_changed.emit()
    return true

func use_item(item_id: String) -> bool:
    if has_item(item_id):
        item_used.emit(item_id)
        remove_item(item_id)
        return true
    return false

func has_item(item_id: String, quantity: int = 1) -> bool:
    return items.get(item_id, 0) >= quantity

func get_quantity(item_id: String) -> int:
    return items.get(item_id, 0)

func clear():
    items.clear()
    inventory_changed.emit()

func save() -> Dictionary:
    return items.duplicate()

func load(data: Dictionary):
    items = data.duplicate()
    inventory_changed.emit()
'''
    },
    
    "🤖 Discord Bot": {
        "Bot Básico com Slash": '''import discord
from discord import app_commands
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} online!")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} comandos sincronizados")
    except Exception as e:
        print(f"Erro: {e}")

@bot.tree.command(name="ping", description="Mostra a latência")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! {round(bot.latency * 1000)}ms")

@bot.tree.command(name="avatar", description="Mostra o avatar")
async def avatar(interaction: discord.Interaction, membro: discord.Member = None):
    membro = membro or interaction.user
    embed = discord.Embed(title=f"Avatar de {membro.name}", color=discord.Color.blue())
    embed.set_image(url=membro.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Info do servidor")
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=g.name, color=discord.Color.gold())
    embed.add_field(name="Membros", value=g.member_count)
    embed.add_field(name="Canais", value=len(g.channels))
    embed.add_field(name="Cargos", value=len(g.roles))
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    await interaction.response.send_message(embed=embed)

# Adicione seu token aqui
bot.run("SEU_TOKEN_AQUI")
'''
    },
    
    "🐍 Python": {
        "Web Scraper": '''import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Erro: {e}")
            return None
    
    def parse(self, html):
        return BeautifulSoup(html, 'html.parser')
    
    def scrape(self, url):
        html = self.fetch(url)
        if not html:
            return None
        
        soup = self.parse(html)
        
        data = {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'headings': [h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3'])],
            'links': [a.get('href') for a in soup.find_all('a', href=True)],
            'timestamp': datetime.now().isoformat()
        }
        
        return data
    
    def save_json(self, data, filename='scrape_result.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Salvo em {filename}")

# Uso
if __name__ == "__main__":
    scraper = WebScraper()
    result = scraper.scrape("https://example.com")
    if result:
        print(f"Título: {result['title']}")
        print(f"Links encontrados: {len(result['links'])}")
        scraper.save_json(result)
''',
        
        "API Flask": '''from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Banco de dados simples
db = {"users": [], "items": []}

@app.route('/')
def home():
    return jsonify({"message": "API Online!", "version": "1.0"})

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({"success": True, "data": db["users"]})

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"success": False, "error": "Nome obrigatório"}), 400
    
    user = {
        "id": len(db["users"]) + 1,
        "name": data["name"],
        "email": data.get("email", ""),
        "created_at": datetime.now().isoformat()
    }
    db["users"].append(user)
    return jsonify({"success": True, "data": user}), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in db["users"] if u["id"] == user_id), None)
    if user:
        return jsonify({"success": True, "data": user})
    return jsonify({"success": False, "error": "Não encontrado"}), 404

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db["users"] = [u for u in db["users"] if u["id"] != user_id]
    return jsonify({"success": True, "message": "Deletado"})

if __name__ == '__main__':
    print("API rodando em http://localhost:5000")
    app.run(debug=True, port=5000)
'''
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
        username = st.text_input("👤 Seu nome", key="login_user")
        access_code = st.text_input("🎫 Código VIP (opcional)", type="password", key="login_code")
        remember = st.checkbox("🔒 Manter conectado", value=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 ENTRAR", use_container_width=True, type="primary"):
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
                        st.success(f"VIP ativado por {days} dias!")
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
            if st.button("🆓 Modo Grátis", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.username = username or "Visitante"
                if remember:
                    save_session()
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 Recursos")
        st.markdown("""
        **🆓 GRATUITO:**
        - ✅ 4 gerações por dia
        - ✅ 10 mensagens de chat por dia
        - ✅ Templates básicos
        
        **👑 VIP:**
        - ✅ Gerações ILIMITADAS
        - ✅ Chat ILIMITADO
        - ✅ Todos os templates
        - ✅ Histórico salvo
        - ✅ Favoritos
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
    
    # Contador de uso
    st.markdown("---")
    can_gen, rem_gen = can_generate()
    can_ch, rem_ch = can_chat()
    
    if is_vip():
        st.success("✨ Uso ilimitado!")
    else:
        st.markdown(f"""
        <div class="usage-box">
            <p>⚡ Gerações: {st.session_state.usage_count}/{DAILY_LIMIT_FREE}</p>
            <p>💬 Chat: {st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}</p>
            <small>🔄 Renova à meia-noite</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Admin - Criar códigos
    if st.session_state.is_master:
        st.markdown("---")
        with st.expander("🎫 Criar Código VIP"):
            new_code = st.text_input("Nome do código")
            code_days = st.selectbox("Duração", ["1 dia", "7 dias", "30 dias", "Ilimitado"])
            
            if st.button("✨ Criar"):
                if new_code and new_code not in st.session_state.created_codes:
                    days_map = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                    st.session_state.created_codes[new_code] = {
                        "days": days_map[code_days],
                        "used": False
                    }
                    st.success(f"Código criado: {new_code}")
                    st.code(new_code)
    
    # Templates
    st.markdown("---")
    st.markdown("### 📚 Templates")
    
    for category, templates in TEMPLATES.items():
        with st.expander(category):
            for name, code in templates.items():
                if st.button(f"📄 {name}", key=f"t_{category}_{name}", use_container_width=True):
                    st.session_state.current_script = code
                    st.toast(f"✅ Template carregado!")
    
    # Sair
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True):
        clear_session()
        st.rerun()

# ====== ÁREA PRINCIPAL ======
st.markdown("""
<div class="header-premium">
    <h1>🎮 ScriptMaster AI Pro</h1>
    <p>Gerador de Scripts e Jogos com Inteligência Artificial</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 Gerar", "💬 Chat IA", "💻 Editor", "📚 Biblioteca", "📊 Stats"])

# ====== TAB GERAR ======
with tab1:
    st.markdown("### 🎯 Descreva o que você quer criar")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_area(
            "📝 Descrição:",
            placeholder="Ex: Crie um jogo de plataforma 2D em HTML5 para mobile com controles touch...",
            height=120
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
        ])
        nivel = st.select_slider("📊 Complexidade", ["Básico", "Médio", "Avançado"])
    
    can_gen, remaining = can_generate()
    
    if not can_gen:
        st.warning(f"⚠️ Limite diário atingido! Volte amanhã ou faça upgrade para VIP.")
    
    if st.button("⚡ GERAR CÓDIGO", use_container_width=True, type="primary", disabled=not can_gen):
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
1. Código 100% funcional e pronto para usar
2. Bem comentado em português
3. Seguir melhores práticas
4. Se for jogo mobile HTML5: usar touch events, viewport correto, meta tags para PWA
5. Se for Game Guardian: usar gg.* API corretamente
6. Retorne APENAS o código, sem markdown ou explicações extras."""

                    response = model.generate_content(system_prompt)
                    codigo = response.text
                    
                    # Limpar markdown
                    codigo = re.sub(r'^```[\w]*\n?', '', codigo)
                    codigo = re.sub(r'\n?```$', '', codigo)
                    codigo = codigo.strip()
                    
                    st.session_state.current_script = codigo
                    use_generation()
                    
                    st.success("✅ Código gerado!")
                    
                    lang, ext = detect_language(codigo)
                    st.code(codigo, language=lang)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.download_button("📥 Download", codigo, f"script{ext}", use_container_width=True)
                    with col2:
                        if st.button("💾 Salvar", use_container_width=True):
                            st.session_state.saved_scripts.append({
                                "name": f"Script_{len(st.session_state.saved_scripts)+1}{ext}",
                                "code": codigo,
                                "date": datetime.now().strftime("%d/%m %H:%M")
                            })
                            save_session()
                            st.success("Salvo!")
                    with col3:
                        if st.button("⭐ Favoritar", use_container_width=True):
                            st.session_state.favorites.append({
                                "name": f"Fav_{len(st.session_state.favorites)+1}{ext}",
                                "code": codigo,
                                "date": datetime.now().strftime("%d/%m %H:%M")
                            })
                            save_session()
                            st.success("Favoritado!")
                    
                except Exception as e:
                    st.error(f"Erro: {e}")

# ====== TAB CHAT ======
with tab2:
    st.markdown("### 💬 Chat com IA")
    
    # Mostrar histórico
    chat_container = st.container()
    
    with chat_container:
        for idx, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.markdown(f"""
                    <div class="chat-user">
                        <strong>Você:</strong><br>{msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("🗑️", key=f"del_msg_{idx}"):
                        st.session_state.chat_history.pop(idx)
                        save_session()
                        st.rerun()
            else:
                st.markdown(f"""
                <div class="chat-assistant">
                    <strong>🤖 IA:</strong><br>{msg["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Botões de ação
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button("📋", key=f"copy_{idx}", help="Copiar"):
                        st.code(msg["content"])
                with col2:
                    if st.button("🗑️", key=f"del_ai_{idx}", help="Deletar"):
                        st.session_state.chat_history.pop(idx)
                        save_session()
                        st.rerun()
    
    st.markdown("---")
    
    # Input
    can_ch, remaining_ch = can_chat()
    
    if not can_ch:
        st.warning("⚠️ Limite de chat atingido! Volte amanhã.")
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("💭 Digite sua mensagem:", key="chat_input", disabled=not can_ch)
    with col2:
        send = st.button("📤", disabled=not can_ch or not user_input, type="primary")
    
    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("Pensando..."):
            try:
                model = get_model()
                
                # Contexto do chat
                context = "\n".join([
                    f"{'Usuário' if m['role']=='user' else 'Assistente'}: {m['content']}"
                    for m in st.session_state.chat_history[-10:]
                ])
                
                response = model.generate_content(f"""Você é um assistente de programação expert.
Responda de forma clara e útil.

Conversa anterior:
{context}

Responda à última mensagem do usuário.""")
                
                ai_response = response.text
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                use_chat()
                save_session()
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro: {e}")
    
    # Limpar chat
    if st.button("🧹 Limpar Chat"):
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
            filename = st.text_input("📄 Nome", value=f"script{ext}")
        with col2:
            st.download_button("📥 Download", st.session_state.current_script, filename, use_container_width=True)
        
        new_code = st.text_area("✏️ Código:", st.session_state.current_script, height=400)
        st.session_state.current_script = new_code
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Salvar na Biblioteca", use_container_width=True):
                st.session_state.saved_scripts.append({
                    "name": filename,
                    "code": new_code,
                    "date": datetime.now().strftime("%d/%m %H:%M")
                })
                save_session()
                st.success("Salvo!")
        with col2:
            if st.button("⭐ Favoritar", use_container_width=True):
                st.session_state.favorites.append({
                    "name": filename,
                    "code": new_code,
                    "date": datetime.now().strftime("%d/%m %H:%M")
                })
                save_session()
                st.success("Favoritado!")
        with col3:
            if st.button("🗑️ Limpar", use_container_width=True):
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
                with st.expander(f"📄 {script['name']} - {script.get('date', '')}"):
                    st.code(script['code'][:500] + "..." if len(script['code']) > 500 else script['code'])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("📋 Carregar", key=f"load_{idx}"):
                            st.session_state.current_script = script['code']
                            st.success("Carregado!")
                    with col2:
                        st.download_button("📥", script['code'], script['name'], key=f"dl_{idx}")
                    with col3:
                        if st.button("🗑️", key=f"del_{idx}"):
                            real_idx = len(st.session_state.saved_scripts) - 1 - idx
                            st.session_state.saved_scripts.pop(real_idx)
                            save_session()
                            st.rerun()
        else:
            st.info("Nenhum script salvo ainda!")
    
    with tab_favs:
        if st.session_state.favorites:
            for idx, fav in enumerate(reversed(st.session_state.favorites)):
                with st.expander(f"⭐ {fav['name']} - {fav.get('date', '')}"):
                    st.code(fav['code'][:500] + "..." if len(fav['code']) > 500 else fav['code'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 Carregar", key=f"loadf_{idx}"):
                            st.session_state.current_script = fav['code']
                            st.success("Carregado!")
                    with col2:
                        if st.button("🗑️ Remover", key=f"delf_{idx}"):
                            real_idx = len(st.session_state.favorites) - 1 - idx
                            st.session_state.favorites.pop(real_idx)
                            save_session()
                            st.rerun()
        else:
            st.info("Nenhum favorito ainda!")

# ====== TAB STATS ======
with tab5:
    st.markdown("### 📊 Estatísticas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Scripts Salvos", len(st.session_state.saved_scripts))
    with col2:
        st.metric("⭐ Favoritos", len(st.session_state.favorites))
    with col3:
        st.metric("💬 Mensagens", len(st.session_state.chat_history))
    with col4:
        total_lines = sum(len(s['code'].split('\n')) for s in st.session_state.saved_scripts)
        st.metric("📏 Linhas Totais", total_lines)
    
    st.markdown("---")
    
    if is_vip():
        st.success("👑 Você é VIP! Uso ilimitado.")
    else:
        st.info(f"""
        📊 **Uso Hoje:**
        - Gerações: {st.session_state.usage_count}/{DAILY_LIMIT_FREE}
        - Chat: {st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}
        """)

# ====== RODAPÉ ======
st.markdown("---")
st.caption("💡 ScriptMaster AI Pro v3.0 | Desenvolvido por Rynamru")
