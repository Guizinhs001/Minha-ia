import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
import re
import base64
import uuid

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(
    page_title="ScriptMaster AI Pro 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CÓDIGO MASTER
MASTER_CODE = "GuizinhsDono"

# Limites de uso
DAILY_LIMIT_FREE = 4
DAILY_LIMIT_CHAT_FREE = 10

# ==================== CSS ULTRA MODERNO ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Reset e Base */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Header Premium Animado */
    .header-ultra {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f64f59 100%);
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .header-ultra::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shine 4s linear infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    @keyframes shine {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .header-ultra h1 {
        color: white;
        margin: 0;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .header-ultra p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Badges */
    .master-badge {
        background: linear-gradient(135deg, #ff0000 0%, #ff4444 50%, #cc0000 100%);
        color: white;
        padding: 0.6rem 1.5rem;
        border-radius: 30px;
        font-weight: 700;
        display: inline-block;
        animation: masterPulse 2s infinite;
        box-shadow: 0 4px 20px rgba(255, 0, 0, 0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    @keyframes masterPulse {
        0%, 100% { transform: scale(1); box-shadow: 0 4px 20px rgba(255, 0, 0, 0.5); }
        50% { transform: scale(1.05); box-shadow: 0 6px 30px rgba(255, 0, 0, 0.7); }
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%);
        color: #1a1a2e;
        padding: 0.6rem 1.5rem;
        border-radius: 30px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .free-badge {
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Welcome Box */
    .welcome-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    
    .welcome-box h3 {
        margin: 0 0 0.5rem 0;
        font-weight: 700;
    }
    
    /* Chat Container */
    .chat-container {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f23 100%);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.1);
        max-height: 500px;
        overflow-y: auto;
    }
    
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 16px;
        margin: 0.8rem 0;
        position: relative;
        animation: fadeInUp 0.3s ease;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 4px;
    }
    
    .ai-message {
        background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
        color: #e0e0e0;
        margin-right: 20%;
        border-bottom-left-radius: 4px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .message-actions {
        position: absolute;
        top: 8px;
        right: 8px;
        display: flex;
        gap: 5px;
        opacity: 0;
        transition: opacity 0.2s;
    }
    
    .chat-message:hover .message-actions {
        opacity: 1;
    }
    
    .action-btn {
        background: rgba(255,255,255,0.1);
        border: none;
        color: white;
        padding: 4px 8px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s;
    }
    
    .action-btn:hover {
        background: rgba(255,255,255,0.2);
    }
    
    /* Cards */
    .feature-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .feature-card h4 {
        color: #667eea;
        margin: 0 0 0.5rem 0;
    }
    
    .feature-card p {
        color: #a0a0a0;
        margin: 0;
        font-size: 0.9rem;
    }
    
    /* Stats Card */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .stats-card h2 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 800;
    }
    
    .stats-card p {
        margin: 0.3rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Usage Meter */
    .usage-meter {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .usage-bar {
        background: #2d2d44;
        border-radius: 8px;
        height: 10px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .usage-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.5s ease;
    }
    
    .usage-fill.green { background: linear-gradient(90deg, #00c853, #69f0ae); }
    .usage-fill.yellow { background: linear-gradient(90deg, #ffd600, #ffff00); }
    .usage-fill.red { background: linear-gradient(90deg, #ff1744, #ff5252); }
    
    /* Code Block */
    .code-block {
        background: #0d1117;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #30363d;
        overflow-x: auto;
    }
    
    .code-block pre {
        margin: 0;
        color: #c9d1d9;
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #1a1a2e !important;
        color: white !important;
        border: 2px solid #2d2d44 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Select Box */
    .stSelectbox > div > div {
        background: #1a1a2e !important;
        border: 2px solid #2d2d44 !important;
        border-radius: 12px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #a0a0a0;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1a1a2e !important;
        border: 1px solid #2d2d44 !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #2d2d44, transparent);
        margin: 2rem 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metric Cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
    }
    
    [data-testid="metric-container"] label {
        color: #a0a0a0 !important;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: white !important;
    }
    
    /* Toast/Alerts */
    .stAlert {
        background: #1a1a2e !important;
        border: 1px solid #2d2d44 !important;
        border-radius: 12px !important;
    }
    
    /* Login Card */
    .login-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 24px;
        padding: 2.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    .login-card h3 {
        color: white;
        margin: 0 0 1.5rem 0;
        text-align: center;
    }
    
    /* VIP Info Card */
    .vip-info-card {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #1a1a2e;
        padding: 2rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(255, 215, 0, 0.3);
    }
    
    .vip-info-card h3 {
        margin: 0 0 1rem 0;
        font-weight: 800;
    }
    
    /* Floating Action Button */
    .fab {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        cursor: pointer;
        transition: all 0.3s;
        z-index: 1000;
    }
    
    .fab:hover {
        transform: scale(1.1);
    }
    
    /* Template Card */
    .template-card {
        background: #1e1e2e;
        border: 1px solid #2d2d44;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .template-card:hover {
        border-color: #667eea;
        transform: translateX(5px);
    }
    
    /* Sidebar Improvements */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%) !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES DE PERSISTÊNCIA ====================

def encode_data(data):
    """Codifica dados para URL"""
    try:
        json_str = json.dumps(data, ensure_ascii=False)
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        return encoded
    except:
        return ""

def decode_data(encoded):
    """Decodifica dados da URL"""
    try:
        json_str = base64.urlsafe_b64decode(encoded.encode()).decode()
        return json.loads(json_str)
    except:
        return {}

def generate_token(username, is_master, vip_days=0):
    """Gera token de login"""
    data = f"{username}|{is_master}|{vip_days}|scriptmaster_v3"
    return hashlib.sha256(data.encode()).hexdigest()[:20]

def save_login(username, is_master, vip_until=None):
    """Salva login na URL"""
    vip_days = 0
    if vip_until:
        vip_days = max(0, (vip_until - datetime.now()).days)
    
    token = generate_token(username, is_master, vip_days)
    
    st.query_params["user"] = username
    st.query_params["master"] = "1" if is_master else "0"
    st.query_params["vip"] = str(vip_days)
    st.query_params["token"] = token

def save_user_data():
    """Salva dados do usuário (histórico, favoritos, etc) na URL"""
    try:
        data = {
            "history": st.session_state.get("script_history", [])[-20:],  # Últimos 20
            "favorites": st.session_state.get("favorites", [])[-20:],  # Últimos 20
            "saved": st.session_state.get("saved_scripts", [])[-10:],  # Últimos 10
            "usage": st.session_state.get("daily_usage", {}),
            "chat": st.session_state.get("chat_messages", [])[-30:]  # Últimas 30 msgs
        }
        encoded = encode_data(data)
        if len(encoded) < 2000:  # Limite de URL
            st.query_params["data"] = encoded
    except Exception as e:
        pass

def load_user_data():
    """Carrega dados do usuário da URL"""
    try:
        if "data" in st.query_params:
            encoded = st.query_params.get("data", "")
            data = decode_data(encoded)
            
            if data:
                st.session_state.script_history = data.get("history", [])
                st.session_state.favorites = data.get("favorites", [])
                st.session_state.saved_scripts = data.get("saved", [])
                st.session_state.daily_usage = data.get("usage", {})
                st.session_state.chat_messages = data.get("chat", [])
                return True
    except:
        pass
    return False

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
                else:
                    st.session_state.vip_until = None
                
                st.session_state.authenticated = True
                
                # Carregar dados do usuário
                load_user_data()
                
                return True
        return False
    except:
        return False

def clear_login():
    """Limpa login"""
    st.query_params.clear()
    keys_to_clear = ['authenticated', 'is_master', 'vip_until', 'username', 
                     'current_script', 'saved_scripts', 'favorites', 
                     'script_history', 'chat_messages', 'daily_usage']
    for key in keys_to_clear:
        if key in st.session_state:
            if key == 'authenticated':
                st.session_state[key] = False
            elif key in ['saved_scripts', 'favorites', 'script_history', 'chat_messages']:
                st.session_state[key] = []
            elif key == 'daily_usage':
                st.session_state[key] = {}
            else:
                st.session_state[key] = None

# ==================== SISTEMA DE LIMITE DE USO ====================

def get_today_key():
    """Retorna chave do dia atual"""
    return datetime.now().strftime("%Y-%m-%d")

def check_usage_limit(usage_type="generate"):
    """Verifica se o usuário ainda tem uso disponível"""
    if st.session_state.get("is_master", False) or is_vip_active():
        return True, float('inf')
    
    today = get_today_key()
    
    if "daily_usage" not in st.session_state:
        st.session_state.daily_usage = {}
    
    if today not in st.session_state.daily_usage:
        st.session_state.daily_usage = {today: {"generate": 0, "chat": 0}}
    
    current_usage = st.session_state.daily_usage[today].get(usage_type, 0)
    
    if usage_type == "generate":
        limit = DAILY_LIMIT_FREE
    else:
        limit = DAILY_LIMIT_CHAT_FREE
    
    remaining = limit - current_usage
    return remaining > 0, remaining

def increment_usage(usage_type="generate"):
    """Incrementa contador de uso"""
    if st.session_state.get("is_master", False) or is_vip_active():
        return
    
    today = get_today_key()
    
    if "daily_usage" not in st.session_state:
        st.session_state.daily_usage = {}
    
    if today not in st.session_state.daily_usage:
        st.session_state.daily_usage = {today: {"generate": 0, "chat": 0}}
    
    st.session_state.daily_usage[today][usage_type] = \
        st.session_state.daily_usage[today].get(usage_type, 0) + 1
    
    # Salvar dados
    save_user_data()

def get_usage_stats():
    """Retorna estatísticas de uso"""
    today = get_today_key()
    
    if "daily_usage" not in st.session_state:
        return {"generate": 0, "chat": 0}
    
    return st.session_state.daily_usage.get(today, {"generate": 0, "chat": 0})

# ==================== INICIALIZAÇÃO ====================

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
    "chat_messages": [],
    "daily_usage": {},
    "editing_message_id": None
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Auto-login
if not st.session_state.authenticated and not st.session_state.login_checked:
    st.session_state.login_checked = True
    if load_login():
        st.toast(f"✅ Bem-vindo de volta, {st.session_state.username}!", icon="🎉")

# Configurar API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("❌ Chave API não configurada!")
    st.info("Configure em Settings > Secrets > GEMINI_API_KEY")
    st.stop()

def is_vip_active():
    if st.session_state.get("is_master", False):
        return True
    vip_until = st.session_state.get("vip_until")
    if vip_until:
        return datetime.now() < vip_until
    return False

@st.cache_resource
def get_models():
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except:
        return ["models/gemini-1.5-flash"]

def detect_language(code):
    """Detecta a linguagem do código"""
    code_lower = code.lower()
    
    if 'extends' in code_lower and 'func ' in code_lower:
        return 'gdscript', '.gd'
    elif 'using unityengine' in code_lower or 'monobehaviour' in code_lower:
        return 'csharp', '.cs'
    elif '<!doctype html>' in code_lower or '<html' in code_lower:
        return 'html', '.html'
    elif 'local ' in code_lower and 'function' in code_lower:
        return 'lua', '.lua'
    elif 'gg.' in code_lower or 'gameguardian' in code_lower.replace(' ', ''):
        return 'lua', '.lua'
    elif 'def ' in code_lower and 'import ' in code_lower:
        return 'python', '.py'
    elif 'select ' in code_lower and 'from ' in code_lower:
        return 'sql', '.sql'
    elif 'function' in code_lower or 'const ' in code_lower:
        return 'javascript', '.js'
    else:
        return 'python', '.py'

# ==================== TEMPLATES COMPLETOS ====================

TEMPLATES = {
    "🎮 Jogos HTML5 Android": {
        "PWA Game - Plataforma Completo": {
            "code": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#1a1a2e">
    <title>Platformer Mobile</title>
    
    <!-- PWA Manifest -->
    <link rel="manifest" href="data:application/json,{
        \\"name\\": \\"Platformer Mobile\\",
        \\"short_name\\": \\"Platformer\\",
        \\"start_url\\": \\"./\\",
        \\"display\\": \\"fullscreen\\",
        \\"orientation\\": \\"landscape\\",
        \\"background_color\\": \\"#1a1a2e\\",
        \\"theme_color\\": \\"#667eea\\"
    }">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            touch-action: none;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
            user-select: none;
        }
        
        body {
            background: #1a1a2e;
            overflow: hidden;
            position: fixed;
            width: 100%;
            height: 100%;
        }
        
        #gameCanvas {
            display: block;
            width: 100%;
            height: 100%;
            image-rendering: pixelated;
        }
        
        #ui {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            pointer-events: none;
            z-index: 10;
        }
        
        .ui-box {
            background: rgba(0,0,0,0.7);
            padding: 10px 20px;
            border-radius: 15px;
            color: white;
            font-family: Arial, sans-serif;
            font-weight: bold;
            font-size: 18px;
            backdrop-filter: blur(10px);
        }
        
        #controls {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 40%;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            padding: 20px;
            z-index: 10;
        }
        
        .joystick-area {
            width: 150px;
            height: 150px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 3px solid rgba(255,255,255,0.3);
        }
        
        .joystick-inner {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            box-shadow: 0 5px 20px rgba(102,126,234,0.5);
        }
        
        .action-buttons {
            display: flex;
            gap: 15px;
        }
        
        .action-btn {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            box-shadow: 0 5px 20px rgba(102,126,234,0.5);
            border: 3px solid rgba(255,255,255,0.3);
        }
        
        .action-btn:active {
            transform: scale(0.9);
        }
        
        #pauseMenu {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 100;
        }
        
        .menu-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 20px 60px;
            font-size: 24px;
            font-weight: bold;
            border-radius: 30px;
            margin: 10px;
            cursor: pointer;
        }
        
        #gameOver {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 100;
        }
        
        #gameOver h1 {
            color: #ff4444;
            font-size: 48px;
            margin-bottom: 20px;
            font-family: Arial;
        }
        
        #finalScore {
            color: white;
            font-size: 32px;
            margin-bottom: 30px;
            font-family: Arial;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui">
        <div class="ui-box" id="scoreDisplay">🪙 0</div>
        <div class="ui-box" id="levelDisplay">Nível 1</div>
        <div class="ui-box" id="livesDisplay">❤️❤️❤️</div>
    </div>
    
    <div id="controls">
        <div class="joystick-area" id="joystick">
            <div class="joystick-inner" id="joystickInner"></div>
        </div>
        <div class="action-buttons">
            <div class="action-btn" id="jumpBtn">⬆️</div>
            <div class="action-btn" id="actionBtn">⚡</div>
        </div>
    </div>
    
    <div id="pauseMenu">
        <h1 style="color:white; font-size:48px; margin-bottom:40px;">⏸️ PAUSADO</h1>
        <button class="menu-btn" id="resumeBtn">▶️ Continuar</button>
        <button class="menu-btn" id="restartBtn">🔄 Reiniciar</button>
    </div>
    
    <div id="gameOver">
        <h1>💀 GAME OVER</h1>
        <div id="finalScore">Score: 0</div>
        <button class="menu-btn" id="retryBtn">🔄 Tentar Novamente</button>
    </div>
    
    <script>
        // Canvas Setup
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // Game State
        let gameState = 'playing';
        let score = 0;
        let level = 1;
        let lives = 3;
        
        // Physics
        const GRAVITY = 0.6;
        const FRICTION = 0.85;
        const JUMP_FORCE = -15;
        
        // Player
        const player = {
            x: 100,
            y: 300,
            width: 50,
            height: 50,
            vx: 0,
            vy: 0,
            speed: 8,
            jumping: false,
            grounded: false,
            color: '#00ff88',
            facing: 1
        };
        
        // Level
        let platforms = [];
        let coins = [];
        let enemies = [];
        let particles = [];
        
        function generateLevel() {
            platforms = [
                {x: 0, y: canvas.height - 50, width: canvas.width, height: 50, color: '#4a4a6a'},
                {x: 200, y: canvas.height - 150, width: 150, height: 20, color: '#5a5a8a'},
                {x: 450, y: canvas.height - 250, width: 150, height: 20, color: '#5a5a8a'},
                {x: 700, y: canvas.height - 200, width: 200, height: 20, color: '#5a5a8a'},
                {x: 100, y: canvas.height - 350, width: 120, height: 20, color: '#5a5a8a'}
            ];
            
            coins = [
                {x: 250, y: canvas.height - 200, radius: 15, collected: false},
                {x: 500, y: canvas.height - 300, radius: 15, collected: false},
                {x: 780, y: canvas.height - 250, radius: 15, collected: false},
                {x: 150, y: canvas.height - 400, radius: 15, collected: false}
            ];
            
            enemies = [
                {x: 500, y: canvas.height - 90, width: 40, height: 40, vx: 2, minX: 400, maxX: 600}
            ];
        }
        generateLevel();
        
        // Touch Controls
        let joystickActive = false;
        let joystickVector = {x: 0, y: 0};
        const joystickArea = document.getElementById('joystick');
        const joystickInner = document.getElementById('joystickInner');
        const jumpBtn = document.getElementById('jumpBtn');
        
        joystickArea.addEventListener('touchstart', (e) => {
            joystickActive = true;
            handleJoystick(e);
        });
        
        joystickArea.addEventListener('touchmove', (e) => {
            if (joystickActive) handleJoystick(e);
        });
        
        joystickArea.addEventListener('touchend', () => {
            joystickActive = false;
            joystickVector = {x: 0, y: 0};
            joystickInner.style.transform = 'translate(0, 0)';
        });
        
        function handleJoystick(e) {
            const touch = e.touches[0];
            const rect = joystickArea.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            let dx = touch.clientX - centerX;
            let dy = touch.clientY - centerY;
            
            const maxDist = 40;
            const dist = Math.sqrt(dx*dx + dy*dy);
            
            if (dist > maxDist) {
                dx = (dx / dist) * maxDist;
                dy = (dy / dist) * maxDist;
            }
            
            joystickVector.x = dx / maxDist;
            joystickVector.y = dy / maxDist;
            
            joystickInner.style.transform = `translate(${dx}px, ${dy}px)`;
        }
        
        jumpBtn.addEventListener('touchstart', () => {
            if (player.grounded) {
                player.vy = JUMP_FORCE;
                player.jumping = true;
                player.grounded = false;
                createParticles(player.x + player.width/2, player.y + player.height, '#00ff88', 5);
            }
        });
        
        // Particles
        function createParticles(x, y, color, count) {
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: x,
                    y: y,
                    vx: (Math.random() - 0.5) * 8,
                    vy: (Math.random() - 0.5) * 8,
                    radius: Math.random() * 5 + 2,
                    color: color,
                    life: 30
                });
            }
        }
        
        // Update
        function update() {
            if (gameState !== 'playing') return;
            
            // Player movement
            player.vx = joystickVector.x * player.speed;
            
            if (joystickVector.x !== 0) {
                player.facing = joystickVector.x > 0 ? 1 : -1;
            }
            
            // Physics
            player.vy += GRAVITY;
            player.x += player.vx;
            player.y += player.vy;
            
            // Platform collision
            player.grounded = false;
            for (let plat of platforms) {
                if (player.x + player.width > plat.x &&
                    player.x < plat.x + plat.width &&
                    player.y + player.height > plat.y &&
                    player.y + player.height < plat.y + plat.height + player.vy + 10) {
                    
                    player.y = plat.y - player.height;
                    player.vy = 0;
                    player.grounded = true;
                    player.jumping = false;
                }
            }
            
            // Screen bounds
            if (player.x < 0) player.x = 0;
            if (player.x + player.width > canvas.width) player.x = canvas.width - player.width;
            
            // Fall death
            if (player.y > canvas.height) {
                loseLife();
            }
            
            // Coins
            for (let coin of coins) {
                if (!coin.collected) {
                    const dx = (player.x + player.width/2) - coin.x;
                    const dy = (player.y + player.height/2) - coin.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist < player.width/2 + coin.radius) {
                        coin.collected = true;
                        score += 10;
                        updateUI();
                        createParticles(coin.x, coin.y, '#ffd700', 10);
                    }
                }
            }
            
            // Enemies
            for (let enemy of enemies) {
                enemy.x += enemy.vx;
                if (enemy.x <= enemy.minX || enemy.x + enemy.width >= enemy.maxX) {
                    enemy.vx *= -1;
                }
                
                // Collision with player
                if (player.x + player.width > enemy.x &&
                    player.x < enemy.x + enemy.width &&
                    player.y + player.height > enemy.y &&
                    player.y < enemy.y + enemy.height) {
                    
                    // Jump on enemy
                    if (player.vy > 0 && player.y + player.height < enemy.y + 20) {
                        enemies = enemies.filter(e => e !== enemy);
                        player.vy = JUMP_FORCE * 0.7;
                        score += 50;
                        updateUI();
                        createParticles(enemy.x + enemy.width/2, enemy.y, '#ff4444', 15);
                    } else {
                        loseLife();
                    }
                }
            }
            
            // Particles
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.3;
                p.life--;
                if (p.life <= 0) particles.splice(i, 1);
            }
            
            // Check level complete
            if (coins.every(c => c.collected) && enemies.length === 0) {
                level++;
                generateLevel();
                updateUI();
            }
        }
        
        function loseLife() {
            lives--;
            updateUI();
            createParticles(player.x + player.width/2, player.y + player.height/2, '#ff4444', 20);
            
            if (lives <= 0) {
                gameOver();
            } else {
                player.x = 100;
                player.y = 300;
                player.vx = 0;
                player.vy = 0;
            }
        }
        
        function gameOver() {
            gameState = 'gameover';
            document.getElementById('finalScore').textContent = `Score: ${score}`;
            document.getElementById('gameOver').style.display = 'flex';
        }
        
        function updateUI() {
            document.getElementById('scoreDisplay').textContent = `🪙 ${score}`;
            document.getElementById('levelDisplay').textContent = `Nível ${level}`;
            document.getElementById('livesDisplay').textContent = '❤️'.repeat(lives);
        }
        
        // Draw
        function draw() {
            // Background
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Platforms
            for (let plat of platforms) {
                ctx.fillStyle = plat.color;
                ctx.fillRect(plat.x, plat.y, plat.width, plat.height);
            }
            
            // Coins
            for (let coin of coins) {
                if (!coin.collected) {
                    ctx.fillStyle = '#ffd700';
                    ctx.beginPath();
                    ctx.arc(coin.x, coin.y, coin.radius, 0, Math.PI * 2);
                    ctx.fill();
                    
                    ctx.fillStyle = '#fff';
                    ctx.beginPath();
                    ctx.arc(coin.x - 4, coin.y - 4, 4, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            // Enemies
            for (let enemy of enemies) {
                ctx.fillStyle = '#ff4444';
                ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
                
                ctx.fillStyle = '#fff';
                ctx.fillRect(enemy.x + 8, enemy.y + 8, 8, 8);
                ctx.fillRect(enemy.x + enemy.width - 16, enemy.y + 8, 8, 8);
            }
            
            // Player
            ctx.fillStyle = player.color;
            ctx.fillRect(player.x, player.y, player.width, player.height);
            
            // Player eyes
            ctx.fillStyle = '#fff';
            const eyeX = player.facing > 0 ? player.x + 30 : player.x + 10;
            ctx.fillRect(eyeX, player.y + 12, 10, 10);
            
            ctx.fillStyle = '#000';
            ctx.fillRect(eyeX + 3, player.y + 15, 4, 4);
            
            // Particles
            for (let p of particles) {
                ctx.globalAlpha = p.life / 30;
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.globalAlpha = 1;
        }
        
        // Game Loop
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // Menu
        document.getElementById('resumeBtn').onclick = () => {
            document.getElementById('pauseMenu').style.display = 'none';
            gameState = 'playing';
        };
        
        document.getElementById('restartBtn').onclick = restart;
        document.getElementById('retryBtn').onclick = restart;
        
        function restart() {
            document.getElementById('pauseMenu').style.display = 'none';
            document.getElementById('gameOver').style.display = 'none';
            
            score = 0;
            level = 1;
            lives = 3;
            player.x = 100;
            player.y = 300;
            player.vx = 0;
            player.vy = 0;
            particles = [];
            generateLevel();
            updateUI();
            gameState = 'playing';
        }
        
        // Start
        updateUI();
        gameLoop();
        
        console.log('✅ Platformer Mobile iniciado!');
    </script>
</body>
</html>''',
            "lang": "html",
            "ext": ".html"
        },
        
        "PWA Game - Endless Runner": {
            "code": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#1a1a2e">
    <title>Endless Runner Mobile</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; touch-action: manipulation; user-select: none; }
        body { background: #1a1a2e; overflow: hidden; position: fixed; width: 100%; height: 100%; }
        #gameCanvas { display: block; width: 100%; height: 100%; }
        
        #ui {
            position: absolute;
            top: 15px;
            left: 15px;
            right: 15px;
            display: flex;
            justify-content: space-between;
            z-index: 10;
        }
        
        .ui-box {
            background: rgba(0,0,0,0.7);
            padding: 10px 25px;
            border-radius: 25px;
            color: white;
            font-family: Arial, sans-serif;
            font-size: 20px;
            font-weight: bold;
        }
        
        #startScreen, #gameOverScreen {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.95);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 100;
        }
        
        #gameOverScreen { display: none; }
        
        h1 { color: #667eea; font-size: 48px; margin-bottom: 20px; font-family: Arial; }
        h2 { color: #ff4444; font-size: 42px; margin-bottom: 20px; font-family: Arial; }
        
        .play-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 20px 80px;
            font-size: 28px;
            font-weight: bold;
            border-radius: 40px;
            margin-top: 30px;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(102,126,234,0.5);
        }
        
        .instructions {
            color: rgba(255,255,255,0.7);
            font-size: 18px;
            margin-top: 20px;
            font-family: Arial;
        }
        
        #finalScore {
            color: white;
            font-size: 32px;
            font-family: Arial;
        }
        
        #highScore {
            color: #ffd700;
            font-size: 24px;
            font-family: Arial;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui">
        <div class="ui-box" id="scoreDisplay">🏃 0</div>
        <div class="ui-box" id="distanceDisplay">📏 0m</div>
    </div>
    
    <div id="startScreen">
        <h1>🏃 ENDLESS RUNNER</h1>
        <p class="instructions">Toque para pular</p>
        <p class="instructions">Deslize para baixo para rolar</p>
        <button class="play-btn" id="startBtn">▶️ JOGAR</button>
    </div>
    
    <div id="gameOverScreen">
        <h2>💀 GAME OVER</h2>
        <div id="finalScore">Score: 0</div>
        <div id="highScore">🏆 Recorde: 0</div>
        <button class="play-btn" id="retryBtn">🔄 JOGAR NOVAMENTE</button>
    </div>
    
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);
        
        // Game variables
        let gameRunning = false;
        let score = 0;
        let distance = 0;
        let highScore = localStorage.getItem('endlessRunnerHighScore') || 0;
        let speed = 8;
        let gravity = 0.8;
        
        // Ground
        const groundY = canvas.height * 0.75;
        
        // Player
        const player = {
            x: 100,
            y: groundY - 60,
            width: 50,
            height: 60,
            vy: 0,
            jumping: false,
            rolling: false,
            rollTimer: 0
        };
        
        // Obstacles
        let obstacles = [];
        let coins = [];
        let particles = [];
        let clouds = [];
        
        // Initialize clouds
        for (let i = 0; i < 5; i++) {
            clouds.push({
                x: Math.random() * canvas.width,
                y: Math.random() * groundY * 0.5,
                width: Math.random() * 100 + 50,
                speed: Math.random() * 1 + 0.5
            });
        }
        
        // Touch controls
        let touchStartY = 0;
        
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            touchStartY = e.touches[0].clientY;
            
            if (gameRunning && !player.jumping && !player.rolling) {
                player.vy = -18;
                player.jumping = true;
                createParticles(player.x + player.width/2, player.y + player.height, '#00ff88', 5);
            }
        });
        
        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const touchY = e.touches[0].clientY;
            
            if (touchY - touchStartY > 50 && !player.rolling && player.y >= groundY - 60) {
                player.rolling = true;
                player.rollTimer = 30;
            }
        });
        
        function createParticles(x, y, color, count) {
            for (let i = 0; i < count; i++) {
                particles.push({
                    x, y,
                    vx: (Math.random() - 0.5) * 6,
                    vy: (Math.random() - 0.5) * 6,
                    radius: Math.random() * 4 + 2,
                    color,
                    life: 25
                });
            }
        }
        
        function spawnObstacle() {
            const types = ['small', 'tall', 'flying'];
            const type = types[Math.floor(Math.random() * types.length)];
            
            let obstacle = { x: canvas.width + 50, type };
            
            if (type === 'small') {
                obstacle.y = groundY - 40;
                obstacle.width = 30;
                obstacle.height = 40;
            } else if (type === 'tall') {
                obstacle.y = groundY - 80;
                obstacle.width = 30;
                obstacle.height = 80;
            } else {
                obstacle.y = groundY - 120;
                obstacle.width = 50;
                obstacle.height = 30;
            }
            
            obstacles.push(obstacle);
        }
        
        function spawnCoin() {
            coins.push({
                x: canvas.width + 50,
                y: groundY - 100 - Math.random() * 100,
                radius: 15,
                collected: false
            });
        }
        
        function update() {
            if (!gameRunning) return;
            
            // Increase difficulty
            speed = 8 + Math.floor(distance / 500) * 0.5;
            
            // Player physics
            player.vy += gravity;
            player.y += player.vy;
            
            if (player.y >= groundY - (player.rolling ? 30 : 60)) {
                player.y = groundY - (player.rolling ? 30 : 60);
                player.vy = 0;
                player.jumping = false;
            }
            
            if (player.rolling) {
                player.rollTimer--;
                if (player.rollTimer <= 0) player.rolling = false;
            }
            
            // Spawn obstacles
            if (Math.random() < 0.02) spawnObstacle();
            if (Math.random() < 0.03) spawnCoin();
            
            // Update obstacles
            for (let i = obstacles.length - 1; i >= 0; i--) {
                obstacles[i].x -= speed;
                
                if (obstacles[i].x + obstacles[i].width < 0) {
                    obstacles.splice(i, 1);
                    continue;
                }
                
                // Collision
                const obs = obstacles[i];
                const playerHeight = player.rolling ? 30 : 60;
                const playerY = player.rolling ? groundY - 30 : player.y;
                
                if (player.x + player.width > obs.x &&
                    player.x < obs.x + obs.width &&
                    playerY + playerHeight > obs.y &&
                    playerY < obs.y + obs.height) {
                    gameOver();
                }
            }
            
            // Update coins
            for (let i = coins.length - 1; i >= 0; i--) {
                coins[i].x -= speed;
                
                if (coins[i].x + coins[i].radius < 0) {
                    coins.splice(i, 1);
                    continue;
                }
                
                if (!coins[i].collected) {
                    const dx = (player.x + player.width/2) - coins[i].x;
                    const dy = (player.y + 30) - coins[i].y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist < 40) {
                        coins[i].collected = true;
                        score += 10;
                        createParticles(coins[i].x, coins[i].y, '#ffd700', 10);
                    }
                }
            }
            
            // Update clouds
            for (let cloud of clouds) {
                cloud.x -= cloud.speed;
                if (cloud.x + cloud.width < 0) {
                    cloud.x = canvas.width + 50;
                    cloud.y = Math.random() * groundY * 0.5;
                }
            }
            
            // Update particles
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.2;
                p.life--;
                if (p.life <= 0) particles.splice(i, 1);
            }
            
            distance += speed / 10;
            updateUI();
        }
        
        function draw() {
            // Sky gradient
            const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
            gradient.addColorStop(0, '#1a1a2e');
            gradient.addColorStop(1, '#16213e');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Clouds
            ctx.fillStyle = 'rgba(255,255,255,0.1)';
            for (let cloud of clouds) {
                ctx.beginPath();
                ctx.ellipse(cloud.x, cloud.y, cloud.width/2, 20, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // Ground
            ctx.fillStyle = '#4a4a6a';
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            
            // Ground line
            ctx.fillStyle = '#5a5a8a';
            ctx.fillRect(0, groundY, canvas.width, 5);
            
            // Obstacles
            for (let obs of obstacles) {
                ctx.fillStyle = '#ff4444';
                ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
            }
            
            // Coins
            for (let coin of coins) {
                if (!coin.collected) {
                    ctx.fillStyle = '#ffd700';
                    ctx.beginPath();
                    ctx.arc(coin.x, coin.y, coin.radius, 0, Math.PI * 2);
                    ctx.fill();
                    
                    ctx.fillStyle = '#fff';
                    ctx.beginPath();
                    ctx.arc(coin.x - 4, coin.y - 4, 4, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            // Player
            ctx.fillStyle = '#00ff88';
            const playerHeight = player.rolling ? 30 : 60;
            const playerY = player.rolling ? groundY - 30 : player.y;
            ctx.fillRect(player.x, playerY, player.width, playerHeight);
            
            // Player eye
            ctx.fillStyle = '#fff';
            ctx.fillRect(player.x + 30, playerY + (player.rolling ? 5 : 15), 12, 12);
            ctx.fillStyle = '#000';
            ctx.fillRect(player.x + 35, playerY + (player.rolling ? 8 : 18), 5, 5);
            
            // Particles
            for (let p of particles) {
                ctx.globalAlpha = p.life / 25;
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.globalAlpha = 1;
        }
        
        function updateUI() {
            document.getElementById('scoreDisplay').textContent = `🪙 ${score}`;
            document.getElementById('distanceDisplay').textContent = `📏 ${Math.floor(distance)}m`;
        }
        
        function gameOver() {
            gameRunning = false;
            
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('endlessRunnerHighScore', highScore);
            }
            
            document.getElementById('finalScore').textContent = `Score: ${score}`;
            document.getElementById('highScore').textContent = `🏆 Recorde: ${highScore}`;
            document.getElementById('gameOverScreen').style.display = 'flex';
        }
        
        function startGame() {
            document.getElementById('startScreen').style.display = 'none';
            document.getElementById('gameOverScreen').style.display = 'none';
            
            score = 0;
            distance = 0;
            speed = 8;
            obstacles = [];
            coins = [];
            particles = [];
            player.y = groundY - 60;
            player.vy = 0;
            player.jumping = false;
            player.rolling = false;
            
            gameRunning = true;
            updateUI();
        }
        
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // Events
        document.getElementById('startBtn').addEventListener('click', startGame);
        document.getElementById('retryBtn').addEventListener('click', startGame);
        
        // Start
        gameLoop();
    </script>
</body>
</html>''',
            "lang": "html",
            "ext": ".html"
        }
    },
    
    "🎮 Godot 4.x": {
        "Player Controller Completo": {
            "code": '''extends CharacterBody2D
## Player Controller Profissional para Godot 4.x
## Controles: WASD ou Arrows, Espaço para pular

# Configurações exportáveis
@export_group("Movimento")
@export var speed: float = 300.0
@export var acceleration: float = 2000.0
@export var friction: float = 1500.0
@export var air_resistance: float = 200.0

@export_group("Pulo")
@export var jump_velocity: float = -450.0
@export var double_jump_velocity: float = -350.0
@export var max_jumps: int = 2
@export var coyote_time: float = 0.15
@export var jump_buffer_time: float = 0.1

@export_group("Física")
@export var gravity_multiplier: float = 1.0
@export var fall_gravity_multiplier: float = 1.5
@export var max_fall_speed: float = 800.0

# Variáveis internas
var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")
var jumps_remaining: int = max_jumps
var coyote_timer: float = 0.0
var jump_buffer_timer: float = 0.0
var was_on_floor: bool = false
var facing_direction: int = 1

# Referências (criar nós com estes nomes)
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D

# Sinais
signal jumped
signal landed
signal double_jumped
signal took_damage(amount: int)
signal died

func _ready() -> void:
    jumps_remaining = max_jumps
    print("✅ Player Controller inicializado!")

func _physics_process(delta: float) -> void:
    handle_timers(delta)
    handle_gravity(delta)
    handle_jump()
    handle_movement(delta)
    handle_animations()
    
    was_on_floor = is_on_floor()
    move_and_slide()

func handle_timers(delta: float) -> void:
    # Coyote time (permite pular logo após cair de plataforma)
    if was_on_floor and not is_on_floor():
        coyote_timer = coyote_time
    elif is_on_floor():
        coyote_timer = 0.0
        jumps_remaining = max_jumps
    else:
        coyote_timer -= delta
    
    # Jump buffer (registra input de pulo antes de tocar o chão)
    if Input.is_action_just_pressed("ui_accept"):
        jump_buffer_timer = jump_buffer_time
    else:
        jump_buffer_timer -= delta

func handle_gravity(delta: float) -> void:
    if not is_on_floor():
        var current_gravity = gravity * gravity_multiplier
        
        # Gravidade maior ao cair
        if velocity.y > 0:
            current_gravity *= fall_gravity_multiplier
        
        velocity.y += current_gravity * delta
        velocity.y = min(velocity.y, max_fall_speed)

func handle_jump() -> void:
    var can_coyote_jump = coyote_timer > 0
    var has_buffered_jump = jump_buffer_timer > 0
    
    # Pulo normal ou com coyote time
    if (is_on_floor() or can_coyote_jump) and (Input.is_action_just_pressed("ui_accept") or has_buffered_jump):
        perform_jump(jump_velocity)
        coyote_timer = 0.0
        jump_buffer_timer = 0.0
        jumped.emit()
    
    # Double jump
    elif Input.is_action_just_pressed("ui_accept") and jumps_remaining > 0 and not is_on_floor():
        perform_jump(double_jump_velocity)
        double_jumped.emit()
    
    # Soltar botão = pulo mais curto
    if Input.is_action_just_released("ui_accept") and velocity.y < 0:
        velocity.y *= 0.5

func perform_jump(power: float) -> void:
    velocity.y = power
    jumps_remaining -= 1
    spawn_jump_particles()

func handle_movement(delta: float) -> void:
    var direction = Input.get_axis("ui_left", "ui_right")
    
    if direction != 0:
        facing_direction = sign(direction)
        
        if is_on_floor():
            velocity.x = move_toward(velocity.x, direction * speed, acceleration * delta)
        else:
            velocity.x = move_toward(velocity.x, direction * speed, air_resistance * delta)
    else:
        if is_on_floor():
            velocity.x = move_toward(velocity.x, 0, friction * delta)
        else:
            velocity.x = move_toward(velocity.x, 0, air_resistance * 0.5 * delta)

func handle_animations() -> void:
    if not sprite:
        return
    
    # Flip sprite baseado na direção
    sprite.flip_h = facing_direction < 0
    
    # Animações
    if not is_on_floor():
        if velocity.y < 0:
            play_animation("jump")
        else:
            play_animation("fall")
    elif abs(velocity.x) > 10:
        play_animation("run")
    else:
        play_animation("idle")

func play_animation(anim_name: String) -> void:
    if sprite and sprite.sprite_frames and sprite.sprite_frames.has_animation(anim_name):
        if sprite.animation != anim_name:
            sprite.play(anim_name)

func spawn_jump_particles() -> void:
    # Implementar sistema de partículas aqui
    pass

# Funções públicas
func take_damage(amount: int) -> void:
    took_damage.emit(amount)
    play_animation("hurt")
    
    # Knockback
    velocity.y = jump_velocity * 0.5
    velocity.x = -facing_direction * speed * 0.5

func die() -> void:
    died.emit()
    set_physics_process(false)
    play_animation("death")

func respawn(pos: Vector2) -> void:
    global_position = pos
    velocity = Vector2.ZERO
    set_physics_process(true)
    play_animation("idle")
''',
            "lang": "gdscript",
            "ext": ".gd"
        },
        
        "Sistema de Inventário": {
            "code": '''extends Node
class_name InventorySystem
## Sistema de Inventário Completo para Godot 4.x

signal item_added(item: InventoryItem, slot: int)
signal item_removed(item: InventoryItem, slot: int)
signal item_used(item: InventoryItem)
signal inventory_changed

const MAX_SLOTS: int = 20
const MAX_STACK: int = 99

var slots: Array[InventorySlot] = []

class InventoryItem:
    var id: String
    var name: String
    var description: String
    var icon: Texture2D
    var max_stack: int = 99
    var item_type: ItemType
    var rarity: Rarity
    var stats: Dictionary = {}
    
    enum ItemType { WEAPON, ARMOR, CONSUMABLE, MATERIAL, QUEST }
    enum Rarity { COMMON, UNCOMMON, RARE, EPIC, LEGENDARY }
    
    func _init(item_id: String, item_name: String, type: ItemType = ItemType.MATERIAL):
        id = item_id
        name = item_name
        item_type = type
        rarity = Rarity.COMMON
    
    func get_rarity_color() -> Color:
        match rarity:
            Rarity.COMMON: return Color.WHITE
            Rarity.UNCOMMON: return Color.GREEN
            Rarity.RARE: return Color.BLUE
            Rarity.EPIC: return Color.PURPLE
            Rarity.LEGENDARY: return Color.ORANGE
            _: return Color.WHITE

class InventorySlot:
    var item: InventoryItem = null
    var quantity: int = 0
    
    func is_empty() -> bool:
        return item == null or quantity <= 0
    
    func can_add(new_item: InventoryItem, amount: int = 1) -> bool:
        if is_empty():
            return true
        return item.id == new_item.id and quantity + amount <= item.max_stack
    
    func add(new_item: InventoryItem, amount: int = 1) -> int:
        if is_empty():
            item = new_item
            quantity = min(amount, new_item.max_stack)
            return amount - quantity
        
        if item.id != new_item.id:
            return amount
        
        var space = item.max_stack - quantity
        var to_add = min(amount, space)
        quantity += to_add
        return amount - to_add
    
    func remove(amount: int = 1) -> int:
        var removed = min(amount, quantity)
        quantity -= removed
        
        if quantity <= 0:
            item = null
            quantity = 0
        
        return removed
    
    func clear() -> void:
        item = null
        quantity = 0

func _ready() -> void:
    # Inicializar slots vazios
    for i in range(MAX_SLOTS):
        slots.append(InventorySlot.new())
    print("✅ Sistema de Inventário inicializado com ", MAX_SLOTS, " slots")

func add_item(item: InventoryItem, amount: int = 1) -> int:
    var remaining = amount
    
    # Primeiro, tentar adicionar em slots existentes com o mesmo item
    for i in range(slots.size()):
        if slots[i].item and slots[i].item.id == item.id:
            remaining = slots[i].add(item, remaining)
            if remaining <= 0:
                item_added.emit(item, i)
                inventory_changed.emit()
                return 0
    
    # Depois, adicionar em slots vazios
    for i in range(slots.size()):
        if slots[i].is_empty():
            remaining = slots[i].add(item, remaining)
            if remaining <= 0:
                item_added.emit(item, i)
                inventory_changed.emit()
                return 0
    
    inventory_changed.emit()
    return remaining  # Retorna quantidade que não coube

func remove_item(item_id: String, amount: int = 1) -> bool:
    var remaining = amount
    
    for i in range(slots.size() - 1, -1, -1):
        if slots[i].item and slots[i].item.id == item_id:
            var removed = slots[i].remove(remaining)
            remaining -= removed
            
            if slots[i].is_empty():
                item_removed.emit(slots[i].item, i)
            
            if remaining <= 0:
                inventory_changed.emit()
                return true
    
    inventory_changed.emit()
    return remaining <= 0

func has_item(item_id: String, amount: int = 1) -> bool:
    return get_item_count(item_id) >= amount

func get_item_count(item_id: String) -> int:
    var count = 0
    for slot in slots:
        if slot.item and slot.item.id == item_id:
            count += slot.quantity
    return count

func get_item_at(index: int) -> InventorySlot:
    if index >= 0 and index < slots.size():
        return slots[index]
    return null

func swap_slots(index1: int, index2: int) -> void:
    if index1 < 0 or index1 >= slots.size():
        return
    if index2 < 0 or index2 >= slots.size():
        return
    
    var temp_item = slots[index1].item
    var temp_quantity = slots[index1].quantity
    
    slots[index1].item = slots[index2].item
    slots[index1].quantity = slots[index2].quantity
    
    slots[index2].item = temp_item
    slots[index2].quantity = temp_quantity
    
    inventory_changed.emit()

func use_item(index: int) -> bool:
    var slot = get_item_at(index)
    if slot and not slot.is_empty():
        if slot.item.item_type == InventoryItem.ItemType.CONSUMABLE:
            item_used.emit(slot.item)
            slot.remove(1)
            inventory_changed.emit()
            return true
    return false

func sort_inventory() -> void:
    # Ordenar por tipo e depois por nome
    var items_data = []
    
    for slot in slots:
        if not slot.is_empty():
            items_data.append({
                "item": slot.item,
                "quantity": slot.quantity
            })
        slot.clear()
    
    items_data.sort_custom(func(a, b):
        if a.item.item_type != b.item.item_type:
            return a.item.item_type < b.item.item_type
        return a.item.name < b.item.name
    )
    
    var slot_index = 0
    for data in items_data:
        if slot_index < slots.size():
            slots[slot_index].item = data.item
            slots[slot_index].quantity = data.quantity
            slot_index += 1
    
    inventory_changed.emit()

func clear_inventory() -> void:
    for slot in slots:
        slot.clear()
    inventory_changed.emit()

func get_all_items() -> Array:
    var items = []
    for slot in slots:
        if not slot.is_empty():
            items.append({
                "item": slot.item,
                "quantity": slot.quantity
            })
    return items

func save_inventory() -> Dictionary:
    var save_data = []
    for slot in slots:
        if slot.is_empty():
            save_data.append(null)
        else:
            save_data.append({
                "id": slot.item.id,
                "quantity": slot.quantity
            })
    return {"slots": save_data}

func load_inventory(data: Dictionary, item_database: Dictionary) -> void:
    clear_inventory()
    
    if not data.has("slots"):
        return
    
    for i in range(min(data.slots.size(), slots.size())):
        if data.slots[i] != null:
            var item_id = data.slots[i].id
            if item_database.has(item_id):
                slots[i].item = item_database[item_id]
                slots[i].quantity = data.slots[i].quantity
    
    inventory_changed.emit()
''',
            "lang": "gdscript",
            "ext": ".gd"
        }
    },
    
    "🛡️ Game Guardian": {
        "Hack de Moedas/Dinheiro": {
            "code": '''--[[
    Game Guardian Script - Hack de Moedas/Dinheiro
    Compatível com: Games que usam valores inteiros
    Autor: ScriptMaster AI
    
    INSTRUÇÕES:
    1. Abra o jogo e anote a quantidade atual de moedas
    2. Execute este script no Game Guardian
    3. Digite o valor atual quando solicitado
    4. Gaste algumas moedas no jogo
    5. Digite o novo valor
    6. Repita até encontrar o endereço
    7. Modifique para o valor desejado
]]

gg.clearResults()
gg.setVisible(false)

-- Configurações
local SCRIPT_NAME = "💰 Coin Hack v1.0"
local SEARCH_TYPES = {
    gg.TYPE_DWORD,    -- Int32 (mais comum)
    gg.TYPE_FLOAT,    -- Float (alguns jogos)
    gg.TYPE_DOUBLE,   -- Double (jogos Unity)
    gg.TYPE_QWORD     -- Int64 (valores grandes)
}

-- Menu principal
function mainMenu()
    local menu = gg.choice({
        "🔍 Buscar Valor (Primeira Busca)",
        "🔎 Refinar Busca (Valor Mudou)",
        "💎 Modificar Valores Encontrados",
        "🔄 Congelar Valores",
        "❄️ Descongelar Valores",
        "🗑️ Limpar Resultados",
        "❌ Sair"
    }, nil, SCRIPT_NAME)
    
    return menu
end

-- Buscar valor
function searchValue()
    local value = gg.prompt(
        {"Digite o valor atual de moedas:"},
        {[1] = ""},
        {[1] = "number"}
    )
    
    if value == nil then
        gg.toast("❌ Busca cancelada")
        return
    end
    
    gg.clearResults()
    gg.toast("🔍 Buscando valor: " .. value[1])
    
    -- Buscar em todos os tipos
    for i, searchType in ipairs(SEARCH_TYPES) do
        gg.searchNumber(value[1], searchType)
    end
    
    local count = gg.getResultsCount()
    gg.toast("✅ Encontrados: " .. count .. " resultados")
    
    if count > 1000 then
        gg.alert("⚠️ Muitos resultados (" .. count .. ")\n\nGaste algumas moedas no jogo e use 'Refinar Busca' com o novo valor.")
    elseif count == 0 then
        gg.alert("❌ Nenhum resultado encontrado.\n\nTente:\n- Verificar se o valor está correto\n- O jogo pode usar encriptação")
    else
        gg.alert("✅ " .. count .. " resultados encontrados!\n\nSe ainda são muitos, refine a busca.")
    end
end

-- Refinar busca
function refineSearch()
    local count = gg.getResultsCount()
    
    if count == 0 then
        gg.alert("❌ Nenhum resultado para refinar.\n\nFaça uma busca primeiro!")
        return
    end
    
    local value = gg.prompt(
        {"Digite o NOVO valor de moedas:"},
        {[1] = ""},
        {[1] = "number"}
    )
    
    if value == nil then
        gg.toast("❌ Refinamento cancelado")
        return
    end
    
    gg.toast("🔎 Refinando para: " .. value[1])
    gg.refineNumber(value[1], gg.TYPE_DWORD)
    
    local newCount = gg.getResultsCount()
    gg.toast("✅ Restam: " .. newCount .. " resultados")
    
    if newCount <= 10 and newCount > 0 then
        gg.alert("🎯 Poucos resultados!\n\nAgora use 'Modificar Valores' para alterar.")
    end
end

-- Modificar valores
function modifyValues()
    local count = gg.getResultsCount()
    
    if count == 0 then
        gg.alert("❌ Nenhum resultado para modificar!")
        return
    end
    
    local newValue = gg.prompt(
        {"Digite o NOVO valor desejado:", "Quantidade de resultados a modificar (0 = todos):"},
        {[1] = "999999", [2] = "0"},
        {[1] = "number", [2] = "number"}
    )
    
    if newValue == nil then
        gg.toast("❌ Modificação cancelada")
        return
    end
    
    local amount = tonumber(newValue[2])
    if amount == 0 then amount = count end
    
    local results = gg.getResults(amount)
    
    for i, v in ipairs(results) do
        v.value = newValue[1]
        v.freeze = false
    end
    
    gg.setValues(results)
    gg.toast("✅ " .. #results .. " valores modificados para " .. newValue[1])
end

-- Congelar valores
function freezeValues()
    local count = gg.getResultsCount()
    
    if count == 0 then
        gg.alert("❌ Nenhum resultado para congelar!")
        return
    end
    
    local freezeValue = gg.prompt(
        {"Valor para congelar:"},
        {[1] = "999999"},
        {[1] = "number"}
    )
    
    if freezeValue == nil then
        gg.toast("❌ Congelamento cancelado")
        return
    end
    
    local results = gg.getResults(100)
    
    for i, v in ipairs(results) do
        v.value = freezeValue[1]
        v.freeze = true
    end
    
    gg.setValues(results)
    gg.addListItems(results)
    gg.toast("❄️ " .. #results .. " valores congelados em " .. freezeValue[1])
end

-- Descongelar valores
function unfreezeValues()
    local list = gg.getListItems()
    
    if #list == 0 then
        gg.alert("❌ Nenhum valor congelado!")
        return
    end
    
    for i, v in ipairs(list) do
        v.freeze = false
    end
    
    gg.setValues(list)
    gg.clearList()
    gg.toast("🔓 Todos os valores descongelados!")
end

-- Loop principal
function main()
    gg.toast("✅ " .. SCRIPT_NAME .. " carregado!")
    
    while true do
        if gg.isVisible() then
            local choice = mainMenu()
            
            if choice == 1 then
                searchValue()
            elseif choice == 2 then
                refineSearch()
            elseif choice == 3 then
                modifyValues()
            elseif choice == 4 then
                freezeValues()
            elseif choice == 5 then
                unfreezeValues()
            elseif choice == 6 then
                gg.clearResults()
                gg.toast("🗑️ Resultados limpos!")
            elseif choice == 7 then
                gg.toast("👋 Até logo!")
                gg.setVisible(false)
                os.exit()
            end
            
            gg.setVisible(false)
        end
        
        gg.sleep(100)
    end
end

main()
''',
            "lang": "lua",
            "ext": ".lua"
        },
        
        "Speed Hack Universal": {
            "code": '''--[[
    Game Guardian Script - Speed Hack Universal
    Funciona com a maioria dos jogos
    Autor: ScriptMaster AI
    
    AVISOS:
    - Pode causar ban em jogos online
    - Use apenas em jogos offline/single player
    - Alguns jogos detectam modificação de velocidade
]]

gg.clearResults()
gg.setVisible(false)

local SCRIPT_NAME = "⚡ Speed Hack v2.0"

-- Velocidades predefinidas
local SPEEDS = {
    {name = "0.25x (Câmera Lenta)", value = 0.25},
    {name = "0.5x (Lento)", value = 0.5},
    {name = "1x (Normal)", value = 1.0},
    {name = "1.5x (Rápido)", value = 1.5},
    {name = "2x (Muito Rápido)", value = 2.0},
    {name = "3x (Ultra Rápido)", value = 3.0},
    {name = "5x (Extremo)", value = 5.0},
    {name = "🎮 Velocidade Personalizada", value = -1}
}

local currentSpeed = 1.0

function showMenu()
    local menuItems = {}
    
    for i, speed in ipairs(SPEEDS) do
        local prefix = ""
        if speed.value == currentSpeed then
            prefix = "✓ "
        end
        table.insert(menuItems, prefix .. speed.name)
    end
    
    table.insert(menuItems, "📊 Status Atual")
    table.insert(menuItems, "❌ Sair")
    
    return gg.choice(menuItems, nil, SCRIPT_NAME .. " - Atual: " .. currentSpeed .. "x")
end

function setSpeed(speed)
    if speed <= 0 then
        gg.alert("❌ Velocidade inválida!")
        return false
    end
    
    -- Método 1: Usando setSpeed do GG
    local success = pcall(function()
        gg.setSpeed(speed)
    end)
    
    if success then
        currentSpeed = speed
        gg.toast("⚡ Velocidade: " .. speed .. "x")
        return true
    else
        gg.alert("❌ Erro ao definir velocidade.\n\nO jogo pode não suportar modificação de velocidade.")
        return false
    end
end

function customSpeed()
    local input = gg.prompt(
        {"Digite a velocidade desejada (0.1 - 10):"},
        {[1] = "2.0"},
        {[1] = "number"}
    )
    
    if input == nil then
        return
    end
    
    local speed = tonumber(input[1])
    
    if speed == nil or speed < 0.1 or speed > 10 then
        gg.alert("❌ Valor inválido!\n\nUse um valor entre 0.1 e 10")
        return
    end
    
    setSpeed(speed)
end

function showStatus()
    local status = string.format([[
📊 STATUS DO SPEED HACK

⚡ Velocidade Atual: %sx
🎮 Jogo: %s
📱 Pacote: %s

💡 DICAS:
• Use 0.5x para jogos de precisão
• Use 2-3x para farming
• Volte para 1x antes de fechar
    ]], currentSpeed, gg.getTargetInfo().label, gg.getTargetInfo().packageName)
    
    gg.alert(status)
end

-- Loop principal
function main()
    gg.toast("✅ " .. SCRIPT_NAME .. " carregado!")
    
    while true do
        if gg.isVisible() then
            local choice = showMenu()
            
            if choice == nil then
                -- Usuário cancelou
            elseif choice <= #SPEEDS then
                local selectedSpeed = SPEEDS[choice]
                
                if selectedSpeed.value == -1 then
                    customSpeed()
                else
                    setSpeed(selectedSpeed.value)
                end
            elseif choice == #SPEEDS + 1 then
                showStatus()
            elseif choice == #SPEEDS + 2 then
                -- Resetar velocidade antes de sair
                setSpeed(1.0)
                gg.toast("👋 Velocidade resetada. Até logo!")
                os.exit()
            end
            
            gg.setVisible(false)
        end
        
        gg.sleep(100)
    end
end

main()
''',
            "lang": "lua",
            "ext": ".lua"
        },
        
        "Hack de Vida/HP Infinito": {
            "code": '''--[[
    Game Guardian Script - HP/Vida Infinito
    Busca e congela valores de HP
    Autor: ScriptMaster AI
]]

gg.clearResults()
gg.setVisible(false)

local SCRIPT_NAME = "❤️ HP Infinito v1.0"
local savedAddresses = {}

function mainMenu()
    return gg.choice({
        "🔍 Buscar HP (Valor Exato)",
        "🔎 Buscar HP (Porcentagem)",
        "🔄 Refinar Busca",
        "💉 Curar (Restaurar HP)",
        "🛡️ God Mode (HP Infinito)",
        "❌ Desativar God Mode",
        "📋 Ver Endereços Salvos",
        "🗑️ Limpar Tudo",
        "❌ Sair"
    }, nil, SCRIPT_NAME)
end

function searchExactHP()
    local input = gg.prompt(
        {"Digite seu HP atual:"},
        {[1] = "100"},
        {[1] = "number"}
    )
    
    if input == nil then return end
    
    gg.clearResults()
    
    -- Buscar como diferentes tipos
    gg.searchNumber(input[1], gg.TYPE_DWORD)
    local count1 = gg.getResultsCount()
    
    gg.searchNumber(input[1], gg.TYPE_FLOAT)
    local count2 = gg.getResultsCount()
    
    local total = count1 + count2
    gg.toast("✅ Encontrados: " .. total .. " resultados")
    
    if total > 500 then
        gg.alert("⚠️ Muitos resultados!\n\nTome dano no jogo e use 'Refinar Busca'.")
    elseif total == 0 then
        gg.alert("❌ HP não encontrado.\n\nTente buscar por porcentagem ou valor diferente.")
    end
end

function searchPercentHP()
    local input = gg.prompt(
        {"Digite a porcentagem de HP (ex: 100 para 100%):", "HP máximo do personagem:"},
        {[1] = "100", [2] = "100"},
        {[1] = "number", [2] = "number"}
    )
    
    if input == nil then return end
    
    local percent = tonumber(input[1])
    local maxHP = tonumber(input[2])
    local currentHP = (percent / 100) * maxHP
    
    gg.clearResults()
    
    -- Buscar valor calculado
    gg.searchNumber(tostring(currentHP), gg.TYPE_FLOAT)
    gg.searchNumber(tostring(math.floor(currentHP)), gg.TYPE_DWORD)
    
    -- Buscar porcentagem direta (alguns jogos usam 0-1)
    local percentDecimal = percent / 100
    gg.searchNumber(tostring(percentDecimal), gg.TYPE_FLOAT)
    
    local count = gg.getResultsCount()
    gg.toast("✅ Encontrados: " .. count .. " resultados")
end

function refineSearch()
    local count = gg.getResultsCount()
    
    if count == 0 then
        gg.alert("❌ Faça uma busca primeiro!")
        return
    end
    
    local input = gg.prompt(
        {"Digite o NOVO valor de HP:"},
        {[1] = ""},
        {[1] = "number"}
    )
    
    if input == nil then return end
    
    gg.refineNumber(input[1], gg.TYPE_DWORD)
    gg.refineNumber(input[1], gg.TYPE_FLOAT)
    
    local newCount = gg.getResultsCount()
    gg.toast("✅ Restam: " .. newCount .. " resultados")
    
    if newCount <= 20 and newCount > 0 then
        gg.alert("🎯 Poucos resultados!\n\nAgora ative o God Mode!")
    end
end

function healPlayer()
    local count = gg.getResultsCount()
    
    if count == 0 then
        gg.alert("❌ Nenhum endereço de HP encontrado!")
        return
    end
    
    local input = gg.prompt(
        {"HP para restaurar:"},
        {[1] = "99999"},
        {[1] = "number"}
    )
    
    if input == nil then return end
    
    local results = gg.getResults(100)
    
    for i, v in ipairs(results) do
        v.value = input[1]
    end
    
    gg.setValues(results)
    gg.toast("💉 HP restaurado para " .. input[1])
end

function enableGodMode()
    local count = gg.getResultsCount()
    
    if count == 0 then
        gg.alert("❌ Busque o HP primeiro!")
        return
    end
    
    local input = gg.prompt(
        {"HP para congelar (God Mode):", "Quantidade de endereços (0 = todos):"},
        {[1] = "99999", [2] = "10"},
        {[1] = "number", [2] = "number"}
    )
    
    if input == nil then return end
    
    local amount = tonumber(input[2])
    if amount == 0 then amount = math.min(count, 100) end
    
    local results = gg.getResults(amount)
    savedAddresses = {}
    
    for i, v in ipairs(results) do
        v.value = input[1]
        v.freeze = true
        table.insert(savedAddresses, {
            address = v.address,
            value = input[1]
        })
    end
    
    gg.setValues(results)
    gg.addListItems(results)
    
    gg.toast("🛡️ GOD MODE ATIVADO!")
    gg.alert("🛡️ God Mode Ativo!\n\n" .. #results .. " valores congelados em " .. input[1] .. "\n\nSeu HP não vai diminuir!")
end

function disableGodMode()
    local list = gg.getListItems()
    
    if #list == 0 then
        gg.alert("❌ God Mode não está ativo!")
        return
    end
    
    for i, v in ipairs(list) do
        v.freeze = false
    end
    
    gg.setValues(list)
    gg.clearList()
    savedAddresses = {}
    
    gg.toast("❌ God Mode desativado")
end

function showSavedAddresses()
    if #savedAddresses == 0 then
        gg.alert("📋 Nenhum endereço salvo.\n\nAtive o God Mode primeiro!")
        return
    end
    
    local info = "📋 ENDEREÇOS SALVOS:\n\n"
    
    for i, addr in ipairs(savedAddresses) do
        info = info .. string.format("%d. 0x%X = %s\n", i, addr.address, addr.value)
    end
    
    gg.alert(info)
end

function clearAll()
    gg.clearResults()
    gg.clearList()
    savedAddresses = {}
    gg.toast("🗑️ Tudo limpo!")
end

-- Main loop
function main()
    gg.toast("✅ " .. SCRIPT_NAME .. " carregado!")
    
    while true do
        if gg.isVisible() then
            local choice = mainMenu()
            
            if choice == 1 then
                searchExactHP()
            elseif choice == 2 then
                searchPercentHP()
            elseif choice == 3 then
                refineSearch()
            elseif choice == 4 then
                healPlayer()
            elseif choice == 5 then
                enableGodMode()
            elseif choice == 6 then
                disableGodMode()
            elseif choice == 7 then
                showSavedAddresses()
            elseif choice == 8 then
                clearAll()
            elseif choice == 9 then
                disableGodMode()
                gg.toast("👋 Até logo!")
                os.exit()
            end
            
            gg.setVisible(false)
        end
        
        gg.sleep(100)
    end
end

main()
''',
            "lang": "lua",
            "ext": ".lua"
        }
    },
    
    "🤖 Bots Discord": {
        "Bot Completo com Slash Commands": {
            "code": '''import discord
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
intents.guilds = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.synced = False
    
    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Comandos sincronizados!")
    
    async def on_ready(self):
        print(f"✅ {self.user} está online!")
        print(f"📊 Servidores: {len(self.guilds)}")
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servidores | /help"
            )
        )

bot = MyBot()

# ==================== ECONOMIA ====================
class Economy:
    def __init__(self):
        self.file = "economy.json"
        self.data = self.load()
    
    def load(self):
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                return json.load(f)
        return {}
    
    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_user(self, user_id):
        uid = str(user_id)
        if uid not in self.data:
            self.data[uid] = {"balance": 0, "bank": 0, "daily": None}
            self.save()
        return self.data[uid]
    
    def add_balance(self, user_id, amount):
        user = self.get_user(user_id)
        user["balance"] += amount
        self.save()
    
    def remove_balance(self, user_id, amount):
        user = self.get_user(user_id)
        if user["balance"] >= amount:
            user["balance"] -= amount
            self.save()
            return True
        return False

economy = Economy()

# ==================== COMANDOS SLASH ====================

@bot.tree.command(name="ajuda", description="Mostra todos os comandos")
async def ajuda(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Central de Ajuda",
        description="Todos os comandos disponíveis",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="💰 Economia",
        value="`/saldo` `/daily` `/depositar` `/sacar` `/transferir` `/rank`",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Diversão",
        value="`/dado` `/moeda` `/8ball` `/rps`",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Utilidades",
        value="`/avatar` `/userinfo` `/serverinfo` `/ping`",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Moderação",
        value="`/limpar` `/kick` `/ban` `/mute` `/warn`",
        inline=False
    )
    
    embed.set_footer(text="Desenvolvido com ❤️")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Verifica a latência do bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    
    if latency < 100:
        status = "🟢 Excelente"
        color = discord.Color.green()
    elif latency < 200:
        status = "🟡 Bom"
        color = discord.Color.yellow()
    else:
        status = "🔴 Lento"
        color = discord.Color.red()
    
    embed = discord.Embed(
        title="🏓 Pong!",
        color=color
    )
    embed.add_field(name="Latência", value=f"`{latency}ms`")
    embed.add_field(name="Status", value=status)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="saldo", description="Veja seu saldo")
async def saldo(interaction: discord.Interaction, usuario: discord.Member = None):
    user = usuario or interaction.user
    data = economy.get_user(user.id)
    
    embed = discord.Embed(
        title=f"💰 Saldo de {user.display_name}",
        color=discord.Color.gold()
    )
    embed.add_field(name="💵 Carteira", value=f"`{data['balance']:,}` moedas")
    embed.add_field(name="🏦 Banco", value=f"`{data['bank']:,}` moedas")
    embed.add_field(name="💎 Total", value=f"`{data['balance'] + data['bank']:,}` moedas")
    embed.set_thumbnail(url=user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="Receba suas moedas diárias")
async def daily(interaction: discord.Interaction):
    import random
    
    user_data = economy.get_user(interaction.user.id)
    
    # Verificar cooldown (simplificado)
    reward = random.randint(100, 500)
    economy.add_balance(interaction.user.id, reward)
    
    embed = discord.Embed(
        title="🎁 Recompensa Diária!",
        description=f"Você recebeu **{reward}** moedas!",
        color=discord.Color.green()
    )
    embed.add_field(name="💰 Novo Saldo", value=f"`{user_data['balance'] + reward:,}` moedas")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="transferir", description="Transfira moedas para outro usuário")
async def transferir(interaction: discord.Interaction, usuario: discord.Member, quantidade: int):
    if quantidade <= 0:
        await interaction.response.send_message("❌ Quantidade inválida!", ephemeral=True)
        return
    
    if usuario.id == interaction.user.id:
        await interaction.response.send_message("❌ Você não pode transferir para si mesmo!", ephemeral=True)
        return
    
    if economy.remove_balance(interaction.user.id, quantidade):
        economy.add_balance(usuario.id, quantidade)
        
        embed = discord.Embed(
            title="💸 Transferência Realizada!",
            description=f"**{quantidade:,}** moedas enviadas para {usuario.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Saldo insuficiente!", ephemeral=True)

@bot.tree.command(name="rank", description="Veja o ranking de economia")
async def rank(interaction: discord.Interaction):
    sorted_users = sorted(
        economy.data.items(),
        key=lambda x: x[1].get("balance", 0) + x[1].get("bank", 0),
        reverse=True
    )[:10]
    
    embed = discord.Embed(
        title="🏆 Top 10 Mais Ricos",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    
    description = ""
    for i, (user_id, data) in enumerate(sorted_users):
        try:
            user = await bot.fetch_user(int(user_id))
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            total = data.get("balance", 0) + data.get("bank", 0)
            description += f"{medal} {user.name}: `{total:,}` moedas\\n"
        except:
            continue
    
    embed.description = description
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="Veja o avatar de um usuário")
async def avatar(interaction: discord.Interaction, usuario: discord.Member = None):
    user = usuario or interaction.user
    
    embed = discord.Embed(
        title=f"🖼️ Avatar de {user.display_name}",
        color=user.color
    )
    embed.set_image(url=user.display_avatar.url)
    embed.add_field(name="🔗 Link", value=f"[Clique aqui]({user.display_avatar.url})")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Informações de um usuário")
async def userinfo(interaction: discord.Interaction, usuario: discord.Member = None):
    user = usuario or interaction.user
    
    embed = discord.Embed(
        title=f"👤 {user.display_name}",
        color=user.color
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="🆔 ID", value=f"`{user.id}`")
    embed.add_field(name="📛 Tag", value=f"`{user}`")
    embed.add_field(name="📅 Conta criada", value=f"<t:{int(user.created_at.timestamp())}:R>")
    embed.add_field(name="📥 Entrou no servidor", value=f"<t:{int(user.joined_at.timestamp())}:R>")
    embed.add_field(name="🎭 Cargos", value=f"{len(user.roles) - 1}")
    embed.add_field(name="🤖 Bot?", value="Sim" if user.bot else "Não")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Informações do servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    
    embed = discord.Embed(
        title=f"📊 {guild.name}",
        color=discord.Color.blue()
    )
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="👑 Dono", value=guild.owner.mention)
    embed.add_field(name="👥 Membros", value=f"`{guild.member_count}`")
    embed.add_field(name="💬 Canais", value=f"`{len(guild.channels)}`")
    embed.add_field(name="😀 Emojis", value=f"`{len(guild.emojis)}`")
    embed.add_field(name="🎭 Cargos", value=f"`{len(guild.roles)}`")
    embed.add_field(name="📅 Criado em", value=f"<t:{int(guild.created_at.timestamp())}:R>")
    embed.add_field(name="🔒 Verificação", value=f"`{guild.verification_level}`")
    embed.add_field(name="📈 Boosts", value=f"`{guild.premium_subscription_count}` (Nível {guild.premium_tier})")
    
    await interaction.response.send_message(embed=embed)

# Jogos
@bot.tree.command(name="dado", description="Role um dado")
async def dado(interaction: discord.Interaction, lados: int = 6):
    import random
    
    if lados < 2 or lados > 100:
        await interaction.response.send_message("❌ O dado deve ter entre 2 e 100 lados!", ephemeral=True)
        return
    
    result = random.randint(1, lados)
    
    embed = discord.Embed(
        title="🎲 Dado Rolado!",
        description=f"**Resultado:** `{result}` (d{lados})",
        color=discord.Color.purple()
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="moeda", description="Cara ou coroa")
async def moeda(interaction: discord.Interaction):
    import random
    
    result = random.choice(["Cara", "Coroa"])
    emoji = "🪙" if result == "Cara" else "👑"
    
    embed = discord.Embed(
        title=f"{emoji} {result}!",
        color=discord.Color.gold()
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="8ball", description="Pergunte à bola mágica")
async def eightball(interaction: discord.Interaction, pergunta: str):
    import random
    
    respostas = [
        "✅ Sim, com certeza!",
        "✅ Provavelmente sim",
        "✅ As estrelas dizem que sim",
        "🤔 Talvez...",
        "🤔 Não tenho certeza",
        "🤔 Pergunte novamente",
        "❌ Não conte com isso",
        "❌ Muito duvidoso",
        "❌ Definitivamente não"
    ]
    
    embed = discord.Embed(
        title="🎱 Bola Mágica",
        color=discord.Color.dark_purple()
    )
    embed.add_field(name="❓ Pergunta", value=pergunta, inline=False)
    embed.add_field(name="🔮 Resposta", value=random.choice(respostas), inline=False)
    
    await interaction.response.send_message(embed=embed)

# Moderação
@bot.tree.command(name="limpar", description="Limpa mensagens do chat")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar(interaction: discord.Interaction, quantidade: int):
    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message("❌ Quantidade deve ser entre 1 e 100!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"✅ {len(deleted)} mensagens deletadas!", ephemeral=True)

@bot.tree.command(name="kick", description="Expulsa um membro")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
    if membro.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ Você não pode expulsar este membro!", ephemeral=True)
        return
    
    await membro.kick(reason=motivo)
    
    embed = discord.Embed(
        title="👢 Membro Expulso",
        description=f"{membro.mention} foi expulso do servidor",
        color=discord.Color.orange()
    )
    embed.add_field(name="Motivo", value=motivo)
    embed.add_field(name="Moderador", value=interaction.user.mention)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ban", description="Bane um membro")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
    if membro.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ Você não pode banir este membro!", ephemeral=True)
        return
    
    await membro.ban(reason=motivo)
    
    embed = discord.Embed(
        title="🔨 Membro Banido",
        description=f"{membro.mention} foi banido do servidor",
        color=discord.Color.red()
    )
    embed.add_field(name="Motivo", value=motivo)
    embed.add_field(name="Moderador", value=interaction.user.mention)
    
    await interaction.response.send_message(embed=embed)

# Error handler
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Você não tem permissão!", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Erro: {str(error)}", ephemeral=True)

# Rodar
if __name__ == "__main__":
    TOKEN = "SEU_TOKEN_AQUI"
    bot.run(TOKEN)
''',
            "lang": "python",
            "ext": ".py"
        }
    },
    
    "🐍 Python Scripts": {
        "Web Scraper Profissional": {
            "code": '''"""
Web Scraper Profissional
Extrai dados de websites com sistema de retry e rate limiting
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
import time
from urllib.parse import urljoin, urlparse
import logging
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebScraper:
    def __init__(self, base_url, delay=1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
        })
        self.data = []
    
    def fetch(self, url, retries=3):
        """Busca página com retry automático"""
        for attempt in range(retries):
            try:
                logging.info(f"Buscando: {url}")
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                time.sleep(self.delay)
                return response
            except Exception as e:
                logging.error(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None
    
    def parse(self, html):
        """Parse HTML"""
        return BeautifulSoup(html, 'html.parser')
    
    def extract_text(self, soup, selector):
        """Extrai texto de um seletor CSS"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None
    
    def extract_all(self, soup, selector):
        """Extrai todos os textos de um seletor"""
        elements = soup.select(selector)
        return [el.get_text(strip=True) for el in elements]
    
    def extract_links(self, soup):
        """Extrai todos os links"""
        links = []
        for a in soup.find_all('a', href=True):
            url = urljoin(self.base_url, a['href'])
            if self._is_valid_url(url):
                links.append({
                    'url': url,
                    'text': a.get_text(strip=True)
                })
        return links
    
    def _is_valid_url(self, url):
        """Verifica se URL é válida"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def scrape_page(self, url):
        """Scrape uma página"""
        response = self.fetch(url)
        if not response:
            return None
        
        soup = self.parse(response.content)
        
        return {
            'url': url,
            'title': self.extract_text(soup, 'title'),
            'h1': self.extract_all(soup, 'h1'),
            'h2': self.extract_all(soup, 'h2'),
            'paragraphs': len(soup.find_all('p')),
            'images': len(soup.find_all('img')),
            'links': len(soup.find_all('a')),
            'timestamp': datetime.now().isoformat()
        }
    
    def scrape_multiple(self, urls):
        """Scrape múltiplas URLs"""
        for url in urls:
            data = self.scrape_page(url)
            if data:
                self.data.append(data)
                logging.info(f"✅ Scraped: {url}")
        return self.data
    
    def save_json(self, filename=None):
        """Salva em JSON"""
        if not filename:
            filename = f'scrape_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"✅ Salvo em {filename}")
        return filename
    
    def save_csv(self, filename=None):
        """Salva em CSV"""
        if not filename:
            filename = f'scrape_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        if not self.data:
            logging.warning("Nenhum dado para salvar")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            
            for row in self.data:
                # Converter listas para string
                row_copy = row.copy()
                for key, value in row_copy.items():
                    if isinstance(value, list):
                        row_copy[key] = ' | '.join(str(v) for v in value)
                writer.writerow(row_copy)
        
        logging.info(f"✅ Salvo em {filename}")
        return filename

# Exemplo de uso
if __name__ == "__main__":
    # Criar scraper
    scraper = WebScraper("https://example.com", delay=1.0)
    
    # Scrape uma página
    urls = [
        "https://example.com",
        "https://example.com/about"
    ]
    
    # Executar scraping
    results = scraper.scrape_multiple(urls)
    
    # Salvar resultados
    scraper.save_json()
    scraper.save_csv()
    
    # Mostrar resumo
    print(f"\\n📊 Resumo:")
    print(f"   Páginas: {len(results)}")
    print(f"   Total H1: {sum(len(r.get('h1', [])) for r in results)}")
    print(f"   Total H2: {sum(len(r.get('h2', [])) for r in results)}")
''',
            "lang": "python",
            "ext": ".py"
        }
    }
}

# ==================== TELA DE LOGIN ====================
if not st.session_state.authenticated:
    st.markdown("""
    <div class="header-ultra">
        <h1>🎮 ScriptMaster AI Pro</h1>
        <p>Gerador de Código com IA • Interface Premium • Recursos Ilimitados</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 🔐 Entrar no Sistema")
        
        username = st.text_input("👤 Seu nome de usuário", placeholder="Digite seu nome", key="login_username")
        access_code = st.text_input("🎫 Código VIP (opcional)", type="password", placeholder="Cole seu código VIP", key="login_code")
        
        remember = st.checkbox("🔒 Manter conectado e salvar dados", value=True)
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 ENTRAR VIP", use_container_width=True, type="primary"):
                if not username:
                    st.error("❌ Digite seu nome!")
                elif not access_code:
                    st.error("❌ Digite o código VIP!")
                elif access_code == MASTER_CODE:
                    st.session_state.authenticated = True
                    st.session_state.is_master = True
                    st.session_state.username = username
                    st.session_state.vip_until = None
                    
                    if remember:
                        save_login(username, True, None)
                    
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
                
                st.rerun()
        
        st.divider()
        
        st.info("""
        **💡 Dica:** Marque "Manter conectado" para salvar:
        - ✅ Seu login
        - ✅ Histórico de códigos
        - ✅ Scripts favoritos
        - ✅ Conversas do chat
        """)
    
    with col2:
        st.markdown("### ⚡ Comparativo de Planos")
        
        col_free, col_vip = st.columns(2)
        
        with col_free:
            st.markdown("""
            <div style="background: #2d2d44; padding: 1.5rem; border-radius: 16px; border: 1px solid #444;">
                <h4 style="color: #a0a0a0; margin:0;">🆓 GRÁTIS</h4>
                <hr style="border-color: #444;">
                <p style="color: #888; font-size: 14px;">
                    ✅ 4 gerações/dia<br>
                    ✅ 10 msgs chat/dia<br>
                    ✅ Templates básicos<br>
                    ❌ Histórico limitado<br>
                    ❌ Sem favoritos salvos
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_vip:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #FFD700, #FFA500); padding: 1.5rem; border-radius: 16px;">
                <h4 style="color: #1a1a2e; margin:0;">👑 VIP</h4>
                <hr style="border-color: rgba(0,0,0,0.2);">
                <p style="color: #1a1a2e; font-size: 14px;">
                    ✅ Geração ILIMITADA<br>
                    ✅ Chat ILIMITADO<br>
                    ✅ TODOS templates<br>
                    ✅ Histórico completo<br>
                    ✅ Favoritos salvos
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### 💻 O que você pode criar")
        st.markdown("""
        - 🎮 **Jogos HTML5** para Android (PWA)
        - 🕹️ **Godot 4.x** Scripts completos
        - 🛡️ **Game Guardian** Hacks de memória
        - 🤖 **Bots Discord/Telegram**
        - 🐍 **Python** Web scrapers, APIs
        - 💾 **Muito mais...**
        """)
    
    st.stop()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown(f"""
    <div class="welcome-box">
        <h3>👋 {st.session_state.username}</h3>
        <p style="margin:0; opacity:0.9; font-size:14px;">
            {"🔥 ADMIN" if st.session_state.is_master else "👑 VIP" if is_vip_active() else "🆓 Free"}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Badge
    if st.session_state.is_master:
        st.markdown('<div class="master-badge">🔥 ADMINISTRADOR</div>', unsafe_allow_html=True)
    elif is_vip_active():
        dias_restantes = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<div class="vip-badge">👑 VIP - {dias_restantes}d</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="free-badge">🆓 Modo Gratuito</div>', unsafe_allow_html=True)
        
        # Medidor de uso
        usage = get_usage_stats()
        gen_used = usage.get("generate", 0)
        chat_used = usage.get("chat", 0)
        
        st.markdown("#### 📊 Uso Diário")
        
        gen_percent = min(100, (gen_used / DAILY_LIMIT_FREE) * 100)
        gen_color = "green" if gen_percent < 50 else "yellow" if gen_percent < 80 else "red"
        
        st.markdown(f"""
        <div class="usage-meter">
            <div style="display:flex; justify-content:space-between; color:white; font-size:14px;">
                <span>⚡ Gerações</span>
                <span>{gen_used}/{DAILY_LIMIT_FREE}</span>
            </div>
            <div class="usage-bar">
                
