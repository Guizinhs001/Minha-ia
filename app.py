import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
import re
import base64

# Configuração
st.set_page_config(
    page_title="ScriptMaster AI Pro 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CÓDIGO MASTER (SECRETO)
MASTER_CODE = "GuizinhsDono"

# CSS Melhorado
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
        animation: gradient 3s ease infinite;
    }
    
    @keyframes gradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .header-premium h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .master-badge {
        background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.4);
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
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
    
    .code-stats {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-animation {
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# ====== SISTEMA DE LOGIN PERSISTENTE ======

def generate_token(username, is_master, vip_days=0):
    """Gera token de login"""
    data = f"{username}|{is_master}|{vip_days}|scriptmaster"
    return hashlib.md5(data.encode()).hexdigest()[:16]

def save_login(username, is_master, vip_until=None):
    """Salva login na URL"""
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
    for key in ['authenticated', 'is_master', 'vip_until', 'username', 'current_script', 'saved_scripts']:
        if key in st.session_state:
            if key == 'authenticated':
                st.session_state[key] = False
            elif key in ['saved_scripts']:
                st.session_state[key] = []
            else:
                st.session_state[key] = None

# Inicializar session state
default_states = {
    "authenticated": False,
    "is_master": False,
    "vip_until": None,
    "username": None,
    "current_script": "",
    "saved_scripts": [],
    "created_codes": {},
    "login_checked": False,
    "script_history": [],
    "favorites": [],
    "current_language": "python",
    "theme": "dark"
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
    st.error("❌ Chave API não configurada! Configure em Settings > Secrets")
    st.code("""
# Adicione no arquivo .streamlit/secrets.toml:
GEMINI_API_KEY = "sua_chave_aqui"
""")
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
    except Exception as e:
        st.error(f"Erro ao carregar modelos: {e}")
        return []

def detect_language(code):
    """Detecta a linguagem do código"""
    code_lower = code.lower()
    
    if 'extends' in code_lower and 'func' in code_lower:
        return 'gdscript', '.gd'
    elif 'using unityengine' in code_lower or 'monobehaviour' in code_lower:
        return 'csharp', '.cs'
    elif '<!doctype html>' in code_lower or '<html' in code_lower:
        return 'html', '.html'
    elif 'import react' in code_lower or 'const' in code_lower and '=>' in code_lower:
        return 'javascript', '.jsx'
    elif 'def ' in code_lower or 'import ' in code_lower:
        return 'python', '.py'
    elif 'select' in code_lower and 'from' in code_lower:
        return 'sql', '.sql'
    elif 'function' in code_lower or 'const' in code_lower or 'let' in code_lower:
        return 'javascript', '.js'
    else:
        return 'python', '.py'

def download_button_with_icon(label, data, filename, mime="text/plain"):
    """Botão de download customizado"""
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:{mime};base64,{b64}" download="{filename}">{label}</a>'
    return href

# ====== TEMPLATES EXPANDIDOS ======
TEMPLATES = {
    "🎮 Jogos": {
        "Godot - Player 2D Completo": {
            "code": '''extends CharacterBody2D

# Configurações do Player
const SPEED = 300.0
const JUMP_VELOCITY = -400.0
const ACCELERATION = 1500.0
const FRICTION = 1200.0
const AIR_RESISTANCE = 200.0

# Física
var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")
var is_jumping = false

# Referências
@onready var sprite = $AnimatedSprite2D
@onready var animation_player = $AnimationPlayer

func _ready():
    # Configuração inicial
    print("Player pronto!")

func _physics_process(delta):
    # Gravidade
    if not is_on_floor():
        velocity.y += gravity * delta
        velocity.x = move_toward(velocity.x, 0, AIR_RESISTANCE * delta)
    else:
        is_jumping = false
    
    # Pulo
    if Input.is_action_just_pressed("ui_up") and is_on_floor():
        velocity.y = JUMP_VELOCITY
        is_jumping = true
        play_animation("jump")
    
    # Movimento horizontal
    var direction = Input.get_axis("ui_left", "ui_right")
    
    if direction != 0:
        velocity.x = move_toward(velocity.x, direction * SPEED, ACCELERATION * delta)
        sprite.flip_h = direction < 0
        
        if is_on_floor() and not is_jumping:
            play_animation("run")
    else:
        velocity.x = move_toward(velocity.x, 0, FRICTION * delta)
        
        if is_on_floor() and not is_jumping:
            play_animation("idle")
    
    # Aplicar movimento
    move_and_slide()

func play_animation(anim_name):
    if sprite.animation != anim_name:
        sprite.play(anim_name)

# Função para receber dano
func take_damage(amount):
    print("Dano recebido: ", amount)
    play_animation("hurt")

# Função para coletar item
func collect_item(item):
    print("Item coletado: ", item)
''',
            "lang": "gdscript",
            "ext": ".gd"
        },
        
        "HTML5 - Jogo Completo com Score": {
            "code": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meu Jogo HTML5</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Arial', sans-serif;
        }
        
        #gameContainer {
            text-align: center;
        }
        
        canvas {
            border: 5px solid #fff;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: block;
            margin: 20px auto;
            background: #1a1a2e;
        }
        
        #score {
            color: white;
            font-size: 32px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 20px;
        }
        
        #controls {
            color: white;
            margin-top: 20px;
            font-size: 18px;
        }
        
        button {
            background: #fff;
            color: #667eea;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 25px;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s;
        }
        
        button:hover {
            transform: scale(1.1);
            box-shadow: 0 5px 15px rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <div id="score">Score: 0</div>
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div id="controls">
            <p>⬅️ A | D ➡️ | ESPAÇO para pular | Clique para começar</p>
            <button onclick="restartGame()">🔄 Reiniciar</button>
            <button onclick="pauseGame()">⏸️ Pausar</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Configurações do jogo
        let score = 0;
        let gameRunning = false;
        let gamePaused = false;
        let gameSpeed = 3;
        
        // Player
        const player = {
            x: 100,
            y: 450,
            width: 50,
            height: 50,
            color: '#00ff00',
            velocityY: 0,
            jumping: false,
            speed: 5
        };
        
        // Física
        const gravity = 0.8;
        const jumpPower = -15;
        const groundY = 550;
        
        // Obstáculos
        let obstacles = [];
        let obstacleTimer = 0;
        
        // Moedas
        let coins = [];
        let coinTimer = 0;
        
        // Partículas
        let particles = [];
        
        class Obstacle {
            constructor() {
                this.x = canvas.width;
                this.y = groundY - 50;
                this.width = 40;
                this.height = 50;
                this.color = '#ff0000';
                this.speed = gameSpeed;
            }
            
            update() {
                this.x -= this.speed;
            }
            
            draw() {
                ctx.fillStyle = this.color;
                ctx.fillRect(this.x, this.y, this.width, this.height);
                
                // Sombra
                ctx.fillStyle = 'rgba(0,0,0,0.3)';
                ctx.fillRect(this.x + 5, this.y + this.height, this.width - 10, 10);
            }
        }
        
        class Coin {
            constructor() {
                this.x = canvas.width;
                this.y = Math.random() * 300 + 100;
                this.radius = 15;
                this.color = '#FFD700';
                this.speed = gameSpeed;
                this.collected = false;
            }
            
            update() {
                this.x -= this.speed;
            }
            
            draw() {
                if (!this.collected) {
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Brilho
                    ctx.fillStyle = '#FFF';
                    ctx.beginPath();
                    ctx.arc(this.x - 5, this.y - 5, 5, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
        }
        
        class Particle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 5;
                this.vy = (Math.random() - 0.5) * 5;
                this.radius = Math.random() * 3 + 2;
                this.color = color;
                this.life = 30;
            }
            
            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.life--;
            }
            
            draw() {
                ctx.globalAlpha = this.life / 30;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }
        
        function createParticles(x, y, color, count = 10) {
            for (let i = 0; i < count; i++) {
                particles.push(new Particle(x, y, color));
            }
        }
        
        function updatePlayer() {
            // Física
            player.velocityY += gravity;
            player.y += player.velocityY;
            
            // Colisão com chão
            if (player.y + player.height > groundY) {
                player.y = groundY - player.height;
                player.velocityY = 0;
                player.jumping = false;
            }
            
            // Limites laterais
            if (player.x < 0) player.x = 0;
            if (player.x + player.width > canvas.width) {
                player.x = canvas.width - player.width;
            }
        }
        
        function drawPlayer() {
            // Corpo
            ctx.fillStyle = player.color;
            ctx.fillRect(player.x, player.y, player.width, player.height);
            
            // Olhos
            ctx.fillStyle = '#FFF';
            ctx.fillRect(player.x + 10, player.y + 10, 10, 10);
            ctx.fillRect(player.x + 30, player.y + 10, 10, 10);
            
            // Pupilas
            ctx.fillStyle = '#000';
            ctx.fillRect(player.x + 15, player.y + 15, 5, 5);
            ctx.fillRect(player.x + 35, player.y + 15, 5, 5);
            
            // Sombra
            ctx.fillStyle = 'rgba(0,0,0,0.3)';
            ctx.fillRect(player.x + 5, groundY + 5, player.width - 10, 10);
        }
        
        function checkCollisions() {
            // Colisão com obstáculos
            for (let obs of obstacles) {
                if (player.x < obs.x + obs.width &&
                    player.x + player.width > obs.x &&
                    player.y < obs.y + obs.height &&
                    player.y + player.height > obs.y) {
                    gameOver();
                }
            }
            
            // Colisão com moedas
            for (let coin of coins) {
                if (!coin.collected) {
                    const dist = Math.hypot(
                        player.x + player.width/2 - coin.x,
                        player.y + player.height/2 - coin.y
                    );
                    
                    if (dist < player.width/2 + coin.radius) {
                        coin.collected = true;
                        score += 10;
                        updateScore();
                        createParticles(coin.x, coin.y, '#FFD700', 15);
                    }
                }
            }
        }
        
        function updateScore() {
            document.getElementById('score').textContent = `Score: ${score}`;
            
            // Aumentar dificuldade
            if (score % 100 === 0 && score > 0) {
                gameSpeed += 0.5;
            }
        }
        
        function gameOver() {
            gameRunning = false;
            alert(`Game Over! Score final: ${score}`);
        }
        
        function restartGame() {
            score = 0;
            gameSpeed = 3;
            player.x = 100;
            player.y = 450;
            player.velocityY = 0;
            obstacles = [];
            coins = [];
            particles = [];
            updateScore();
            gameRunning = true;
            gamePaused = false;
        }
        
        function pauseGame() {
            gamePaused = !gamePaused;
            document.querySelector('button:nth-of-type(2)').textContent = 
                gamePaused ? '▶️ Continuar' : '⏸️ Pausar';
        }
        
        function gameLoop() {
            if (!gameRunning || gamePaused) {
                requestAnimationFrame(gameLoop);
                return;
            }
            
            // Limpar canvas
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Desenhar chão
            ctx.fillStyle = '#654321';
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            
            // Grama
            ctx.fillStyle = '#228B22';
            ctx.fillRect(0, groundY, canvas.width, 10);
            
            // Atualizar e desenhar player
            updatePlayer();
            drawPlayer();
            
            // Spawnar obstáculos
            obstacleTimer++;
            if (obstacleTimer > 100) {
                obstacles.push(new Obstacle());
                obstacleTimer = 0;
            }
            
            // Spawnar moedas
            coinTimer++;
            if (coinTimer > 80) {
                coins.push(new Coin());
                coinTimer = Math.random() * 30;
            }
            
            // Atualizar obstáculos
            for (let i = obstacles.length - 1; i >= 0; i--) {
                obstacles[i].update();
                obstacles[i].draw();
                
                if (obstacles[i].x + obstacles[i].width < 0) {
                    obstacles.splice(i, 1);
                    score += 5;
                    updateScore();
                }
            }
            
            // Atualizar moedas
            for (let i = coins.length - 1; i >= 0; i--) {
                coins[i].update();
                coins[i].draw();
                
                if (coins[i].x + coins[i].radius < 0) {
                    coins.splice(i, 1);
                }
            }
            
            // Atualizar partículas
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update();
                particles[i].draw();
                
                if (particles[i].life <= 0) {
                    particles.splice(i, 1);
                }
            }
            
            // Verificar colisões
            checkCollisions();
            
            requestAnimationFrame(gameLoop);
        }
        
        // Controles
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !player.jumping) {
                player.velocityY = jumpPower;
                player.jumping = true;
            }
            
            if (e.code === 'KeyA') {
                player.x -= player.speed * 2;
            }
            
            if (e.code === 'KeyD') {
                player.x += player.speed * 2;
            }
        });
        
        canvas.addEventListener('click', () => {
            if (!gameRunning) {
                restartGame();
            } else if (!player.jumping) {
                player.velocityY = jumpPower;
                player.jumping = true;
            }
        });
        
        // Touch para mobile
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            if (!gameRunning) {
                restartGame();
            } else if (!player.jumping) {
                player.velocityY = jumpPower;
                player.jumping = true;
            }
        });
        
        // Iniciar
        gameLoop();
    </script>
</body>
</html>
''',
            "lang": "html",
            "ext": ".html"
        },
        
        "Unity - Sistema de Inventário": {
            "code": '''using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class Item
{
    public string itemName;
    public Sprite icon;
    public int maxStack = 99;
    public ItemType type;
    
    public enum ItemType
    {
        Weapon,
        Consumable,
        Material,
        Quest
    }
}

[System.Serializable]
public class InventorySlot
{
    public Item item;
    public int quantity;
    
    public InventorySlot(Item _item, int _quantity)
    {
        item = _item;
        quantity = _quantity;
    }
    
    public bool CanAddItem(Item _item)
    {
        return item == _item && quantity < item.maxStack;
    }
}

public class InventorySystem : MonoBehaviour
{
    public static InventorySystem Instance;
    
    public List<InventorySlot> inventorySlots = new List<InventorySlot>();
    public int maxSlots = 20;
    
    // Eventos
    public delegate void OnInventoryChanged();
    public event OnInventoryChanged onInventoryChangedCallback;
    
    void Awake()
    {
        if (Instance == null)
            Instance = this;
        else
            Destroy(gameObject);
    }
    
    public bool AddItem(Item item, int quantity = 1)
    {
        // Verificar se já existe no inventário
        foreach (InventorySlot slot in inventorySlots)
        {
            if (slot.item == item && slot.quantity < item.maxStack)
            {
                int amountToAdd = Mathf.Min(quantity, item.maxStack - slot.quantity);
                slot.quantity += amountToAdd;
                quantity -= amountToAdd;
                
                if (quantity <= 0)
                {
                    onInventoryChangedCallback?.Invoke();
                    return true;
                }
            }
        }
        
        // Adicionar em novo slot
        while (quantity > 0 && inventorySlots.Count < maxSlots)
        {
            int amountToAdd = Mathf.Min(quantity, item.maxStack);
            inventorySlots.Add(new InventorySlot(item, amountToAdd));
            quantity -= amountToAdd;
        }
        
        onInventoryChangedCallback?.Invoke();
        return quantity <= 0;
    }
    
    public bool RemoveItem(Item item, int quantity = 1)
    {
        for (int i = inventorySlots.Count - 1; i >= 0; i--)
        {
            if (inventorySlots[i].item == item)
            {
                if (inventorySlots[i].quantity > quantity)
                {
                    inventorySlots[i].quantity -= quantity;
                    onInventoryChangedCallback?.Invoke();
                    return true;
                }
                else
                {
                    quantity -= inventorySlots[i].quantity;
                    inventorySlots.RemoveAt(i);
                    
                    if (quantity <= 0)
                    {
                        onInventoryChangedCallback?.Invoke();
                        return true;
                    }
                }
            }
        }
        
        onInventoryChangedCallback?.Invoke();
        return quantity <= 0;
    }
    
    public int GetItemCount(Item item)
    {
        int count = 0;
        foreach (InventorySlot slot in inventorySlots)
        {
            if (slot.item == item)
                count += slot.quantity;
        }
        return count;
    }
    
    public bool HasItem(Item item, int quantity = 1)
    {
        return GetItemCount(item) >= quantity;
    }
    
    public void SortInventory()
    {
        inventorySlots.Sort((a, b) => a.item.itemName.CompareTo(b.item.itemName));
        onInventoryChangedCallback?.Invoke();
    }
    
    public void ClearInventory()
    {
        inventorySlots.Clear();
        onInventoryChangedCallback?.Invoke();
    }
}
''',
            "lang": "csharp",
            "ext": ".cs"
        }
    },
    
    "🤖 Bots": {
        "Discord Bot Avançado": {
            "code": '''import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
from datetime import datetime, timedelta

# Configuração
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Sistema de economia
class Economy:
    def __init__(self):
        self.data_file = "economy.json"
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def get_balance(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {"balance": 0, "daily_last": None}
        return self.data[user_id]["balance"]
    
    def add_money(self, user_id, amount):
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {"balance": 0, "daily_last": None}
        self.data[user_id]["balance"] += amount
        self.save_data()
    
    def remove_money(self, user_id, amount):
        user_id = str(user_id)
        balance = self.get_balance(user_id)
        if balance >= amount:
            self.data[user_id]["balance"] -= amount
            self.save_data()
            return True
        return False
    
    def can_claim_daily(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data:
            return True
        
        last_claim = self.data[user_id].get("daily_last")
        if not last_claim:
            return True
        
        last_date = datetime.fromisoformat(last_claim)
        return datetime.now() - last_date > timedelta(hours=24)
    
    def claim_daily(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {"balance": 0, "daily_last": None}
        
        self.data[user_id]["daily_last"] = datetime.now().isoformat()
        self.save_data()

economy = Economy()

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} está online!')
    print(f'📊 Servidores: {len(bot.guilds)}')
    print(f'👥 Usuários: {len(bot.users)}')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidores | /help"
        )
    )
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} comandos slash sincronizados')
    except Exception as e:
        print(f'❌ Erro ao sincronizar: {e}')

@bot.event
async def on_member_join(member):
    """Mensagem de boas-vindas"""
    embed = discord.Embed(
        title="👋 Bem-vindo!",
        description=f"Olá {member.mention}! Bem-vindo ao **{member.guild.name}**!",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="📅 Conta criada", value=member.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="👥 Membro", value=f"#{member.guild.member_count}")
    embed.set_footer(text=f"ID: {member.id}")
    
    channel = member.guild.system_channel
    if channel:
        await channel.send(embed=embed)

# Comandos Slash
@tree.command(name="ping", description="Verifica a latência do bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: **{latency}ms**",
        color=discord.Color.blue()
    )
    
    if latency < 100:
        embed.add_field(name="Status", value="✅ Excelente")
    elif latency < 200:
        embed.add_field(name="Status", value="⚠️ Bom")
    else:
        embed.add_field(name="Status", value="❌ Lento")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="avatar", description="Mostra o avatar de um usuário")
async def avatar(interaction: discord.Interaction, membro: discord.Member = None):
    membro = membro or interaction.user
    
    embed = discord.Embed(
        title=f"Avatar de {membro.name}",
        color=discord.Color.purple()
    )
    embed.set_image(url=membro.display_avatar.url)
    embed.add_field(name="Link", value=f"[Clique aqui]({membro.display_avatar.url})")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="serverinfo", description="Informações do servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    
    embed = discord.Embed(
        title=f"📊 {guild.name}",
        color=discord.Color.gold()
    )
    
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👑 Dono", value=guild.owner.mention)
    embed.add_field(name="👥 Membros", value=guild.member_count)
    embed.add_field(name="💬 Canais", value=len(guild.channels))
    embed.add_field(name="😀 Emojis", value=len(guild.emojis))
    embed.add_field(name="🎭 Cargos", value=len(guild.roles))
    embed.add_field(name="📅 Criado em", value=guild.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="🔒 Nível de verificação", value=str(guild.verification_level))
    embed.add_field(name="📈 Boost", value=f"Nível {guild.premium_tier} ({guild.premium_subscription_count} boosts)")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="userinfo", description="Informações de um usuário")
async def userinfo(interaction: discord.Interaction, membro: discord.Member = None):
    membro = membro or interaction.user
    
    embed = discord.Embed(
        title=f"👤 {membro.name}",
        color=membro.color
    )
    
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="🆔 ID", value=membro.id)
    embed.add_field(name="📛 Nome", value=membro.display_name)
    embed.add_field(name="📅 Conta criada", value=membro.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="📥 Entrou em", value=membro.joined_at.strftime("%d/%m/%Y"))
    embed.add_field(name="🎭 Cargos", value=len(membro.roles) - 1)
    embed.add_field(name="🤖 Bot?", value="Sim" if membro.bot else "Não")
    
    await interaction.response.send_message(embed=embed)

# Sistema de Economia
@tree.command(name="saldo", description="Verifica seu saldo")
async def saldo(interaction: discord.Interaction):
    balance = economy.get_balance(interaction.user.id)
    
    embed = discord.Embed(
        title="💰 Seu Saldo",
        description=f"Você possui **{balance:,}** moedas!",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Use /daily para ganhar moedas diárias!")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="daily", description="Resgata recompensa diária")
async def daily(interaction: discord.Interaction):
    if economy.can_claim_daily(interaction.user.id):
        reward = 100
        economy.add_money(interaction.user.id, reward)
        economy.claim_daily(interaction.user.id)
        
        embed = discord.Embed(
            title="🎁 Recompensa Diária",
            description=f"Você ganhou **{reward}** moedas!",
            color=discord.Color.green()
        )
        embed.add_field(name="💰 Novo saldo", value=f"{economy.get_balance(interaction.user.id):,} moedas")
        embed.set_footer(text="Volte amanhã para mais!")
        
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="⏰ Já Resgatado",
            description="Você já resgatou sua recompensa hoje!",
            color=discord.Color.red()
        )
        embed.set_footer(text="Volte em 24 horas")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="rank", description="Ranking de economia")
async def rank(interaction: discord.Interaction):
    # Ordenar usuários por saldo
    sorted_users = sorted(
        economy.data.items(),
        key=lambda x: x[1]["balance"],
        reverse=True
    )[:10]
    
    embed = discord.Embed(
        title="🏆 Top 10 Mais Ricos",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (user_id, data) in enumerate(sorted_users):
        try:
            user = await bot.fetch_user(int(user_id))
            medal = medals[i] if i < 3 else f"{i+1}."
            embed.add_field(
                name=f"{medal} {user.name}",
                value=f"💰 {data['balance']:,} moedas",
                inline=False
            )
        except:
            continue
    
    await interaction.response.send_message(embed=embed)

# Comandos de Moderação
@tree.command(name="limpar", description="Limpa mensagens do chat")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar(interaction: discord.Interaction, quantidade: int):
    if quantidade > 100:
        await interaction.response.send_message("❌ Máximo 100 mensagens!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    deleted = await interaction.channel.purge(limit=quantidade)
    
    await interaction.followup.send(f"✅ {len(deleted)} mensagens deletadas!", ephemeral=True)

@tree.command(name="kick", description="Expulsa um membro")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
    await membro.kick(reason=motivo)
    
    embed = discord.Embed(
        title="👢 Membro Expulso",
        description=f"{membro.mention} foi expulso!",
        color=discord.Color.orange()
    )
    embed.add_field(name="Motivo", value=motivo)
    embed.add_field(name="Moderador", value=interaction.user.mention)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="ban", description="Bane um membro")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
    await membro.ban(reason=motivo)
    
    embed = discord.Embed(
        title="🔨 Membro Banido",
        description=f"{membro.mention} foi banido!",
        color=discord.Color.red()
    )
    embed.add_field(name="Motivo", value=motivo)
    embed.add_field(name="Moderador", value=interaction.user.mention)
    
    await interaction.response.send_message(embed=embed)

# Comandos de Diversão
@tree.command(name="coinflip", description="Cara ou coroa")
async def coinflip(interaction: discord.Interaction):
    import random
    result = random.choice(["Cara", "Coroa"])
    
    embed = discord.Embed(
        title="🪙 Cara ou Coroa",
        description=f"Resultado: **{result}**!",
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="dado", description="Rola um dado")
async def dado(interaction: discord.Interaction, lados: int = 6):
    import random
    
    if lados < 2:
        await interaction.response.send_message("❌ O dado precisa ter pelo menos 2 lados!", ephemeral=True)
        return
    
    result = random.randint(1, lados)
    
    embed = discord.Embed(
        title="🎲 Rolando Dado",
        description=f"Dado de {lados} lados: **{result}**!",
        color=discord.Color.green()
    )
    
    await interaction.response.send_message(embed=embed)

# Sistema de Tickets
ticket_channel_id = None  # Configure aqui o ID do canal de tickets

@tree.command(name="ticket", description="Abre um ticket de suporte")
async def ticket(interaction: discord.Interaction, motivo: str):
    guild = interaction.guild
    user = interaction.user
    
    # Criar canal privado
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    
    channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        overwrites=overwrites
    )
    
    embed = discord.Embed(
        title="🎫 Ticket Criado",
        description=f"Seu ticket foi criado em {channel.mention}!",
        color=discord.Color.green()
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Mensagem no canal do ticket
    ticket_embed = discord.Embed(
        title="🎫 Novo Ticket de Suporte",
        description=f"**Criado por:** {user.mention}\n**Motivo:** {motivo}",
        color=discord.Color.blue()
    )
    ticket_embed.set_footer(text="Use /close para fechar o ticket")
    
    await channel.send(embed=ticket_embed)

@tree.command(name="close", description="Fecha o ticket atual")
async def close_ticket(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message("🗑️ Fechando ticket em 5 segundos...")
        await asyncio.sleep(5)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("❌ Este não é um canal de ticket!", ephemeral=True)

# Handler de erros
@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Erro: {str(error)}", ephemeral=True)

# Rodar bot
if __name__ == "__main__":
    TOKEN = "SEU_TOKEN_AQUI"  # Coloque seu token aqui
    bot.run(TOKEN)
''',
            "lang": "python",
            "ext": ".py"
        },
        
        "Telegram Bot Completo": {
            "code": '''from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import logging
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Sistema de dados
class UserData:
    def __init__(self):
        self.data_file = "users.json"
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def get_user(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {
                "name": "",
                "points": 0,
                "joined_at": datetime.now().isoformat()
            }
            self.save_data()
        return self.data[user_id]
    
    def add_points(self, user_id, points):
        user_id = str(user_id)
        user = self.get_user(user_id)
        user["points"] += points
        self.save_data()

user_data = UserData()

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = user_data.get_user(user.id)
    user_info["name"] = user.first_name
    user_data.save_data()
    
    welcome_text = f"""
👋 Olá, {user.first_name}!

Bem-vindo ao bot de exemplo!

📚 Comandos disponíveis:
/start - Iniciar bot
/help - Ajuda
/menu - Menu principal
/pontos - Ver seus pontos
/rank - Ranking de usuários
/sobre - Sobre o bot

💡 Use /menu para ver todas as opções!
"""
    
    keyboard = [
        [InlineKeyboardButton("📚 Menu", callback_data="menu")],
        [InlineKeyboardButton("ℹ️ Ajuda", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *AJUDA DO BOT*

🔹 *Comandos Básicos:*
/start - Iniciar o bot
/help - Mostrar esta mensagem
/menu - Menu interativo

🔹 *Sistema de Pontos:*
/pontos - Ver seus pontos
/rank - Ver ranking
/daily - Ganhar pontos diários

🔹 *Interação:*
/echo <texto> - Repete sua mensagem
/clima <cidade> - Ver clima
/calcular <expressão> - Calculadora

🔹 *Diversão:*
/dado - Rolar dado
/moeda - Cara ou coroa
/quiz - Quiz aleatório

💡 Use os botões para navegar!
"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Voltar", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=reply_markup)

# Menu interativo
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = """
🎯 *MENU PRINCIPAL*

Escolha uma opção abaixo:
"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Pontos", callback_data="pontos"),
         InlineKeyboardButton("🏆 Ranking", callback_data="rank")],
        [InlineKeyboardButton("🎮 Jogos", callback_data="games"),
         InlineKeyboardButton("🛠️ Ferramentas", callback_data="tools")],
        [InlineKeyboardButton("ℹ️ Sobre", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(menu_text, parse_mode="Markdown", reply_markup=reply_markup)

# Sistema de pontos
async def pontos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = user_data.get_user(user.id)
    
    text = f"""
💰 *Seus Pontos*

Pontos atuais: *{user_info['points']}*
Membro desde: {datetime.fromisoformat(user_info['joined_at']).strftime('%d/%m/%Y')}

Use /daily para ganhar pontos diários!
"""
    
    await update.message.reply_text(text, parse_mode="Markdown")

# Ranking
async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ordenar usuários por pontos
    sorted_users = sorted(
        user_data.data.items(),
        key=lambda x: x[1]["points"],
        reverse=True
    )[:10]
    
    rank_text = "🏆 *TOP 10 RANKING*\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (user_id, data) in enumerate(sorted_users):
        medal = medals[i] if i < 3 else f"{i+1}."
        name = data.get("name", "Desconhecido")
        points = data.get("points", 0)
        rank_text += f"{medal} {name}: *{points}* pontos\n"
    
    await update.message.reply_text(rank_text, parse_mode="Markdown")

# Daily rewards
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    reward = 100
    user_data.add_points(user.id, reward)
    
    user_info = user_data.get_user(user.id)
    
    text = f"""
🎁 *Recompensa Diária*

Você ganhou *{reward}* pontos!

💰 Total: *{user_info['points']}* pontos
"""
    
    await update.message.reply_text(text, parse_mode="Markdown")

# Echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        message = " ".join(context.args)
        await update.message.reply_text(f"🔊 {message}")
    else:
        await update.message.reply_text("❌ Use: /echo <sua mensagem>")

# Calculadora
async def calcular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /calcular <expressão>\nExemplo: /calcular 2 + 2")
        return
    
    try:
        expression = " ".join(context.args)
        # Segurança básica
        allowed_chars = "0123456789+-*/() ."
        if not all(c in allowed_chars for c in expression):
            await update.message.reply_text("❌ Apenas números e operadores matemáticos são permitidos!")
            return
        
        result = eval(expression)
        await update.message.reply_text(f"🔢 Resultado: *{result}*", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao calcular: {str(e)}")

# Dado
async def dado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random
    result = random.randint(1, 6)
    
    dice_emoji = {
        1: "⚀",
        2: "⚁",
        3: "⚂",
        4: "⚃",
        5: "⚄",
        6: "⚅"
    }
    
    await update.message.reply_text(f"🎲 Você tirou: {dice_emoji[result]} *{result}*", parse_mode="Markdown")

# Moeda
async def moeda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random
    result = random.choice(["Cara", "Coroa"])
    emoji = "🪙" if result == "Cara" else "🎭"
    
    await update.message.reply_text(f"{emoji} Resultado: *{result}*!", parse_mode="Markdown")

# Quiz
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random
    
    perguntas = [
        {
            "pergunta": "Qual é a capital do Brasil?",
            "opcoes": ["São Paulo", "Brasília", "Rio de Janeiro", "Salvador"],
            "resposta": 1
        },
        {
            "pergunta": "Quanto é 5 x 7?",
            "opcoes": ["30", "35", "40", "45"],
            "resposta": 1
        },
        {
            "pergunta": "Qual é o maior planeta do sistema solar?",
            "opcoes": ["Terra", "Marte", "Júpiter", "Saturno"],
            "resposta": 2
        }
    ]
    
    quiz_data = random.choice(perguntas)
    
    text = f"❓ *{quiz_data['pergunta']}*"
    
    keyboard = []
    for i, opcao in enumerate(quiz_data['opcoes']):
        keyboard.append([InlineKeyboardButton(
            opcao,
            callback_data=f"quiz_{i}_{quiz_data['resposta']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

# Handler de callbacks (botões)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "menu":
        text = """
🎯 *MENU PRINCIPAL*

Escolha uma opção abaixo:
"""
        keyboard = [
            [InlineKeyboardButton("💰 Pontos", callback_data="pontos"),
             InlineKeyboardButton("🏆 Ranking", callback_data="rank")],
            [InlineKeyboardButton("🎮 Jogos", callback_data="games"),
             InlineKeyboardButton("🛠️ Ferramentas", callback_data="tools")],
            [InlineKeyboardButton("ℹ️ Sobre", callback_data="about")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    
    elif data == "pontos":
        user = query.from_user
        user_info = user_data.get_user(user.id)
        
        text = f"""
💰 *Seus Pontos*

Pontos atuais: *{user_info['points']}*
Membro desde: {datetime.fromisoformat(user_info['joined_at']).strftime('%d/%m/%Y')}

Use /daily para ganhar pontos diários!
"""
        keyboard = [[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    
    elif data == "games":
        text = """
🎮 *JOGOS DISPONÍVEIS*

/dado - Rolar um dado 🎲
/moeda - Cara ou coroa 🪙
/quiz - Quiz de perguntas ❓

Divirta-se!
"""
        keyboard = [[InlineKeyboardButton("🏠 Voltar", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    
    elif data.startswith("quiz_"):
        parts = data.split("_")
        escolha = int(parts[1])
        resposta_certa = int(parts[2])
        
        if escolha == resposta_certa:
            user_data.add_points(query.from_user.id, 10)
            text = "✅ *Correto!* Você ganhou 10 pontos! 🎉"
        else:
            text = "❌ *Errado!* Tente novamente!"
        
        await query.edit_message_text(text, parse_mode="Markdown")

# Handler de mensagens
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "oi" in text or "olá" in text or "ola" in text:
        await update.message.reply_text(f"👋 Olá, {update.effective_user.first_name}!")
    
    elif "tchau" in text or "até logo" in text:
        await update.message.reply_text("👋 Até logo! Volte sempre!")
    
    elif "obrigado" in text or "obrigada" in text:
        await update.message.reply_text("😊 De nada! Estou aqui para ajudar!")

# Handler de erros
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Erro: {context.error}")

# Main
def main():
    # Token do bot
    TOKEN = "SEU_TOKEN_AQUI"  # Coloque seu token aqui
    
    # Criar aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("pontos", pontos))
    application.add_handler(CommandHandler("rank", rank))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CommandHandler("calcular", calcular))
    application.add_handler(CommandHandler("dado", dado))
    application.add_handler(CommandHandler("moeda", moeda))
    application.add_handler(CommandHandler("quiz", quiz))
    
    # Callback queries (botões)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Mensagens de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Erros
    application.add_error_handler(error_handler)
    
    # Iniciar bot
    print("✅ Bot iniciado!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
''',
            "lang": "python",
            "ext": ".py"
        }
    },
    
    "🐍 Python Scripts": {
        "Web Scraper Avançado": {
            "code": '''import requests
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
import time
from urllib.parse import urljoin, urlparse
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebScraper:
    def __init__(self, base_url, output_format='csv'):
        self.base_url = base_url
        self.output_format = output_format
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.data = []
    
    def fetch_page(self, url, retries=3):
        """Busca uma página com retry"""
        for attempt in range(retries):
            try:
                logging.info(f"Buscando: {url}")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except Exception as e:
                logging.error(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logging.error(f"Falha ao buscar {url}")
                    return None
    
    def parse_html(self, html_content):
        """Parse HTML content"""
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_links(self, soup, base_url):
        """Extrai todos os links da página"""
        links = []
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            if urlparse(url).netloc == urlparse(base_url).netloc:
                links.append(url)
        return list(set(links))  # Remove duplicatas
    
    def scrape_page(self, url):
        """Scrape uma página específica"""
        response = self.fetch_page(url)
        if not response:
            return None
        
        soup = self.parse_html(response.content)
        
        # Extrair dados (customize conforme necessário)
        page_data = {
            'url': url,
            'title': soup.title.string if soup.title else 'N/A',
            'headings': [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])],
            'paragraphs': [p.get_text(strip=True) for p in soup.find_all('p')],
            'images': [img.get('src', '') for img in soup.find_all('img')],
            'links': self.extract_links(soup, url),
            'timestamp': datetime.now().isoformat()
        }
        
        return page_data
    
    def scrape_multiple(self, urls):
        """Scrape múltiplas URLs"""
        for url in urls:
            data = self.scrape_page(url)
            if data:
                self.data.append(data)
            time.sleep(1)  # Respeitar o servidor
    
    def save_to_csv(self, filename=None):
        """Salva dados em CSV"""
        if not filename:
            filename = f'scrape_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        if not self.data:
            logging.warning("Nenhum dado para salvar")
            return
        
        # Flatten data para CSV
        flattened_data = []
        for item in self.data:
            flattened_item = {
                'url': item['url'],
                'title': item['title'],
                'num_headings': len(item['headings']),
                'num_paragraphs': len(item['paragraphs']),
                'num_images': len(item['images']),
                'num_links': len(item['links']),
                'timestamp': item['timestamp']
            }
            flattened_data.append(flattened_item)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if flattened_data:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
        
        logging.info(f"✅ Dados salvos em {filename}")
    
    def save_to_json(self, filename=None):
        """Salva dados em JSON"""
        if not filename:
            filename = f'scrape_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        
        logging.info(f"✅ Dados salvos em {filename}")
    
    def save(self, filename=None):
        """Salva dados no formato especificado"""
        if self.output_format == 'csv':
            self.save_to_csv(filename)
        elif self.output_format == 'json':
            self.save_to_json(filename)
        else:
            logging.error(f"Formato não suportado: {self.output_format}")
    
    def get_stats(self):
        """Retorna estatísticas do scraping"""
        if not self.data:
            return "Nenhum dado coletado"
        
        total_pages = len(self.data)
        total_headings = sum(len(d['headings']) for d in self.data)
        total_paragraphs = sum(len(d['paragraphs']) for d in self.data)
        total_images = sum(len(d['images']) for d in self.data)
        total_links = sum(len(d['links']) for d in self.data)
        
        return f"""
📊 ESTATÍSTICAS DO SCRAPING:
━━━━━━━━━━━━━━━━━━━━━━━
📄 Páginas: {total_pages}
📋 Headings: {total_headings}
📝 Parágrafos: {total_paragraphs}
🖼️  Imagens: {total_images}
🔗 Links: {total_links}
"""

# Exemplo de uso
if __name__ == "__main__":
    # Configuração
    url = "https://example.com"  # Substitua pela URL desejada
    
    # Criar scraper
    scraper = WebScraper(url, output_format='json')
    
    # Scrape uma página
    print("🔍 Iniciando scraping...")
    data = scraper.scrape_page(url)
    
    if data:
        scraper.data.append(data)
        
        # Mostrar estatísticas
        print(scraper.get_stats())
        
        # Salvar dados
        scraper.save()
        print("✅ Scraping concluído!")
    else:
        print("❌ Erro ao fazer scraping")
    
    # Para scrape múltiplo:
    # urls = ["url1", "url2", "url3"]
    # scraper.scrape_multiple(urls)
    # scraper.save()
''',
            "lang": "python",
            "ext": ".py"
        },
        
        "API RESTful com Flask": {
            "code": '''from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)  # Habilitar CORS

# Arquivo de dados
DATA_FILE = 'database.json'

# Funções de banco de dados
def load_data():
    """Carrega dados do arquivo JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'users': [], 'posts': []}

def save_data(data):
    """Salva dados no arquivo JSON"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Carregar dados iniciais
db = load_data()

# ==================== ROTAS ====================

@app.route('/')
def home():
    """Rota principal"""
    return jsonify({
        'message': 'API RESTful com Flask',
        'version': '1.0',
        'endpoints': {
            'users': '/api/users',
            'posts': '/api/posts',
            'health': '/api/health'
        }
    })

@app.route('/api/health')
def health():
    """Verifica saúde da API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'total_users': len(db['users']),
        'total_posts': len(db['posts'])
    })

# ==================== USERS ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Lista todos os usuários"""
    return jsonify({
        'success': True,
        'data': db['users'],
        'count': len(db['users'])
    })

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Busca usuário por ID"""
    user = next((u for u in db['users'] if u['id'] == user_id), None)
    
    if user:
        return jsonify({
            'success': True,
            'data': user
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Usuário não encontrado'
        }), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    """Cria novo usuário"""
    data = request.get_json()
    
    # Validação
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({
            'success': False,
            'error': 'Nome e email são obrigatórios'
        }), 400
    
    # Verificar email duplicado
    if any(u['email'] == data['email'] for u in db['users']):
        return jsonify({
            'success': False,
            'error': 'Email já cadastrado'
        }), 400
    
    # Criar usuário
    new_user = {
        'id': len(db['users']) + 1,
        'name': data['name'],
        'email': data['email'],
        'created_at': datetime.now().isoformat()
    }
    
    db['users'].append(new_user)
    save_data(db)
    
    return jsonify({
        'success': True,
        'data': new_user,
        'message': 'Usuário criado com sucesso'
    }), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Atualiza usuário"""
    user = next((u for u in db['users'] if u['id'] == user_id), None)
    
    if not user:
        return jsonify({
            'success': False,
            'error': 'Usuário não encontrado'
        }), 404
    
    data = request.get_json()
    
    if 'name' in data:
        user['name'] = data['name']
    if 'email' in data:
        user['email'] = data['email']
    
    user['updated_at'] = datetime.now().isoformat()
    
    save_data(db)
    
    return jsonify({
        'success': True,
        'data': user,
        'message': 'Usuário atualizado com sucesso'
    })

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deleta usuário"""
    user = next((u for u in db['users'] if u['id'] == user_id), None)
    
    if not user:
        return jsonify({
            'success': False,
            'error': 'Usuário não encontrado'
        }), 404
    
    db['users'] = [u for u in db['users'] if u['id'] != user_id]
    save_data(db)
    
    return jsonify({
        'success': True,
        'message': 'Usuário deletado com sucesso'
    })

# ==================== POSTS ====================

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Lista todos os posts"""
    return jsonify({
        'success': True,
        'data': db['posts'],
        'count': len(db['posts'])
    })

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Busca post por ID"""
    post = next((p for p in db['posts'] if p['id'] == post_id), None)
    
    if post:
        return jsonify({
            'success': True,
            'data': post
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Post não encontrado'
        }), 404

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Cria novo post"""
    data = request.get_json()
    
    # Validação
    if not data or 'title' not in data or 'content' not in data or 'user_id' not in data:
        return jsonify({
            'success': False,
            'error': 'Título, conteúdo e user_id são obrigatórios'
        }), 400
    
    # Verificar se usuário existe
    user = next((u for u in db['users'] if u['id'] == data['user_id']), None)
    if not user:
        return jsonify({
            'success': False,
            'error': 'Usuário não encontrado'
        }), 404
    
    # Criar post
    new_post = {
        'id': len(db['posts']) + 1,
        'title': data['title'],
        'content': data['content'],
        'user_id': data['user_id'],
        'author': user['name'],
        'created_at': datetime.now().isoformat()
    }
    
    db['posts'].append(new_post)
    save_data(db)
    
    return jsonify({
        'success': True,
        'data': new_post,
        'message': 'Post criado com sucesso'
    }), 201

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Atualiza post"""
    post = next((p for p in db['posts'] if p['id'] == post_id), None)
    
    if not post:
        return jsonify({
            'success': False,
            'error': 'Post não encontrado'
        }), 404
    
    data = request.get_json()
    
    if 'title' in data:
        post['title'] = data['title']
    if 'content' in data:
        post['content'] = data['content']
    
    post['updated_at'] = datetime.now().isoformat()
    
    save_data(db)
    
    return jsonify({
        'success': True,
        'data': post,
        'message': 'Post atualizado com sucesso'
    })

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Deleta post"""
    post = next((p for p in db['posts'] if p['id'] == post_id), None)
    
    if not post:
        return jsonify({
            'success': False,
            'error': 'Post não encontrado'
        }), 404
    
    db['posts'] = [p for p in db['posts'] if p['id'] != post_id]
    save_data(db)
    
    return jsonify({
        'success': True,
        'message': 'Post deletado com sucesso'
    })

# ==================== BUSCA ====================

@app.route('/api/search', methods=['GET'])
def search():
    """Busca global"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Query não fornecida'
        }), 400
    
    # Buscar em users
    users_result = [
        u for u in db['users']
        if query in u['name'].lower() or query in u['email'].lower()
    ]
    
    # Buscar em posts
    posts_result = [
        p for p in db['posts']
        if query in p['title'].lower() or query in p['content'].lower()
    ]
    
    return jsonify({
        'success': True,
        'query': query,
        'results': {
            'users': users_result,
            'posts': posts_result
        },
        'total': len(users_result) + len(posts_result)
    })

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor'
    }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("🚀 Iniciando API...")
    print("📍 http://localhost:5000")
    print("\n📚 Endpoints disponíveis:")
    print("   GET    /api/users")
    print("   POST   /api/users")
    print("   GET    /api/users/<id>")
    print("   PUT    /api/users/<id>")
    print("   DELETE /api/users/<id>")
    print("   GET    /api/posts")
    print("   POST   /api/posts")
    print("   GET    /api/search?q=<query>")
    print("\n✅ API rodando!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
''',
            "lang": "python",
            "ext": ".py"
        }
    }
}

# ====== TELA DE LOGIN ======
if not st.session_state.authenticated:
    st.markdown("""
    <div class="header-premium">
        <h1>🎮 ScriptMaster AI Pro</h1>
        <p style="color: white; font-size: 1.2rem;">Gerador Profissional de Scripts e Jogos com IA Avançada</p>
        <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">🔐 Login automático - Sistema aprimorado!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔐 Entrar no Sistema")
        
        username = st.text_input("👤 Seu nome", placeholder="Digite seu nome", key="login_username")
        access_code = st.text_input("🎫 Código de acesso VIP", type="password", placeholder="Cole seu código VIP aqui", key="login_code")
        
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
        
        st.markdown("""
        **🆓 MODO GRATUITO:**
        - ✅ Geração básica de código
        - ✅ Templates simples
        - ✅ Editar e baixar scripts
        - ⚠️ Limite de uso diário
        """)
        
        st.divider()
        
        st.markdown("""
        <div class="vip-info">
            <h3 style="margin:0; color: white;">👑 MODO VIP</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem;">
                ✅ Geração ILIMITADA de código<br>
                ✅ TODOS os templates premium<br>
                ✅ Salvar scripts permanentemente<br>
                ✅ Histórico de geração<br>
                ✅ Sistema de favoritos<br>
                ✅ Suporte prioritário<br>
                ✅ Sem anúncios<br>
                ✅ Novos recursos exclusivos
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### 💻 O que você pode criar:")
        st.markdown("""
        **🎮 Jogos:**
        - Godot 4.6 (GDScript/C#)
        - Unity (C#)
        - HTML5 (Phaser, Canvas)
        - React Native Mobile
        
        **🤖 Bots:**
        - Discord Bot (Slash Commands)
        - Telegram Bot (Inline Buttons)
        - WhatsApp Bot
        
        **💾 Scripts:**
        - Python (Web Scraper, API, Automação)
        - JavaScript/Node.js
        - SQL Database
        - Bash/PowerShell
        """)
        
        st.divider()
        
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
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", total_codes)
            with col2:
                st.metric("Usados", used_codes)
            
            st.divider()
            
            for code, info in list(st.session_state.created_codes.items())[:10]:
                status = "✅ USADO" if info.get("used") else "🎫 ATIVO"
                days_icon = "♾️" if info["days"] == 999 else f"{info['days']}d"
                
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
    
    # Templates Organizados
    st.markdown("### 📚 Templates Prontos")
    
    for categoria, templates in TEMPLATES.items():
        with st.expander(categoria):
            for name, template_data in templates.items():
                if st.button(name, use_container_width=True, key=f"temp_{name}"):
                    st.session_state.current_script = template_data['code']
                    st.session_state.current_language = template_data['lang']
                    st.toast(f"✅ Template '{name}' carregado!")
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
    <h1>🎮 ScriptMaster AI Pro</h1>
    <p style="color: white;">Gerador Profissional de Scripts e Jogos com Inteligência Artificial Avançada</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🤖 Gerar Código", "💻 Editor", "📚 Biblioteca", "📊 Estatísticas"])

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
                "PowerShell",
                "Flask API",
                "FastAPI",
                "Node.js Express"
            ]
        )
        
        nivel = st.select_slider("📊 Complexidade", ["Básico", "Intermediário", "Avançado", "Expert"])
        
        incluir_comentarios = st.checkbox("💬 Incluir comentários detalhados", value=True)
        incluir_testes = st.checkbox("🧪 Incluir testes unitários", value=False)
    
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
                    
                    extras = []
                    if incluir_comentarios:
                        extras.append("Comentários explicativos DETALHADOS em português")
                    if incluir_testes:
                        extras.append("Testes unitários funcionais")
                    
                    extras_text = "\n".join(f"{i+1}. {extra}" for i, extra in enumerate(extras)) if extras else "Nenhum extra solicitado"
                    
                    prompt_ia = f"""
Você é um programador EXPERT em {tipo}. Crie código COMPLETO, FUNCIONAL e PROFISSIONAL.

TAREFA: {prompt}

NÍVEL DE COMPLEXIDADE: {nivel}

EXTRAS SOLICITADOS:
{extras_text}

REGRAS OBRIGATÓRIAS:
1. Código 100% COMPLETO e pronto para usar
2. Seguir as melhores práticas da linguagem
3. Incluir tratamento de erros
4. Se for jogo: controles funcionais, física básica, sistema de pontuação
5. Se for mobile: otimizar para touch e performance
6. Se for bot: comandos funcionais e tratamento de eventos
7. Se for API: rotas RESTful, validação de dados
8. Código limpo e bem estruturado
9. Segurança em primeiro lugar

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
                    
                    # Adicionar ao histórico
                    st.session_state.script_history.append({
                        'prompt': prompt,
                        'code': codigo,
                        'tipo': tipo,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    st.success("✅ Código gerado com sucesso!")
                    st.balloons()
                    
                    # Detectar linguagem
                    lang, ext = detect_language(codigo)
                    
                    st.session_state.current_language = lang
                    
                    # Mostrar código
                    st.markdown("### 📄 Seu Código Está Pronto:")
                    st.code(codigo, language=lang)
                    
                    # Informações
                    linhas = len(codigo.split('\n'))
                    caracteres = len(codigo)
                    palavras = len(codigo.split())
                    
                    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                    with col_info1:
                        st.metric("📏 Linhas", linhas)
                    with col_info2:
                        st.metric("🔤 Caracteres", caracteres)
                    with col_info3:
                        st.metric("📝 Palavras", palavras)
                    with col_info4:
                        st.metric("💾 Tipo", lang.upper())
                    
                    st.divider()
                    
                    # Botões de ação
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.download_button(
                            "📥 BAIXAR",
                            data=codigo,
                            file_name=f"script{ext}",
                            mime="text/plain",
                            use_container_width=True,
                            type="primary"
                        )
                    
                    with col_b:
                        if st.button("💾 SALVAR", use_container_width=True, key="save_gen"):
                            st.session_state.saved_scripts.append({
                                "name": f"Script_{len(st.session_state.saved_scripts)+1}{ext}",
                                "code": codigo,
                                "language": lang,
                                "created_at": datetime.now().isoformat()
                            })
                            st.success("✅ Script salvo!")
                            st.rerun()
                    
                    with col_c:
                        if st.button("⭐ FAVORITAR", use_container_width=True, key="fav_gen"):
                            st.session_state.favorites.append({
                                "name": f"Favorito_{len(st.session_state.favorites)+1}{ext}",
                                "code": codigo,
                                "language": lang,
                                "created_at": datetime.now().isoformat()
                            })
                            st.success("⭐ Adicionado aos favoritos!")
                            st.rerun()
                    
                    with col_d:
                        if st.button("✏️ EDITAR", use_container_width=True, key="edit_gen"):
                            st.info("👉 Vá para a aba 'Editor'")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar código: {str(e)}")
                    st.info("💡 Dicas: Tente descrever de forma mais simples ou escolha outro tipo de código")

# TAB 2: EDITOR
with tab2:
    st.markdown("### 💻 Editor de Código Profissional")
    
    if st.session_state.current_script:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            nome = st.text_input("📝 Nome do arquivo", value="meu_script", key="filename")
        
        with col2:
            lang, ext = detect_language(st.session_state.current_script)
            ext_input = st.text_input("📄 Extensão", value=ext, key="ext")
        
        with col3:
            theme = st.selectbox("🎨 Tema", ["Escuro", "Claro"])
        
        with col4:
            st.download_button(
                "📥 Download",
                data=st.session_state.current_script,
                file_name=f"{nome}{ext_input}",
                use_container_width=True
            )
        
        codigo_edit = st.text_area(
            "✏️ Edite seu código:",
            value=st.session_state.current_script,
            height=500,
            key="editor"
        )
        
        st.session_state.current_script = codigo_edit
        
        col_s, col_c, col_f, col_l = st.columns(4)
        
        with col_s:
            if st.button("💾 Salvar", use_container_width=True):
                st.session_state.saved_scripts.append({
                    "name": f"{nome}{ext_input}",
                    "code": codigo_edit,
                    "language": st.session_state.current_language,
                    "created_at": datetime.now().isoformat()
                })
                st.success("✅ Script salvo!")
                st.rerun()
        
        with col_c:
            if st.button("📋 Copiar", use_container_width=True):
                st.code(codigo_edit)
                st.info("📋 Código pronto para copiar!")
        
        with col_f:
            if st.button("⭐ Favoritar", use_container_width=True):
                st.session_state.favorites.append({
                    "name": f"{nome}{ext_input}",
                    "code": codigo_edit,
                    "language": st.session_state.current_language,
                    "created_at": datetime.now().isoformat()
                })
                st.success("⭐ Adicionado aos favoritos!")
                st.rerun()
        
        with col_l:
            if st.button("🗑️ Limpar", use_container_width=True):
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
        st.code(codigo_edit, language=st.session_state.current_language)
        
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
    
    tab_todos, tab_favoritos = st.tabs(["📄 Todos os Scripts", "⭐ Favoritos"])
    
    with tab_todos:
        if st.session_state.saved_scripts:
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                search = st.text_input("🔍 Buscar script", placeholder="Digite para filtrar...")
            
            with col_filter2:
                ordem = st.selectbox("📊 Ordenar por", ["Mais recentes", "Mais antigos", "Nome A-Z"])
            
            st.divider()
            
            scripts_filtered = st.session_state.saved_scripts.copy()
            
            if search:
                scripts_filtered = [s for s in scripts_filtered if search.lower() in s['name'].lower()]
            
            if ordem == "Mais antigos":
                scripts_filtered = scripts_filtered
            elif ordem == "Mais recentes":
                scripts_filtered = list(reversed(scripts_filtered))
            elif ordem == "Nome A-Z":
                scripts_filtered = sorted(scripts_filtered, key=lambda x: x['name'])
            
            for idx, script in enumerate(scripts_filtered):
                data_criacao = datetime.fromisoformat(script['created_at']).strftime('%d/%m/%Y às %H:%M')
                
                with st.expander(f"📄 {script['name']} - Criado em {data_criacao}"):
                    st.code(script['code'], language=script.get('language', 'python'))
                    
                    linhas_script = len(script['code'].split('\n'))
                    tamanho_kb = len(script['code']) / 1024
                    
                    col_stat1, col_stat2 = st.columns(2)
                    with col_stat1:
                        st.caption(f"📏 {linhas_script} linhas")
                    with col_stat2:
                        st.caption(f"💾 {tamanho_kb:.2f} KB")
                    
                    st.divider()
                    
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
                            st.success("✅ Código copiado!")
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
    
    with tab_favoritos:
        if st.session_state.favorites:
            for idx, fav in enumerate(st.session_state.favorites):
                data_criacao = datetime.fromisoformat(fav['created_at']).strftime('%d/%m/%Y às %H:%M')
                
                with st.expander(f"⭐ {fav['name']} - {data_criacao}"):
                    st.code(fav['code'], language=fav.get('language', 'python'))
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            "📥 Download",
                            data=fav['code'],
                            file_name=fav['name'],
                            key=f"dl_fav_{idx}",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("🗑️ Remover", key=f"del_fav_{idx}", use_container_width=True):
                            st.session_state.favorites.pop(idx)
                            st.success("✅ Removido dos favoritos!")
                            st.rerun()
        else:
            st.info("⭐ Nenhum favorito ainda!")

# TAB 4: ESTATÍSTICAS
with tab4:
    st.markdown("### 📊 Estatísticas de Uso")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Scripts Salvos", len(st.session_state.saved_scripts))
    
    with col2:
        st.metric("⭐ Favoritos", len(st.session_state.favorites))
    
    with col3:
        st.metric("📜 Histórico", len(st.session_state.script_history))
    
    with col4:
        total_linhas = sum(len(s['code'].split('\n')) for s in st.session_state.saved_scripts)
        st.metric("📏 Linhas Totais", total_linhas)
    
    st.divider()
    
    if st.session_state.script_history:
        st.markdown("### 📜 Histórico de Gerações")
        
        for idx, hist in enumerate(reversed(st.session_state.script_history[-10:])):
            data = datetime.fromisoformat(hist['timestamp']).strftime('%d/%m/%Y %H:%M')
            
            with st.expander(f"🕐 {data} - {hist['tipo']}"):
                st.markdown(f"**Prompt:** {hist['prompt']}")
                st.code(hist['code'][:500] + "..." if len(hist['code']) > 500 else hist['code'])
                
                if st.button("♻️ Reutilizar este código", key=f"reuse_{idx}"):
                    st.session_state.current_script = hist['code']
                    st.success("✅ Código carregado no editor!")
                    st.rerun()
    else:
        st.info("📭 Nenhum histórico ainda")

# ====== RODAPÉ ======
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📊 Scripts", len(st.session_state.saved_scripts))

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
    st.metric("📏 Linhas", linhas_atual)

with col4:
    login_status = "Salvo ✅" if "user" in st.query_params else "Temp"
    st.metric("🔐 Login", login_status)

with col5:
    st.metric("⭐ Favs", len(st.session_state.favorites))

st.caption("💡 Desenvolvido por Rynamru | Versão 2.0 Pro")
