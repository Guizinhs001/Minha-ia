import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
import re
import base64
import time

# ====== CONFIGURAÇÃO DA PÁGINA ======
st.set_page_config(
    page_title="ScriptMaster AI Pro 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CÓDIGO MASTER (SECRETO) ======
MASTER_CODE = "GuizinhsDono"

# ====== LIMITES DE USO ======
DAILY_LIMIT_FREE = 4  # Prompts por dia para usuários gratuitos
DAILY_LIMIT_CHAT_FREE = 10  # Mensagens de chat por dia para gratuitos

# ====== CSS PREMIUM AVANÇADO ======
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --accent: #f59e0b;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --dark: #0f172a;
        --darker: #020617;
        --light: #f8fafc;
        --gray: #64748b;
        --border: #334155;
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Remove default Streamlit styles */
    .stApp {
        background: linear-gradient(135deg, var(--darker) 0%, #1e1b4b 50%, var(--dark) 100%);
    }
    
    /* Header Premium */
    .header-ultra {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6366f1 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4),
                    0 0 100px rgba(139, 92, 246, 0.2);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .header-ultra::before {
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
    
    .header-ultra h1 {
        color: white;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
        letter-spacing: -0.02em;
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
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        animation: pulse-glow 2s infinite;
        box-shadow: 0 4px 20px rgba(220, 38, 38, 0.5);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    @keyframes pulse-glow {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 4px 20px rgba(220, 38, 38, 0.5);
        }
        50% { 
            transform: scale(1.02);
            box-shadow: 0 6px 30px rgba(220, 38, 38, 0.7);
        }
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.5);
        font-size: 0.9rem;
    }
    
    .free-badge {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Cards */
    .premium-card {
        background: linear-gradient(145deg, rgba(30,27,75,0.8) 0%, rgba(15,23,42,0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    
    .premium-card:hover {
        border-color: rgba(99, 102, 241, 0.6);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2);
    }
    
    /* Chat Styles - Melhor que ChatGPT */
    .chat-container {
        background: linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(30,27,75,0.95) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: inset 0 2px 20px rgba(0,0,0,0.3);
    }
    
    .chat-message {
        display: flex;
        margin-bottom: 1.5rem;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .chat-message.user {
        justify-content: flex-end;
    }
    
    .chat-message.assistant {
        justify-content: flex-start;
    }
    
    .message-bubble {
        max-width: 80%;
        padding: 1rem 1.25rem;
        border-radius: 18px;
        position: relative;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .message-bubble.user {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border-bottom-right-radius: 4px;
    }
    
    .message-bubble.assistant {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #e2e8f0;
        border-bottom-left-radius: 4px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        margin: 0 0.75rem;
        flex-shrink: 0;
    }
    
    .message-avatar.user {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        order: 1;
    }
    
    .message-avatar.assistant {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }
    
    .message-content {
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .message-time {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.5);
        margin-top: 0.5rem;
        text-align: right;
    }
    
    .message-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
        opacity: 0;
        transition: opacity 0.2s;
    }
    
    .message-bubble:hover .message-actions {
        opacity: 1;
    }
    
    .action-btn {
        background: rgba(255,255,255,0.1);
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        color: rgba(255,255,255,0.7);
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .action-btn:hover {
        background: rgba(255,255,255,0.2);
        color: white;
    }
    
    /* Usage Counter */
    .usage-counter {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .usage-bar {
        height: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .usage-fill {
        height: 100%;
        background: linear-gradient(90deg, #10b981, #6366f1, #8b5cf6);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    .usage-fill.warning {
        background: linear-gradient(90deg, #f59e0b, #ef4444);
    }
    
    .usage-fill.danger {
        background: #ef4444;
    }
    
    /* Code Editor */
    .code-editor-container {
        background: #0d1117;
        border-radius: 12px;
        border: 1px solid #30363d;
        overflow: hidden;
    }
    
    .code-header {
        background: #161b22;
        padding: 0.75rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 1px solid #30363d;
    }
    
    .code-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    
    .code-dot.red { background: #ff5f56; }
    .code-dot.yellow { background: #ffbd2e; }
    .code-dot.green { background: #27c93f; }
    
    /* Buttons Premium */
    .btn-premium {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    .btn-premium:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
    }
    
    /* Welcome Box */
    .welcome-box {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    }
    
    .welcome-box h3 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-card {
        background: linear-gradient(145deg, rgba(30,27,75,0.6) 0%, rgba(15,23,42,0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-3px);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
    
    /* Animations */
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); }
        50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.6); }
    }
    
    /* Scrollbar Custom */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8b5cf6, #a78bfa);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.5);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #94a3b8;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
    }
    
    /* Input Styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: rgba(30, 27, 75, 0.5) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
    }
    
    /* VIP Info Card */
    .vip-info-card {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Login Card */
    .login-card {
        background: linear-gradient(145deg, rgba(30,27,75,0.9) 0%, rgba(15,23,42,0.95) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    
    /* Template Card */
    .template-card {
        background: linear-gradient(145deg, rgba(30,27,75,0.6) 0%, rgba(15,23,42,0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .template-card:hover {
        border-color: rgba(99, 102, 241, 0.6);
        background: linear-gradient(145deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        transform: translateX(5px);
    }
    
    /* Footer */
    .footer-premium {
        background: linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(30,27,75,0.9) 100%);
        border-top: 1px solid rgba(99, 102, 241, 0.2);
        padding: 1.5rem;
        border-radius: 16px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ====== FUNÇÕES DE PERSISTÊNCIA ======

def encode_data(data):
    """Codifica dados em base64 para URL"""
    try:
        json_str = json.dumps(data, ensure_ascii=False, default=str)
        return base64.urlsafe_b64encode(json_str.encode()).decode()
    except:
        return ""

def decode_data(encoded):
    """Decodifica dados de base64"""
    try:
        json_str = base64.urlsafe_b64decode(encoded.encode()).decode()
        return json.loads(json_str)
    except:
        return None

def generate_token(username, is_master, vip_days=0):
    """Gera token de login seguro"""
    data = f"{username}|{is_master}|{vip_days}|scriptmaster_v3"
    return hashlib.sha256(data.encode()).hexdigest()[:24]

def save_user_data():
    """Salva dados do usuário na URL"""
    try:
        user_data = {
            "username": st.session_state.get("username", ""),
            "is_master": st.session_state.get("is_master", False),
            "vip_days": 0,
            "usage_count": st.session_state.get("usage_count", 0),
            "chat_count": st.session_state.get("chat_count", 0),
            "last_reset": st.session_state.get("last_reset", datetime.now().strftime("%Y-%m-%d")),
            "saved_scripts": st.session_state.get("saved_scripts", [])[-20:],  # Últimos 20
            "favorites": st.session_state.get("favorites", [])[-10:],  # Últimos 10
            "chat_history": st.session_state.get("chat_history", [])[-50:],  # Últimas 50 mensagens
        }
        
        if st.session_state.get("vip_until"):
            user_data["vip_days"] = max(0, (st.session_state.vip_until - datetime.now()).days)
        
        encoded = encode_data(user_data)
        token = generate_token(
            user_data["username"], 
            user_data["is_master"], 
            user_data["vip_days"]
        )
        
        st.query_params["data"] = encoded
        st.query_params["token"] = token
        
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

def load_user_data():
    """Carrega dados do usuário da URL"""
    try:
        params = st.query_params
        
        if "data" in params and "token" in params:
            encoded = params.get("data", "")
            token = params.get("token", "")
            
            data = decode_data(encoded)
            
            if data:
                expected_token = generate_token(
                    data.get("username", ""),
                    data.get("is_master", False),
                    data.get("vip_days", 0)
                )
                
                if token == expected_token:
                    st.session_state.username = data.get("username", "")
                    st.session_state.is_master = data.get("is_master", False)
                    st.session_state.usage_count = data.get("usage_count", 0)
                    st.session_state.chat_count = data.get("chat_count", 0)
                    st.session_state.last_reset = data.get("last_reset", datetime.now().strftime("%Y-%m-%d"))
                    st.session_state.saved_scripts = data.get("saved_scripts", [])
                    st.session_state.favorites = data.get("favorites", [])
                    st.session_state.chat_history = data.get("chat_history", [])
                    
                    vip_days = data.get("vip_days", 0)
                    if vip_days > 0:
                        st.session_state.vip_until = datetime.now() + timedelta(days=vip_days)
                    elif data.get("is_master"):
                        st.session_state.vip_until = None
                    else:
                        st.session_state.vip_until = None
                    
                    st.session_state.authenticated = True
                    
                    # Reset diário
                    check_daily_reset()
                    
                    return True
        
        return False
    except:
        return False

def check_daily_reset():
    """Verifica e reseta limites diários"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.get("last_reset") != today:
        st.session_state.usage_count = 0
        st.session_state.chat_count = 0
        st.session_state.last_reset = today
        save_user_data()

def clear_all_data():
    """Limpa todos os dados"""
    st.query_params.clear()
    
    keys_to_clear = [
        'authenticated', 'is_master', 'vip_until', 'username',
        'current_script', 'saved_scripts', 'favorites', 'chat_history',
        'usage_count', 'chat_count', 'last_reset', 'created_codes',
        'script_history', 'current_language', 'editing_message'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            if key == 'authenticated':
                st.session_state[key] = False
            elif key in ['saved_scripts', 'favorites', 'chat_history', 'script_history']:
                st.session_state[key] = []
            elif key in ['usage_count', 'chat_count']:
                st.session_state[key] = 0
            else:
                st.session_state[key] = None

# ====== INICIALIZAÇÃO DO SESSION STATE ======
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
    "chat_history": [],
    "usage_count": 0,
    "chat_count": 0,
    "last_reset": datetime.now().strftime("%Y-%m-%d"),
    "editing_message": None,
    "chat_input_key": 0
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ====== AUTO-LOGIN ======
if not st.session_state.authenticated and not st.session_state.login_checked:
    st.session_state.login_checked = True
    if load_user_data():
        st.toast(f"✅ Bem-vindo de volta, {st.session_state.username}!", icon="🎉")

# ====== CONFIGURAR API ======
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("❌ Chave API não configurada!")
    st.code("""
# Adicione no arquivo .streamlit/secrets.toml:
GEMINI_API_KEY = "sua_chave_aqui"
""")
    st.info("💡 Obtenha sua chave em: https://makersuite.google.com/app/apikey")
    st.stop()

# ====== FUNÇÕES AUXILIARES ======

def is_vip_active():
    """Verifica se VIP está ativo"""
    if st.session_state.is_master:
        return True
    if st.session_state.vip_until:
        return datetime.now() < st.session_state.vip_until
    return False

def can_use_generation():
    """Verifica se pode usar geração"""
    if is_vip_active():
        return True, float('inf')
    
    remaining = DAILY_LIMIT_FREE - st.session_state.usage_count
    return remaining > 0, remaining

def can_use_chat():
    """Verifica se pode usar chat"""
    if is_vip_active():
        return True, float('inf')
    
    remaining = DAILY_LIMIT_CHAT_FREE - st.session_state.chat_count
    return remaining > 0, remaining

def increment_usage():
    """Incrementa contador de uso"""
    st.session_state.usage_count += 1
    save_user_data()

def increment_chat():
    """Incrementa contador de chat"""
    st.session_state.chat_count += 1
    save_user_data()

@st.cache_resource
def get_models():
    """Obtém modelos disponíveis"""
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        return []

def detect_language(code):
    """Detecta a linguagem do código"""
    code_lower = code.lower()
    
    patterns = {
        ('extends', 'func', 'var '): ('gdscript', '.gd'),
        ('using unityengine', 'monobehaviour', 'void start'): ('csharp', '.cs'),
        ('<!doctype', '<html', '<head'): ('html', '.html'),
        ('import react', 'usestate', 'useeffect'): ('jsx', '.jsx'),
        ('function(', 'gg.', 'memory'): ('lua', '.lua'),
        ('def ', 'import ', 'class ', 'if __name__'): ('python', '.py'),
        ('select ', 'from ', 'where ', 'insert'): ('sql', '.sql'),
        ('function ', 'const ', 'let ', 'var '): ('javascript', '.js'),
        ('#!/bin/bash', 'echo ', 'if ['): ('bash', '.sh'),
    }
    
    for keywords, result in patterns.items():
        if any(kw in code_lower for kw in keywords):
            return result
    
    return ('python', '.py')

def render_usage_counter():
    """Renderiza contador de uso"""
    can_gen, remaining_gen = can_use_generation()
    can_chat_use, remaining_chat = can_use_chat()
    
    if is_vip_active():
        st.markdown("""
        <div class="usage-counter">
            <span style="color: #f59e0b; font-weight: 600;">👑 USO ILIMITADO</span>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #94a3b8;">
                Você tem acesso VIP sem limites!
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        gen_percent = (st.session_state.usage_count / DAILY_LIMIT_FREE) * 100
        chat_percent = (st.session_state.chat_count / DAILY_LIMIT_CHAT_FREE) * 100
        
        gen_class = "danger" if gen_percent >= 100 else "warning" if gen_percent >= 75 else ""
        chat_class = "danger" if chat_percent >= 100 else "warning" if chat_percent >= 75 else ""
        
        st.markdown(f"""
        <div class="usage-counter">
            <div style="margin-bottom: 1rem;">
                <span style="color: #e2e8f0; font-weight: 500;">⚡ Gerações: {st.session_state.usage_count}/{DAILY_LIMIT_FREE}</span>
                <div class="usage-bar">
                    <div class="usage-fill {gen_class}" style="width: {min(100, gen_percent)}%"></div>
                </div>
            </div>
            <div>
                <span style="color: #e2e8f0; font-weight: 500;">💬 Chat: {st.session_state.chat_count}/{DAILY_LIMIT_CHAT_FREE}</span>
                <div class="usage-bar">
                    <div class="usage-fill {chat_class}" style="width: {min(100, chat_percent)}%"></div>
                </div>
            </div>
            <p style="margin: 0.75rem 0 0 0; font-size: 0.8rem; color: #64748b;">
                🔄 Renova à meia-noite
            </p>
        </div>
        """, unsafe_allow_html=True)

# ====== TEMPLATES EXPANDIDOS ======
TEMPLATES = {
    "🎮 Jogos Mobile (Android)": {
        "HTML5 Android - Jogo Touch Completo": {
            "code": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Mobile Game - Android Ready</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            touch-action: manipulation;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
            user-select: none;
        }
        
        html, body {
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #000;
        }
        
        body {
            display: flex;
            flex-direction: column;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        #gameContainer {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            position: relative;
        }
        
        #gameCanvas {
            display: block;
            background: #0f0f23;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 255, 136, 0.2);
        }
        
        #hud {
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            z-index: 100;
        }
        
        .hud-item {
            color: #fff;
            font-size: 18px;
            font-weight: bold;
            text-shadow: 0 2px 10px rgba(0, 255, 136, 0.5);
        }
        
        .hud-item span {
            color: #00ff88;
        }
        
        #controls {
            position: absolute;
            bottom: 20px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-between;
            padding: 0 20px;
            z-index: 100;
        }
        
        .control-group {
            display: flex;
            gap: 10px;
        }
        
        .control-btn {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            border: 3px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.1s ease;
            backdrop-filter: blur(5px);
        }
        
        .control-btn:active {
            transform: scale(0.9);
            background: rgba(0, 255, 136, 0.4);
            border-color: #00ff88;
        }
        
        .action-btn {
            width: 90px;
            height: 90px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            border: none;
            font-size: 28px;
        }
        
        .action-btn:active {
            background: linear-gradient(135deg, #00cc6a, #009950);
        }
        
        #pauseOverlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        #pauseOverlay.active {
            display: flex;
        }
        
        .overlay-title {
            color: #fff;
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 30px;
            text-shadow: 0 0 20px #00ff88;
        }
        
        .overlay-btn {
            padding: 20px 60px;
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            border: none;
            border-radius: 50px;
            margin: 10px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .overlay-btn:active {
            transform: scale(0.95);
        }
        
        .overlay-btn.secondary {
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        
        #startScreen {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }
        
        .game-title {
            font-size: 56px;
            font-weight: 900;
            background: linear-gradient(135deg, #00ff88, #00cc6a, #667eea);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .game-subtitle {
            color: rgba(255, 255, 255, 0.7);
            font-size: 18px;
            margin-bottom: 50px;
        }
        
        .start-btn {
            padding: 25px 80px;
            font-size: 28px;
            font-weight: bold;
            color: #000;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            border: none;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 10px 40px rgba(0, 255, 136, 0.4);
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        /* Joystick Virtual */
        #joystickContainer {
            position: relative;
            width: 140px;
            height: 140px;
        }
        
        #joystickBase {
            position: absolute;
            width: 140px;
            height: 140px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
            border: 3px solid rgba(255, 255, 255, 0.2);
        }
        
        #joystickHandle {
            position: absolute;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.5);
        }
    </style>
</head>
<body>
    <!-- Tela Inicial -->
    <div id="startScreen">
        <div class="game-title">🎮 MOBILE GAME</div>
        <div class="game-subtitle">Toque para Começar</div>
        <button class="start-btn" onclick="startGame()">▶ JOGAR</button>
    </div>
    
    <!-- Container do Jogo -->
    <div id="gameContainer">
        <!-- HUD -->
        <div id="hud">
            <div class="hud-item">⭐ <span id="scoreDisplay">0</span></div>
            <div class="hud-item">❤️ <span id="livesDisplay">3</span></div>
            <div class="hud-item" onclick="pauseGame()">⏸️</div>
        </div>
        
        <!-- Canvas -->
        <canvas id="gameCanvas"></canvas>
        
        <!-- Controles Touch -->
        <div id="controls">
            <div id="joystickContainer">
                <div id="joystickBase"></div>
                <div id="joystickHandle"></div>
            </div>
            <div class="control-group">
                <button class="control-btn action-btn" id="btnAction">⚡</button>
            </div>
        </div>
    </div>
    
    <!-- Overlay de Pausa -->
    <div id="pauseOverlay">
        <div class="overlay-title">⏸️ PAUSADO</div>
        <button class="overlay-btn" onclick="resumeGame()">▶ CONTINUAR</button>
        <button class="overlay-btn secondary" onclick="restartGame()">🔄 REINICIAR</button>
    </div>

    <script>
        // ========== CONFIGURAÇÃO ==========
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Ajustar canvas para mobile
        function resizeCanvas() {
            const container = document.getElementById('gameContainer');
            const maxWidth = Math.min(window.innerWidth - 40, 800);
            const maxHeight = Math.min(window.innerHeight - 250, 600);
            
            canvas.width = maxWidth;
            canvas.height = maxHeight;
        }
        
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // ========== ESTADO DO JOGO ==========
        let gameState = {
            running: false,
            paused: false,
            score: 0,
            lives: 3,
            level: 1
        };
        
        // ========== PLAYER ==========
        const player = {
            x: 100,
            y: 0,
            width: 50,
            height: 50,
            velocityX: 0,
            velocityY: 0,
            speed: 8,
            jumpPower: -18,
            grounded: false,
            color: '#00ff88'
        };
        
        // ========== FÍSICA ==========
        const physics = {
            gravity: 0.8,
            friction: 0.85,
            groundY: 0
        };
        
        // ========== OBJETOS DO JOGO ==========
        let platforms = [];
        let coins = [];
        let enemies = [];
        let particles = [];
        
        // ========== CONTROLES ==========
        const controls = {
            left: false,
            right: false,
            jump: false,
            action: false,
            joystickX: 0,
            joystickY: 0
        };
        
        // ========== JOYSTICK VIRTUAL ==========
        const joystickContainer = document.getElementById('joystickContainer');
        const joystickHandle = document.getElementById('joystickHandle');
        const joystickBase = document.getElementById('joystickBase');
        
        let joystickActive = false;
        let joystickStartX = 0;
        let joystickStartY = 0;
        
        joystickContainer.addEventListener('touchstart', (e) => {
            e.preventDefault();
            joystickActive = true;
            const touch = e.touches[0];
            const rect = joystickContainer.getBoundingClientRect();
            joystickStartX = rect.left + rect.width / 2;
            joystickStartY = rect.top + rect.height / 2;
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!joystickActive) return;
            e.preventDefault();
            
            const touch = e.touches[0];
            const deltaX = touch.clientX - joystickStartX;
            const deltaY = touch.clientY - joystickStartY;
            
            const maxDistance = 50;
            const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY), maxDistance);
            const angle = Math.atan2(deltaY, deltaX);
            
            const moveX = Math.cos(angle) * distance;
            const moveY = Math.sin(angle) * distance;
            
            joystickHandle.style.transform = `translate(calc(-50% + ${moveX}px), calc(-50% + ${moveY}px))`;
            
            controls.joystickX = moveX / maxDistance;
            controls.joystickY = moveY / maxDistance;
        });
        
        document.addEventListener('touchend', () => {
            joystickActive = false;
            joystickHandle.style.transform = 'translate(-50%, -50%)';
            controls.joystickX = 0;
            controls.joystickY = 0;
        });
        
        // Botão de ação
        const btnAction = document.getElementById('btnAction');
        
        btnAction.addEventListener('touchstart', (e) => {
            e.preventDefault();
            controls.action = true;
            if (player.grounded) {
                player.velocityY = player.jumpPower;
                player.grounded = false;
                createParticles(player.x + player.width/2, player.y + player.height, '#00ff88', 10);
            }
        });
        
        btnAction.addEventListener('touchend', () => {
            controls.action = false;
        });
        
        // ========== PARTÍCULAS ==========
        class Particle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 8;
                this.vy = (Math.random() - 0.5) * 8;
                this.radius = Math.random() * 4 + 2;
                this.color = color;
                this.life = 30;
                this.maxLife = 30;
            }
            
            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.vy += 0.2;
                this.life--;
            }
            
            draw() {
                ctx.globalAlpha = this.life / this.maxLife;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }
        
        function createParticles(x, y, color, count) {
            for (let i = 0; i < count; i++) {
                particles.push(new Particle(x, y, color));
            }
        }
        
        // ========== INICIALIZAÇÃO ==========
        function initGame() {
            physics.groundY = canvas.height - 60;
            player.y = physics.groundY - player.height;
            
            // Criar plataformas
            platforms = [
                { x: 0, y: physics.groundY, width: canvas.width, height: 60, color: '#2d3436' }
            ];
            
            // Criar plataformas flutuantes
            for (let i = 0; i < 5; i++) {
                platforms.push({
                    x: Math.random() * (canvas.width - 150) + 50,
                    y: physics.groundY - 100 - (i * 80),
                    width: 100 + Math.random() * 50,
                    height: 20,
                    color: '#6c5ce7'
                });
            }
            
            // Criar moedas
            coins = [];
            for (let i = 0; i < 10; i++) {
                coins.push({
                    x: Math.random() * (canvas.width - 50) + 25,
                    y: Math.random() * (canvas.height - 200) + 50,
                    radius: 15,
                    collected: false,
                    bobOffset: Math.random() * Math.PI * 2
                });
            }
            
            gameState.score = 0;
            gameState.lives = 3;
            updateHUD();
        }
        
        function updateHUD() {
            document.getElementById('scoreDisplay').textContent = gameState.score;
            document.getElementById('livesDisplay').textContent = gameState.lives;
        }
        
        // ========== GAME LOOP ==========
        function update() {
            if (!gameState.running || gameState.paused) return;
            
            // Movimento do player via joystick
            player.velocityX = controls.joystickX * player.speed;
            
            // Aplicar gravidade
            player.velocityY += physics.gravity;
            
            // Atualizar posição
            player.x += player.velocityX;
            player.y += player.velocityY;
            
            // Colisão com plataformas
            player.grounded = false;
            for (let platform of platforms) {
                if (player.x < platform.x + platform.width &&
                    player.x + player.width > platform.x &&
                    player.y + player.height > platform.y &&
                    player.y + player.height < platform.y + platform.height + 20 &&
                    player.velocityY >= 0) {
                    
                    player.y = platform.y - player.height;
                    player.velocityY = 0;
                    player.grounded = true;
                }
            }
            
            // Limites da tela
            if (player.x < 0) player.x = 0;
            if (player.x + player.width > canvas.width) player.x = canvas.width - player.width;
            
            // Coletar moedas
            for (let coin of coins) {
                if (!coin.collected) {
                    const dist = Math.hypot(
                        player.x + player.width/2 - coin.x,
                        player.y + player.height/2 - coin.y
                    );
                    
                    if (dist < player.width/2 + coin.radius) {
                        coin.collected = true;
                        gameState.score += 10;
                        updateHUD();
                        createParticles(coin.x, coin.y, '#ffd700', 15);
                    }
                }
            }
            
            // Atualizar partículas
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update();
                if (particles[i].life <= 0) {
                    particles.splice(i, 1);
                }
            }
        }
        
        function draw() {
            // Limpar canvas
            ctx.fillStyle = '#0f0f23';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Desenhar grid de fundo
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
            ctx.lineWidth = 1;
            const gridSize = 40;
            for (let x = 0; x < canvas.width; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
            
            // Desenhar plataformas
            for (let platform of platforms) {
                ctx.fillStyle = platform.color;
                ctx.fillRect(platform.x, platform.y, platform.width, platform.height);
                
                // Brilho superior
                ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                ctx.fillRect(platform.x, platform.y, platform.width, 3);
            }
            
            // Desenhar moedas
            const time = Date.now() / 200;
            for (let coin of coins) {
                if (!coin.collected) {
                    const bobY = Math.sin(time + coin.bobOffset) * 5;
                    
                    // Brilho
                    ctx.fillStyle = 'rgba(255, 215, 0, 0.3)';
                    ctx.beginPath();
                    ctx.arc(coin.x, coin.y + bobY, coin.radius + 5, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Moeda
                    ctx.fillStyle = '#ffd700';
                    ctx.beginPath();
                    ctx.arc(coin.x, coin.y + bobY, coin.radius, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Reflexo
                    ctx.fillStyle = '#fff';
                    ctx.beginPath();
                    ctx.arc(coin.x - 4, coin.y + bobY - 4, 4, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            // Desenhar partículas
            for (let particle of particles) {
                particle.draw();
            }
            
            // Desenhar player
            ctx.fillStyle = player.color;
            ctx.fillRect(player.x, player.y, player.width, player.height);
            
            // Olhos do player
            ctx.fillStyle = '#fff';
            ctx.fillRect(player.x + 10, player.y + 12, 10, 10);
            ctx.fillRect(player.x + 30, player.y + 12, 10, 10);
            
            // Pupilas
            ctx.fillStyle = '#000';
            const pupilOffset = controls.joystickX * 3;
            ctx.fillRect(player.x + 14 + pupilOffset, player.y + 16, 4, 4);
            ctx.fillRect(player.x + 34 + pupilOffset, player.y + 16, 4, 4);
            
            // Sombra do player
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.beginPath();
            ctx.ellipse(
                player.x + player.width/2,
                physics.groundY + 5,
                player.width/2,
                8,
                0, 0, Math.PI * 2
            );
            ctx.fill();
        }
        
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // ========== CONTROLES DO JOGO ==========
        function startGame() {
            document.getElementById('startScreen').style.display = 'none';
            gameState.running = true;
            initGame();
            gameLoop();
        }
        
        function pauseGame() {
            gameState.paused = true;
            document.getElementById('pauseOverlay').classList.add('active');
        }
        
        function resumeGame() {
            gameState.paused = false;
            document.getElementById('pauseOverlay').classList.remove('active');
        }
        
        function restartGame() {
            document.getElementById('pauseOverlay').classList.remove('active');
            gameState.paused = false;
            initGame();
        }
        
        // Prevenir scroll no mobile
        document.addEventListener('touchmove', (e) => {
            if (gameState.running) {
                e.preventDefault();
            }
        }, { passive: false });
    </script>
</body>
</html>''',
            "lang": "html",
            "ext": ".html"
        },
        
        "PWA Android - Endless Runner": {
            "code": '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#1a1a2e">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="data:application/json,{%22name%22:%22Endless%20Runner%22,%22short_name%22:%22Runner%22,%22start_url%22:%22.%22,%22display%22:%22standalone%22,%22background_color%22:%22%231a1a2e%22,%22theme_color%22:%22%2300ff88%22}">
    <title>Endless Runner - PWA Android</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
            -webkit-user-select: none;
            user-select: none;
        }
        
        html, body {
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #1a1a2e;
            font-family: 'Arial', sans-serif;
        }
        
        #game {
            width: 100%;
            height: 100%;
            position: relative;
        }
        
        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }
        
        .ui-overlay {
            position: absolute;
            color: white;
            pointer-events: none;
        }
        
        #score {
            top: env(safe-area-inset-top, 20px);
            left: 20px;
            font-size: 32px;
            font-weight: bold;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        
        #highscore {
            top: env(safe-area-inset-top, 20px);
            right: 20px;
            font-size: 18px;
            color: #ffd700;
        }
        
        #gameOver {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            pointer-events: auto;
        }
        
        #gameOver.active {
            display: flex;
        }
        
        #gameOver h1 {
            font-size: 48px;
            color: #ff4757;
            margin-bottom: 20px;
        }
        
        #gameOver p {
            font-size: 24px;
            color: white;
            margin-bottom: 30px;
        }
        
        #gameOver button {
            padding: 20px 60px;
            font-size: 24px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            border: none;
            border-radius: 50px;
            color: #000;
            font-weight: bold;
            cursor: pointer;
        }
        
        #tapToStart {
            position: absolute;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 24px;
            color: rgba(255,255,255,0.8);
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
    </style>
</head>
<body>
    <div id="game">
        <canvas id="canvas"></canvas>
        <div id="score" class="ui-overlay">0</div>
        <div id="highscore" class="ui-overlay">🏆 0</div>
        <div id="tapToStart">👆 TOQUE PARA PULAR</div>
        <div id="gameOver">
            <h1>💀 GAME OVER</h1>
            <p>Pontuação: <span id="finalScore">0</span></p>
            <button onclick="restartGame()">🔄 JOGAR NOVAMENTE</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        // Ajustar tamanho do canvas
        function resize() {
            canvas.width = window.innerWidth * window.devicePixelRatio;
            canvas.height = window.innerHeight * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        }
        resize();
        window.addEventListener('resize', resize);
        
        const W = () => window.innerWidth;
        const H = () => window.innerHeight;
        
        // Estado do jogo
        let gameStarted = false;
        let gameOver = false;
        let score = 0;
        let highScore = parseInt(localStorage.getItem('highScore')) || 0;
        let speed = 6;
        let frame = 0;
        
        // Atualizar highscore no display
        document.getElementById('highscore').textContent = '🏆 ' + highScore;
        
        // Player
        const player = {
            x: 80,
            y: 0,
            width: 50,
            height: 50,
            velocityY: 0,
            jumpPower: -15,
            gravity: 0.6,
            grounded: true,
            color: '#00ff88'
        };
        
        // Chão
        const groundHeight = 100;
        
        // Obstáculos
        let obstacles = [];
        let obstacleTimer = 0;
        
        // Partículas
        let particles = [];
        
        // Background parallax
        let bgOffset = 0;
        
        function getGroundY() {
            return H() - groundHeight;
        }
        
        // Inicializar player
        function initPlayer() {
            player.y = getGroundY() - player.height;
            player.velocityY = 0;
            player.grounded = true;
        }
        initPlayer();
        
        // Criar obstáculo
        function createObstacle() {
            const types = [
                { width: 30, height: 60, color: '#e74c3c' },
                { width: 50, height: 40, color: '#9b59b6' },
                { width: 25, height: 80, color: '#e67e22' }
            ];
            
            const type = types[Math.floor(Math.random() * types.length)];
            
            obstacles.push({
                x: W(),
                y: getGroundY() - type.height,
                width: type.width,
                height: type.height,
                color: type.color,
                passed: false
            });
        }
        
        // Criar partícula
        function createParticle(x, y, color) {
            for (let i = 0; i < 5; i++) {
                particles.push({
                    x: x,
                    y: y,
                    vx: (Math.random() - 0.5) * 4,
                    vy: Math.random() * -5,
                    radius: Math.random() * 4 + 2,
                    color: color,
                    life: 30
                });
            }
        }
        
        // Input
        function jump() {
            if (!gameStarted) {
                gameStarted = true;
                document.getElementById('tapToStart').style.display = 'none';
            }
            
            if (gameOver) return;
            
            if (player.grounded) {
                player.velocityY = player.jumpPower;
                player.grounded = false;
                createParticle(player.x + player.width/2, player.y + player.height, '#00ff88');
            }
        }
        
        // Eventos de toque
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            jump();
        });
        
        canvas.addEventListener('click', jump);
        
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                jump();
            }
        });
        
        // Atualizar jogo
        function update() {
            if (!gameStarted || gameOver) return;
            
            frame++;
            
            // Física do player
            player.velocityY += player.gravity;
            player.y += player.velocityY;
            
            // Colisão com chão
            if (player.y + player.height >= getGroundY()) {
                player.y = getGroundY() - player.height;
                player.velocityY = 0;
                player.grounded = true;
            }
            
            // Criar obstáculos
            obstacleTimer++;
            if (obstacleTimer > 90 - Math.min(score, 50)) {
                createObstacle();
                obstacleTimer = 0;
            }
            
            // Atualizar obstáculos
            for (let i = obstacles.length - 1; i >= 0; i--) {
                obstacles[i].x -= speed;
                
                // Pontuação
                if (!obstacles[i].passed && obstacles[i].x + obstacles[i].width < player.x) {
                    obstacles[i].passed = true;
                    score++;
                    document.getElementById('score').textContent = score;
                    
                    // Aumentar velocidade
                    if (score % 10 === 0) {
                        speed += 0.5;
                    }
                }
                
                // Remover fora da tela
                if (obstacles[i].x + obstacles[i].width < 0) {
                    obstacles.splice(i, 1);
                    continue;
                }
                
                // Colisão
                if (player.x < obstacles[i].x + obstacles[i].width &&
                    player.x + player.width > obstacles[i].x &&
                    player.y < obstacles[i].y + obstacles[i].height &&
                    player.y + player.height > obstacles[i].y) {
                    
                    endGame();
                }
            }
            
            // Atualizar partículas
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].x += particles[i].vx;
                particles[i].y += particles[i].vy;
                particles[i].vy += 0.2;
                particles[i].life--;
                
                if (particles[i].life <= 0) {
                    particles.splice(i, 1);
                }
            }
            
            // Background
            bgOffset = (bgOffset + speed * 0.5) % 100;
        }
        
        // Desenhar
        function draw() {
            // Fundo
            const gradient = ctx.createLinearGradient(0, 0, 0, H());
            gradient.addColorStop(0, '#1a1a2e');
            gradient.addColorStop(1, '#16213e');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, W(), H());
            
            // Grid de fundo
            ctx.strokeStyle = 'rgba(255,255,255,0.03)';
            ctx.lineWidth = 1;
            for (let x = -bgOffset; x < W(); x += 100) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, H());
                ctx.stroke();
            }
            
            // Chão
            ctx.fillStyle = '#2d3436';
            ctx.fillRect(0, getGroundY(), W(), groundHeight);
            
            // Linha do chão
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(0, getGroundY(), W(), 3);
            
            // Linhas decorativas do chão
            ctx.strokeStyle = 'rgba(0,255,136,0.2)';
            for (let x = -bgOffset * 2; x < W(); x += 50) {
                ctx.beginPath();
                ctx.moveTo(x, getGroundY() + 20);
                ctx.lineTo(x + 30, getGroundY() + 20);
                ctx.stroke();
            }
            
            // Partículas
            for (let p of particles) {
                ctx.globalAlpha = p.life / 30;
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.globalAlpha = 1;
            
            // Player
            ctx.fillStyle = player.color;
            ctx.fillRect(player.x, player.y, player.width, player.height);
            
            // Olhos do player
            ctx.fillStyle = '#fff';
            ctx.fillRect(player.x + 10, player.y + 12, 12, 12);
            ctx.fillRect(player.x + 28, player.y + 12, 12, 12);
            
            ctx.fillStyle = '#000';
            ctx.fillRect(player.x + 16, player.y + 18, 4, 4);
            ctx.fillRect(player.x + 34, player.y + 18, 4, 4);
            
            // Obstáculos
            for (let obs of obstacles) {
                ctx.fillStyle = obs.color;
                ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                
                // Brilho
                ctx.fillStyle = 'rgba(255,255,255,0.3)';
                ctx.fillRect(obs.x, obs.y, obs.width, 5);
            }
            
            // Efeito de rastro do player quando pulando
            if (!player.grounded) {
                ctx.fillStyle = 'rgba(0,255,136,0.2)';
                for (let i = 1; i <= 3; i++) {
                    ctx.fillRect(
                        player.x - i * 15,
                        player.y + i * 5,
                        player.width,
                        player.height
                    );
                }
            }
        }
        
        // Fim de jogo
        function endGame() {
            gameOver = true;
            
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('highScore', highScore);
                document.getElementById('highscore').textContent = '🏆 ' + highScore;
            }
            
            document.getElementById('finalScore').textContent = score;
            document.getElementById('gameOver').classList.add('active');
        }
        
        // Reiniciar
        function restartGame() {
            gameOver = false;
            gameStarted = true;
            score = 0;
            speed = 6;
            obstacles = [];
            particles = [];
            obstacleTimer = 0;
            
            document.getElementById('score').textContent = '0';
            document.getElementById('gameOver').classList.remove('active');
            
            initPlayer();
        }
        
        // Loop principal
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        gameLoop();
    </script>
</body>
</html>''',
            "lang": "html",
            "ext": ".html"
        }
    },
    
    "🎮 Godot 4.x": {
        "Player 2D Completo com Estados": {
            "code": '''extends CharacterBody2D
## Player 2D Completo para Godot 4.x
## Sistema de estados, animações e mecânicas avançadas

# ===== CONFIGURAÇÕES =====
@export_group("Movimento")
@export var speed: float = 300.0
@export var acceleration: float = 2000.0
@export var friction: float = 1500.0
@export var air_resistance: float = 200.0

@export_group("Pulo")
@export var jump_velocity: float = -450.0
@export var jump_cut_multiplier: float = 0.5
@export var coyote_time: float = 0.15
@export var jump_buffer_time: float = 0.15
@export var max_jumps: int = 2

@export_group("Dash")
@export var dash_speed: float = 600.0
@export var dash_duration: float = 0.2
@export var dash_cooldown: float = 0.5

# ===== ESTADOS =====
enum State { IDLE, RUN, JUMP, FALL, DASH, WALL_SLIDE, ATTACK, HURT, DEAD }
var current_state: State = State.IDLE

# ===== VARIÁVEIS =====
var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")
var jumps_remaining: int = max_jumps
var coyote_timer: float = 0.0
var jump_buffer_timer: float = 0.0
var dash_timer: float = 0.0
var dash_cooldown_timer: float = 0.0
var is_dashing: bool = false
var dash_direction: Vector2 = Vector2.ZERO
var facing_direction: int = 1
var is_attacking: bool = false

# ===== REFERÊNCIAS =====
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D
@onready var animation_player: AnimationPlayer = $AnimationPlayer
@onready var dust_particles: GPUParticles2D = $DustParticles
@onready var attack_area: Area2D = $AttackArea

# ===== SIGNALS =====
signal player_died
signal player_damaged(amount: int)
signal state_changed(new_state: State)

func _ready() -> void:
	jumps_remaining = max_jumps
	print("Player inicializado!")

func _physics_process(delta: float) -> void:
	update_timers(delta)
	
	match current_state:
		State.IDLE:
			state_idle(delta)
		State.RUN:
			state_run(delta)
		State.JUMP:
			state_jump(delta)
		State.FALL:
			state_fall(delta)
		State.DASH:
			state_dash(delta)
		State.WALL_SLIDE:
			state_wall_slide(delta)
		State.ATTACK:
			state_attack(delta)
		State.HURT:
			state_hurt(delta)
		State.DEAD:
			state_dead(delta)
	
	move_and_slide()

func update_timers(delta: float) -> void:
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

# ===== ESTADOS =====
func state_idle(delta: float) -> void:
	apply_gravity(delta)
	apply_friction(delta)
	play_animation("idle")
	
	if get_movement_input() != 0:
		change_state(State.RUN)
	elif can_jump():
		perform_jump()
	elif Input.is_action_just_pressed("dash") and can_dash():
		perform_dash()
	elif Input.is_action_just_pressed("attack"):
		change_state(State.ATTACK)
	elif not is_on_floor() and coyote_timer <= 0:
		change_state(State.FALL)

func state_run(delta: float) -> void:
	apply_gravity(delta)
	var direction = get_movement_input()
	
	if direction != 0:
		apply_acceleration(delta, direction)
		update_facing(direction)
		play_animation("run")
		emit_dust_particles()
	else:
		change_state(State.IDLE)
		return
	
	if can_jump():
		perform_jump()
	elif Input.is_action_just_pressed("dash") and can_dash():
		perform_dash()
	elif Input.is_action_just_pressed("attack"):
		change_state(State.ATTACK)
	elif not is_on_floor() and coyote_timer <= 0:
		change_state(State.FALL)

func state_jump(delta: float) -> void:
	apply_gravity(delta)
	var direction = get_movement_input()
	
	if direction != 0:
		apply_air_movement(delta, direction)
		update_facing(direction)
	
	# Corte do pulo
	if Input.is_action_just_released("jump") and velocity.y < 0:
		velocity.y *= jump_cut_multiplier
	
	play_animation("jump")
	
	if velocity.y >= 0:
		change_state(State.FALL)
	elif Input.is_action_just_pressed("jump") and jumps_remaining > 0:
		perform_jump()
	elif Input.is_action_just_pressed("dash") and can_dash():
		perform_dash()

func state_fall(delta: float) -> void:
	apply_gravity(delta)
	var direction = get_movement_input()
	
	if direction != 0:
		apply_air_movement(delta, direction)
		update_facing(direction)
	
	play_animation("fall")
	
	if is_on_floor():
		land()
	elif is_on_wall() and direction != 0:
		change_state(State.WALL_SLIDE)
	elif jump_buffer_timer > 0 and jumps_remaining > 0:
		perform_jump()
	elif Input.is_action_just_pressed("dash") and can_dash():
		perform_dash()

func state_dash(delta: float) -> void:
	dash_timer -= delta
	
	velocity = dash_direction * dash_speed
	play_animation("dash")
	
	if dash_timer <= 0:
		is_dashing = false
		dash_cooldown_timer = dash_cooldown
		if is_on_floor():
			change_state(State.IDLE)
		else:
			change_state(State.FALL)

func state_wall_slide(delta: float) -> void:
	velocity.y = min(velocity.y + gravity * 0.3 * delta, 100)
	play_animation("wall_slide")
	
	if is_on_floor():
		land()
	elif not is_on_wall():
		change_state(State.FALL)
	elif Input.is_action_just_pressed("jump"):
		perform_wall_jump()
	elif Input.is_action_just_pressed("dash") and can_dash():
		perform_dash()

func state_attack(_delta: float) -> void:
	play_animation("attack")
	velocity.x = move_toward(velocity.x, 0, friction * _delta)
	
	# A animação chama attack_finished quando termina
	if not is_attacking:
		if is_on_floor():
			change_state(State.IDLE)
		else:
			change_state(State.FALL)

func state_hurt(_delta: float) -> void:
	play_animation("hurt")
	# Controlado por AnimationPlayer

func state_dead(_delta: float) -> void:
	play_animation("dead")
	velocity = Vector2.ZERO

# ===== FUNÇÕES AUXILIARES =====
func get_movement_input() -> float:
	return Input.get_axis("move_left", "move_right")

func apply_gravity(delta: float) -> void:
	if not is_on_floor() and not is_dashing:
		velocity.y += gravity * delta

func apply_acceleration(delta: float, direction: float) -> void:
	velocity.x = move_toward(velocity.x, direction * speed, acceleration * delta)

func apply_friction(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0, friction * delta)

func apply_air_movement(delta: float, direction: float) -> void:
	velocity.x = move_toward(velocity.x, direction * speed, air_resistance * delta)

func update_facing(direction: float) -> void:
	if direction != 0:
		facing_direction = sign(direction) as int
		sprite.flip_h = direction < 0
		attack_area.scale.x = facing_direction

func can_jump() -> bool:
	return (jump_buffer_timer > 0 or Input.is_action_just_pressed("jump")) and \
		   (is_on_floor() or coyote_timer > 0 or jumps_remaining > 0)

func perform_jump() -> void:
	velocity.y = jump_velocity
	jumps_remaining -= 1
	coyote_timer = 0
	jump_buffer_timer = 0
	change_state(State.JUMP)
	emit_dust_particles()

func perform_wall_jump() -> void:
	var wall_normal = get_wall_normal()
	velocity = Vector2(wall_normal.x * speed * 0.8, jump_velocity * 0.9)
	jumps_remaining = max(jumps_remaining - 1, 0)
	change_state(State.JUMP)

func can_dash() -> bool:
	return dash_cooldown_timer <= 0 and not is_dashing

func perform_dash() -> void:
	is_dashing = true
	dash_timer = dash_duration
	dash_direction = Vector2(facing_direction, 0)
	
	if get_movement_input() != 0:
		dash_direction.x = sign(get_movement_input())
	
	change_state(State.DASH)

func land() -> void:
	jumps_remaining = max_jumps
	emit_dust_particles()
	
	if get_movement_input() != 0:
		change_state(State.RUN)
	else:
		change_state(State.IDLE)

func change_state(new_state: State) -> void:
	if current_state == new_state:
		return
	
	# Exit state
	match current_state:
		State.ATTACK:
			is_attacking = false
	
	# Enter state
	match new_state:
		State.ATTACK:
			is_attacking = true
	
	current_state = new_state
	emit_signal("state_changed", new_state)

func play_animation(anim_name: String) -> void:
	if sprite.animation != anim_name:
		sprite.play(anim_name)

func emit_dust_particles() -> void:
	if dust_particles:
		dust_particles.emitting = true

func take_damage(amount: int, knockback: Vector2 = Vector2.ZERO) -> void:
	emit_signal("player_damaged", amount)
	velocity = knockback
	change_state(State.HURT)

func die() -> void:
	change_state(State.DEAD)
	emit_signal("player_died")

func attack_finished() -> void:
	is_attacking = false
''',
            "lang": "gdscript",
            "ext": ".gd"
        },
        
        "Sistema de Inventário Completo": {
            "code": '''extends Node
class_name InventorySystem
## Sistema de Inventário Completo para Godot 4.x
## Suporta stacking, categorias, slots e serialização

# ===== SIGNALS =====
signal item_added(item: InventoryItem, slot: int)
signal item_removed(item: InventoryItem, slot: int)
signal item_used(item: InventoryItem)
signal inventory_changed()
signal slot_selected(slot: int)

# ===== CLASSES =====
class InventoryItem:
	var id: String
	var name: String
	var description: String
	var icon: Texture2D
	var category: String
	var max_stack: int
	var quantity: int
	var rarity: int  # 0=comum, 1=incomum, 2=raro, 3=épico, 4=lendário
	var usable: bool
	var custom_data: Dictionary
	
	func _init(_id: String = "", _name: String = "", _max_stack: int = 99):
		id = _id
		name = _name
		max_stack = _max_stack
		quantity = 1
		rarity = 0
		usable = false
		custom_data = {}
	
	func duplicate_item() -> InventoryItem:
		var new_item = InventoryItem.new(id, name, max_stack)
		new_item.description = description
		new_item.icon = icon
		new_item.category = category
		new_item.quantity = quantity
		new_item.rarity = rarity
		new_item.usable = usable
		new_item.custom_data = custom_data.duplicate()
		return new_item
	
	func to_dict() -> Dictionary:
		return {
			"id": id,
			"name": name,
			"description": description,
			"category": category,
			"max_stack": max_stack,
			"quantity": quantity,
			"rarity": rarity,
			"usable": usable,
			"custom_data": custom_data
		}
	
	static func from_dict(data: Dictionary) -> InventoryItem:
		var item = InventoryItem.new(data.get("id", ""), data.get("name", ""))
		item.description = data.get("description", "")
		item.category = data.get("category", "misc")
		item.max_stack = data.get("max_stack", 99)
		item.quantity = data.get("quantity", 1)
		item.rarity = data.get("rarity", 0)
		item.usable = data.get("usable", false)
		item.custom_data = data.get("custom_data", {})
		return item

class InventorySlot:
	var item: InventoryItem
	var locked: bool
	var category_filter: String
	
	func _init():
		item = null
		locked = false
		category_filter = ""
	
	func is_empty() -> bool:
		return item == null
	
	func can_accept(new_item: InventoryItem) -> bool:
		if locked:
			return false
		if category_filter != "" and new_item.category != category_filter:
			return false
		return true

# ===== CONFIGURAÇÃO =====
@export var max_slots: int = 20
@export var enable_stacking: bool = true
@export var auto_sort: bool = false

# ===== VARIÁVEIS =====
var slots: Array[InventorySlot] = []
var selected_slot: int = -1
var item_database: Dictionary = {}

func _ready():
	initialize_slots()
	load_item_database()

func initialize_slots() -> void:
	slots.clear()
	for i in range(max_slots):
		slots.append(InventorySlot.new())

func load_item_database() -> void:
	# Carregar itens do arquivo ou definir aqui
	# Exemplo de itens
	register_item("potion_health", "Poção de Vida", "Restaura 50 HP", "consumable", 20, true)
	register_item("potion_mana", "Poção de Mana", "Restaura 30 MP", "consumable", 20, true)
	register_item("sword_iron", "Espada de Ferro", "Uma espada comum", "weapon", 1, false, 1)
	register_item("sword_gold", "Espada de Ouro", "Uma espada dourada", "weapon", 1, false, 2)
	register_item("coin", "Moeda de Ouro", "Moeda do reino", "currency", 9999, false)
	register_item("gem_ruby", "Rubi", "Pedra preciosa vermelha", "gem", 99, false, 3)

func register_item(id: String, item_name: String, desc: String, category: String, 
				   max_stack: int, usable: bool, rarity: int = 0) -> void:
	var item = InventoryItem.new(id, item_name, max_stack)
	item.description = desc
	item.category = category
	item.usable = usable
	item.rarity = rarity
	item_database[id] = item

# ===== OPERAÇÕES DO INVENTÁRIO =====
func add_item(item_id: String, quantity: int = 1) -> int:
	"""Adiciona item ao inventário. Retorna quantidade não adicionada."""
	if not item_database.has(item_id):
		push_error("Item não encontrado: " + item_id)
		return quantity
	
	var template = item_database[item_id]
	var remaining = quantity
	
	# Primeiro, tentar stackar em slots existentes
	if enable_stacking:
		for i in range(slots.size()):
			if remaining <= 0:
				break
			
			var slot = slots[i]
			if slot.item != null and slot.item.id == item_id:
				var space = slot.item.max_stack - slot.item.quantity
				var to_add = min(remaining, space)
				
				if to_add > 0:
					slot.item.quantity += to_add
					remaining -= to_add
					emit_signal("item_added", slot.item, i)
	
	# Depois, adicionar em slots vazios
	while remaining > 0:
		var empty_slot = find_empty_slot()
		if empty_slot == -1:
			break
		
		var new_item = template.duplicate_item()
		var to_add = min(remaining, new_item.max_stack)
		new_item.quantity = to_add
		
		slots[empty_slot].item = new_item
		remaining -= to_add
		emit_signal("item_added", new_item, empty_slot)
	
	if remaining != quantity:
		emit_signal("inventory_changed")
		
		if auto_sort:
			sort_inventory()
	
	return remaining

func remove_item(item_id: String, quantity: int = 1) -> bool:
	"""Remove item do inventário. Retorna true se conseguiu remover tudo."""
	var remaining = quantity
	
	for i in range(slots.size() - 1, -1, -1):
		if remaining <= 0:
			break
		
		var slot = slots[i]
		if slot.item != null and slot.item.id == item_id:
			var to_remove = min(remaining, slot.item.quantity)
			slot.item.quantity -= to_remove
			remaining -= to_remove
			
			if slot.item.quantity <= 0:
				var removed_item = slot.item
				slot.item = null
				emit_signal("item_removed", removed_item, i)
	
	if remaining != quantity:
		emit_signal("inventory_changed")
	
	return remaining <= 0

func remove_item_at_slot(slot_index: int, quantity: int = 1) -> InventoryItem:
	"""Remove item de um slot específico."""
	if slot_index < 0 or slot_index >= slots.size():
		return null
	
	var slot = slots[slot_index]
	if slot.item == null:
		return null
	
	var removed_quantity = min(quantity, slot.item.quantity)
	var removed_item = slot.item.duplicate_item()
	removed_item.quantity = removed_quantity
	
	slot.item.quantity -= removed_quantity
	
	if slot.item.quantity <= 0:
		slot.item = null
	
	emit_signal("item_removed", removed_item, slot_index)
	emit_signal("inventory_changed")
	
	return removed_item

func use_item(slot_index: int) -> bool:
	"""Usa um item do slot especificado."""
	if slot_index < 0 or slot_index >= slots.size():
		return false
	
	var slot = slots[slot_index]
	if slot.item == null or not slot.item.usable:
		return false
	
	emit_signal("item_used", slot.item)
	
	slot.item.quantity -= 1
	if slot.item.quantity <= 0:
		slot.item = null
	
	emit_signal("inventory_changed")
	return true

func move_item(from_slot: int, to_slot: int) -> bool:
	"""Move item entre slots."""
	if from_slot < 0 or from_slot >= slots.size():
		return false
	if to_slot < 0 or to_slot >= slots.size():
		return false
	if from_slot == to_slot:
		return false
	
	var from = slots[from_slot]
	var to = slots[to_slot]
	
	if from.item == null:
		return false
	
	if not to.can_accept(from.item):
		return false
	
	# Se o slot destino está vazio
	if to.item == null:
		to.item = from.item
		from.item = null
	# Se tem o mesmo item, tentar stackar
	elif to.item.id == from.item.id and enable_stacking:
		var space = to.item.max_stack - to.item.quantity
		var to_move = min(from.item.quantity, space)
		
		to.item.quantity += to_move
		from.item.quantity -= to_move
		
		if from.item.quantity <= 0:
			from.item = null
	# Se são itens diferentes, trocar
	else:
		if not from.can_accept(to.item):
			return false
		
		var temp = from.item
		from.item = to.item
		to.item = temp
	
	emit_signal("inventory_changed")
	return true

func swap_items(slot_a: int, slot_b: int) -> bool:
	"""Troca itens entre dois slots."""
	if slot_a < 0 or slot_a >= slots.size():
		return false
	if slot_b < 0 or slot_b >= slots.size():
		return false
	
	var temp = slots[slot_a].item
	slots[slot_a].item = slots[slot_b].item
	slots[slot_b].item = temp
	
	emit_signal("inventory_changed")
	return true

# ===== CONSULTAS =====
func get_item_at_slot(slot_index: int) -> InventoryItem:
	if slot_index < 0 or slot_index >= slots.size():
		return null
	return slots[slot_index].item

func find_item(item_id: String) -> int:
	"""Encontra o primeiro slot com o item especificado."""
	for i in range(slots.size()):
		if slots[i].item != null and slots[i].item.id == item_id:
			return i
	return -1

func find_empty_slot() -> int:
	"""Encontra o primeiro slot vazio."""
	for i in range(slots.size()):
		if slots[i].item == null and not slots[i].locked:
			return i
	return -1

func count_item(item_id: String) -> int:
	"""Conta a quantidade total de um item."""
	var total = 0
	for slot in slots:
		if slot.item != null and slot.item.id == item_id:
			total += slot.item.quantity
	return total

func has_item(item_id: String, quantity: int = 1) -> bool:
	"""Verifica se tem a quantidade especificada do item."""
	return count_item(item_id) >= quantity

func get_items_by_category(category: String) -> Array[InventoryItem]:
	"""Retorna todos os itens de uma categoria."""
	var items: Array[InventoryItem] = []
	for slot in slots:
		if slot.item != null and slot.item.category == category:
			items.append(slot.item)
	return items

func get_used_slots() -> int:
	"""Conta slots ocupados."""
	var count = 0
	for slot in slots:
		if slot.item != null:
			count += 1
	return count

func get_free_slots() -> int:
	"""Conta slots livres."""
	return max_slots - get_used_slots()

func is_full() -> bool:
	"""Verifica se o inventário está cheio."""
	return get_free_slots() == 0

# ===== ORGANIZAÇÃO =====
func sort_inventory() -> void:
	"""Organiza o inventário por categoria e nome."""
	var items: Array[InventoryItem] = []
	
	# Coletar todos os itens
	for slot in slots:
		if slot.item != null:
			items.append(slot.item)
			slot.item = null
	
	# Ordenar
	items.sort_custom(func(a, b):
		if a.category != b.category:
			return a.category < b.category
		if a.rarity != b.rarity:
			return a.rarity > b.rarity
		return a.name < b.name
	)
	
	# Colocar de volta
	var slot_index = 0
	for item in items:
		while slot_index < slots.size() and slots[slot_index].locked:
			slot_index += 1
		
		if slot_index < slots.size():
			slots[slot_index].item = item
			slot_index += 1
	
	emit_signal("inventory_changed")

func clear_inventory() -> void:
	"""Limpa todo o inventário."""
	for slot in slots:
		slot.item = null
	emit_signal("inventory_changed")

# ===== SELEÇÃO =====
func select_slot(slot_index: int) -> void:
	if slot_index >= 0 and slot_index < slots.size():
		selected_slot = slot_index
		emit_signal("slot_selected", slot_index)

func get_selected_item() -> InventoryItem:
	if selected_slot >= 0 and selected_slot < slots.size():
		return slots[selected_slot].item
	return null

# ===== SERIALIZAÇÃO =====
func save_inventory() -> Dictionary:
	"""Salva o inventário em um dicionário."""
	var data = {
		"max_slots": max_slots,
		"slots": []
	}
	
	for slot in slots:
		if slot.item != null:
			data.slots.append(slot.item.to_dict())
		else:
			data.slots.append(null)
	
	return data

func load_inventory(data: Dictionary) -> void:
	"""Carrega o inventário de um dicionário."""
	if data.has("max_slots"):
		max_slots = data.max_slots
		initialize_slots()
	
	if data.has("slots"):
		for i in range(min(data.slots.size(), slots.size())):
			if data.slots[i] != null:
				slots[i].item = InventoryItem.from_dict(data.slots[i])
	
	emit_signal("inventory_changed")

func save_to_file(path: String) -> void:
	"""Salva inventário em arquivo."""
	var file = FileAccess.open(path, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(save_inventory()))
		file.close()

func load_from_file(path: String) -> bool:
	"""Carrega inventário de arquivo."""
	if not FileAccess.file_exists(path):
		return false
	
	var file = FileAccess.open(path, FileAccess.READ)
	if file:
		var json = JSON.new()
		var result = json.parse(file.get_as_text())
		file.close()
		
		if result == OK:
			load_inventory(json.data)
			return true
	
	return false
''',
            "lang": "gdscript",
            "ext": ".gd"
        }
    },
    
    "🛡️ Game Guardian Scripts": {
        "GG Script - Básico com Menu": {
            "code": '''--[[
    Game Guardian Script - Template Básico
    Autor: ScriptMaster AI
    Versão: 1.0
    
    ATENÇÃO: Use apenas para fins educacionais!
]]

-- ========== CONFIGURAÇÃO ==========
gg.setVisible(false)
gg.toast("Script carregado!")

-- Variáveis globais
local scriptVersion = "1.0"
local scriptName = "Meu Script GG"
local isRunning = true

-- ========== FUNÇÕES AUXILIARES ==========

-- Função para mostrar mensagem
function showMessage(msg)
    gg.toast(msg)
end

-- Função para confirmar ação
function confirm(title, msg)
    return gg.alert(msg, "Sim", "Não", title) == 1
end

-- Função para entrada de texto
function inputText(title, default)
    local result = gg.prompt({title}, {default}, {"text"})
    if result then
        return result[1]
    end
    return nil
end

-- Função para entrada numérica
function inputNumber(title, default)
    local result = gg.prompt({title}, {tostring(default)}, {"number"})
    if result then
        return tonumber(result[1])
    end
    return nil
end

-- ========== FUNÇÕES DE HACK ==========

-- Função genérica de busca e edição
function searchAndEdit(value, newValue, dataType)
    gg.clearResults()
    gg.setRanges(gg.REGION_ANONYMOUS | gg.REGION_OTHER)
    
    gg.searchNumber(value, dataType)
    local results = gg.getResultsCount()
    
    if results > 0 then
        showMessage("Encontrados: " .. results .. " resultados")
        
        local t = gg.getResults(results)
        for i, v in ipairs(t) do
            t[i].value = newValue
        end
        gg.setValues(t)
        
        showMessage("Valores alterados para: " .. newValue)
        return true
    else
        showMessage("Nenhum resultado encontrado!")
        return false
    end
end

-- Busca por valor DWORD
function searchDword(value, newValue)
    return searchAndEdit(value, newValue, gg.TYPE_DWORD)
end

-- Busca por valor FLOAT
function searchFloat(value, newValue)
    return searchAndEdit(value, newValue, gg.TYPE_FLOAT)
end

-- Busca por valor DOUBLE
function searchDouble(value, newValue)
    return searchAndEdit(value, newValue, gg.TYPE_DOUBLE)
end

-- Hack de dinheiro (exemplo)
function hackMoney()
    local currentMoney = inputNumber("Digite seu dinheiro atual:", 0)
    if not currentMoney then return end
    
    local newMoney = inputNumber("Digite o novo valor:", 999999)
    if not newMoney then return end
    
    searchDword(currentMoney, newMoney)
end

-- Hack de vida (exemplo)
function hackHealth()
    local currentHP = inputNumber("Digite sua vida atual:", 100)
    if not currentHP then return end
    
    local newHP = inputNumber("Digite a nova vida:", 9999)
    if not newHP then return end
    
    -- Tenta como DWORD primeiro
    if not searchDword(currentHP, newHP) then
        -- Se falhar, tenta como FLOAT
        searchFloat(currentHP, newHP)
    end
end

-- Hack de velocidade (exemplo)
function hackSpeed()
    local speedValues = {1.0, 2.0, 3.0, 5.0, 10.0}
    local choice = gg.choice({"Normal (1x)", "2x", "3x", "5x", "10x"}, nil, "Escolha a velocidade:")
    
    if choice then
        local newSpeed = speedValues[choice]
        
        -- Busca valores de velocidade comuns
        gg.clearResults()
        gg.setRanges(gg.REGION_ANONYMOUS)
        gg.searchNumber("1.0", gg.TYPE_FLOAT)
        
        local results = gg.getResults(100)
        for i, v in ipairs(results) do
            results[i].value = newSpeed
        end
        gg.setValues(results)
        
        showMessage("Velocidade alterada para " .. newSpeed .. "x")
    end
end

-- Busca por grupo de valores
function searchGroup()
    local values = inputText("Digite valores separados por ';':", "100;200;300")
    if not values then return end
    
    gg.clearResults()
    gg.setRanges(gg.REGION_ANONYMOUS)
    gg.searchNumber(values, gg.TYPE_DWORD)
    
    local count = gg.getResultsCount()
    showMessage("Encontrados: " .. count .. " grupos")
end

-- Congelar valores
function freezeValues()
    local count = gg.getResultsCount()
    if count == 0 then
        showMessage("Nenhum resultado para congelar!")
        return
    end
    
    local results = gg.getResults(count)
    for i, v in ipairs(results) do
        results[i].freeze = true
    end
    gg.addListItems(results)
    
    showMessage(count .. " valores congelados!")
end

-- Descongelar valores
function unfreezeValues()
    local list = gg.getListItems()
    for i, v in ipairs(list) do
        list[i].freeze = false
    end
    gg.setValues(list)
    gg.clearList()
    
    showMessage("Valores descongelados!")
end

-- Limpar resultados
function clearAll()
    gg.clearResults()
    gg.clearList()
    showMessage("Tudo limpo!")
end

-- ========== MENU PRINCIPAL ==========

function mainMenu()
    local menu = gg.choice({
        "💰 Hack Dinheiro",
        "❤️ Hack Vida",
        "⚡ Hack Velocidade",
        "🔍 Busca por Grupo",
        "❄️ Congelar Valores",
        "🔥 Descongelar Valores",
        "🧹 Limpar Tudo",
        "ℹ️ Informações",
        "❌ Sair"
    }, nil, scriptName .. " v" .. scriptVersion)
    
    if menu == nil then
        return
    end
    
    if menu == 1 then
        hackMoney()
    elseif menu == 2 then
        hackHealth()
    elseif menu == 3 then
        hackSpeed()
    elseif menu == 4 then
        searchGroup()
    elseif menu == 5 then
        freezeValues()
    elseif menu == 6 then
        unfreezeValues()
    elseif menu == 7 then
        clearAll()
    elseif menu == 8 then
        gg.alert(
            "Script: " .. scriptName .. "\\n" ..
            "Versão: " .. scriptVersion .. "\\n" ..
            "Desenvolvido com ScriptMaster AI\\n\\n" ..
            "Use com responsabilidade!",
            "OK"
        )
    elseif menu == 9 then
        if confirm("Sair", "Deseja realmente sair?") then
            isRunning = false
            showMessage("Até logo!")
        end
    end
end

-- ========== LOOP PRINCIPAL ==========

while isRunning do
    if gg.isVisible() then
        gg.setVisible(false)
        mainMenu()
    end
    gg.sleep(100)
end

os.exit()
''',
            "lang": "lua",
            "ext": ".lua"
        },
        
        "GG Script - Avançado Multi-função": {
            "code": '''--[[
    Game Guardian Script Avançado
    Template Multi-função com Sistema de Offset
    Autor: ScriptMaster AI
    
    ⚠️ APENAS PARA FINS EDUCACIONAIS!
]]

-- ========== INICIALIZAÇÃO ==========
gg.setVisible(false)

local SCRIPT_NAME = "Advanced GG Script"
local SCRIPT_VERSION = "2.0"
local SCRIPT_AUTHOR = "ScriptMaster AI"

-- ========== CONFIGURAÇÕES ==========
local Config = {
    autoRefresh = false,
    refreshInterval = 1000,
    safeMode = true,
    logEnabled = true
}

-- ========== SISTEMA DE LOG ==========
local Log = {}

function Log.add(message)
    if Config.logEnabled then
        print("[" .. os.date("%H:%M:%S") .. "] " .. message)
    end
end

function Log.error(message)
    Log.add("ERROR: " .. message)
end

function Log.success(message)
    Log.add("SUCCESS: " .. message)
end

-- ========== FUNÇÕES UTILITÁRIAS ==========
local Utils = {}

function Utils.toast(msg)
    gg.toast(msg)
end

function Utils.alert(msg, title)
    title = title or SCRIPT_NAME
    gg.alert(msg, "OK", nil, title)
end

function Utils.confirm(msg, title)
    title = title or "Confirmação"
    return gg.alert(msg, "Sim", "Não", title) == 1
end

function Utils.input(prompts, defaults, types)
    return gg.prompt(prompts, defaults, types)
end

function Utils.choice(items, title)
    title = title or "Escolha uma opção:"
    return gg.choice(items, nil, title)
end

function Utils.sleep(ms)
    gg.sleep(ms)
end

-- ========== SISTEMA DE MEMÓRIA ==========
local Memory = {}

-- Definir ranges de memória
function Memory.setRanges(ranges)
    local rangeMap = {
        ["all"] = gg.REGION_ANONYMOUS | gg.REGION_OTHER | gg.REGION_JAVA_HEAP | gg.REGION_C_HEAP,
        ["anonymous"] = gg.REGION_ANONYMOUS,
        ["other"] = gg.REGION_OTHER,
        ["java"] = gg.REGION_JAVA_HEAP,
        ["c_heap"] = gg.REGION_C_HEAP,
        ["code"] = gg.REGION_CODE_APP,
        ["stack"] = gg.REGION_STACK,
        ["ashmem"] = gg.REGION_ASHMEM
    }
    
    local r = rangeMap[ranges] or ranges
    gg.setRanges(r)
end

-- Buscar valor único
function Memory.search(value, dataType, ranges)
    ranges = ranges or "anonymous"
    dataType = dataType or gg.TYPE_DWORD
    
    Memory.setRanges(ranges)
    gg.clearResults()
    
    gg.searchNumber(value, dataType)
    return gg.getResultsCount()
end

-- Buscar e editar
function Memory.searchAndEdit(oldValue, newValue, dataType, ranges)
    local count = Memory.search(oldValue, dataType, ranges)
    
    if count > 0 and count < 50000 then
        local results = gg.getResults(count)
        for i, v in ipairs(results) do
            results[i].value = newValue
        end
        gg.setValues(results)
        Log.success("Editados " .. count .. " valores")
        return true
    elseif count >= 50000 then
        Log.error("Muitos resultados: " .. count)
        return false
    else
        Log.error("Nenhum resultado encontrado")
        return false
    end
end

-- Busca refinada
function Memory.refineSearch(value, dataType)
    dataType = dataType or gg.TYPE_DWORD
    gg.refineNumber(value, dataType)
    return gg.getResultsCount()
end

-- Obter resultados
function Memory.getResults(count)
    count = count or gg.getResultsCount()
    return gg.getResults(count)
end

-- Editar resultados
function Memory.editResults(newValue, count)
    count = count or gg.getResultsCount()
    local results = gg.getResults(count)
    
    for i, v in ipairs(results) do
        results[i].value = newValue
    end
    gg.setValues(results)
    
    return #results
end

-- Busca por offset
function Memory.searchWithOffset(baseValue, offsets, dataType)
    dataType = dataType or gg.TYPE_DWORD
    
    -- Buscar valor base
    Memory.search(baseValue, dataType)
    local baseResults = Memory.getResults(100)
    
    if #baseResults == 0 then
        return nil
    end
    
    local validResults = {}
    
    for _, baseResult in ipairs(baseResults) do
        local baseAddr = baseResult.address
        local valid = true
        local values = {}
        
        for _, offset in ipairs(offsets) do
            local targetAddr = baseAddr + offset.offset
            local targetValue = gg.getValues({{address = targetAddr, flags = dataType}})
            
            if targetValue[1].value ~= offset.expected then
                valid = false
                break
            end
            
            table.insert(values, {
                address = targetAddr,
                value = targetValue[1].value,
                offset = offset.offset
            })
        end
        
        if valid then
            table.insert(validResults, {
                baseAddress = baseAddr,
                values = values
            })
        end
    end
    
    return validResults
end

-- Editar por offset
function Memory.editByOffset(baseAddress, offset, newValue, dataType)
    dataType = dataType or gg.TYPE_DWORD
    local targetAddr = baseAddress + offset
    
    gg.setValues({{
        address = targetAddr,
        flags = dataType,
        value = newValue
    }})
end

-- Congelar valores
function Memory.freeze(values)
    for i, v in ipairs(values) do
        values[i].freeze = true
    end
    gg.addListItems(values)
end

-- Descongelar tudo
function Memory.unfreezeAll()
    local list = gg.getListItems()
    if #list > 0 then
        for i, v in ipairs(list) do
            list[i].freeze = false
        end
        gg.setValues(list)
        gg.clearList()
    end
end

-- Limpar tudo
function Memory.clear()
    gg.clearResults()
end

-- ========== MÓDULO DE HACKS ==========
local Hacks = {}

-- Hack de recursos (genérico)
function Hacks.resources()
    local menu = Utils.choice({
        "💰 Dinheiro/Gold",
        "💎 Gemas/Diamonds",
        "⚡ Energia",
        "🎫 Tickets",
        "📦 Outros recursos"
    }, "Tipo de Recurso")
    
    if not menu then return end
    
    local resourceNames = {"Dinheiro", "Gemas", "Energia", "Tickets", "Recurso"}
    local resourceName = resourceNames[menu]
    
    local input = Utils.input(
        {resourceName .. " atual:", "Novo valor:"},
        {"0", "999999"},
        {"number", "number"}
    )
    
    if input then
        local oldVal = tonumber(input[1])
        local newVal = tonumber(input[2])
        
        -- Tentar como DWORD
        if Memory.searchAndEdit(oldVal, newVal, gg.TYPE_DWORD) then
            Utils.toast(resourceName .. " alterado!")
        else
            -- Tentar como FLOAT
            if Memory.searchAndEdit(oldVal, newVal, gg.TYPE_FLOAT) then
                Utils.toast(resourceName .. " alterado (Float)!")
            else
                Utils.toast("Falha ao alterar " .. resourceName)
            end
        end
    end
end

-- Hack de stats
function Hacks.stats()
    local menu = Utils.choice({
        "❤️ Vida/HP",
        "🔵 Mana/MP",
        "⚔️ Ataque",
        "🛡️ Defesa",
        "⚡ Velocidade",
        "🎯 Critical"
    }, "Tipo de Stat")
    
    if not menu then return end
    
    local statNames = {"Vida", "Mana", "Ataque", "Defesa", "Velocidade", "Critical"}
    local statName = statNames[menu]
    
    local input = Utils.input(
        {statName .. " atual:", "Novo valor:"},
        {"100", "9999"},
        {"number", "number"}
    )
    
    if input then
        local oldVal = tonumber(input[1])
        local newVal = tonumber(input[2])
        
        -- Stats geralmente são FLOAT
        if not Memory.searchAndEdit(oldVal, newVal, gg.TYPE_FLOAT) then
            Memory.searchAndEdit(oldVal, newVal, gg.TYPE_DWORD)
        end
        
        Utils.toast(statName .. " modificado!")
    end
end

-- Hack de velocidade do jogo
function Hacks.gameSpeed()
    local speeds = {0.5, 1.0, 1.5, 2.0, 3.0, 5.0}
    local menu = Utils.choice({
        "🐢 0.5x (Lento)",
        "⏺️ 1x (Normal)",
        "🏃 1.5x",
        "🚀 2x",
        "⚡ 3x",
        "💨 5x"
    }, "Velocidade do Jogo")
    
    if menu then
        gg.setSpeed(speeds[menu])
        Utils.toast("Velocidade: " .. speeds[menu] .. "x")
    end
end

-- Hack de tempo
function Hacks.time()
    local menu = Utils.choice({
        "⏸️ Pausar tempo",
        "▶️ Retomar tempo",
        "⏩ Avançar tempo",
        "🔄 Reset cooldowns"
    }, "Controle de Tempo")
    
    if menu == 1 then
        -- Pausar busca por deltaTime
        Memory.setRanges("all")
        gg.searchNumber("0.016~0.017", gg.TYPE_FLOAT)
        Memory.editResults(0)
        Utils.toast("Tempo pausado!")
        
    elseif menu == 2 then
        Memory.setRanges("all")
        gg.searchNumber("0", gg.TYPE_FLOAT)
        Memory.refineSearch("0", gg.TYPE_FLOAT)
        Memory.editResults(0.016667)
        Utils.toast("Tempo retomado!")
        
    elseif menu == 3 then
        local input = Utils.input({"Multiplicador de tempo:"}, {"2"}, {"number"})
        if input then
            local mult = tonumber(input[1])
            gg.setSpeed(mult)
            Utils.toast("Tempo x" .. mult)
        end
        
    elseif menu == 4 then
        -- Buscar cooldowns comuns
        Memory.searchAndEdit(30, 0, gg.TYPE_FLOAT)
        Memory.searchAndEdit(60, 0, gg.TYPE_FLOAT)
        Memory.searchAndEdit(300, 0, gg.TYPE_FLOAT)
        Utils.toast("Cooldowns resetados!")
    end
end

-- Busca avançada
function Hacks.advancedSearch()
    local menu = Utils.choice({
        "🔍 Busca simples",
        "🔎 Busca refinada",
        "📊 Busca por grupo",
        "🎯 Busca por faixa",
        "📍 Busca por offset"
    }, "Tipo de Busca")
    
    if menu == 1 then
        local input = Utils.input(
            {"Valor:", "Tipo (1=DWORD, 2=FLOAT, 3=DOUBLE):"},
            {"0", "1"},
            {"text", "number"}
        )
        
        if input then
            local types = {gg.TYPE_DWORD, gg.TYPE_FLOAT, gg.TYPE_DOUBLE}
            local count = Memory.search(input[1], types[tonumber(input[2])])
            Utils.toast("Encontrados: " .. count .. " resultados")
        end
        
    elseif menu == 2 then
        local input = Utils.input({"Novo valor:"},{"0"},{"text"})
        if input then
            local count = Memory.refineSearch(input[1])
            Utils.toast("Refinado para: " .. count .. " resultados")
        end
        
    elseif menu == 3 then
        local input = Utils.input({"Valores (separados por ';'):"},{"100;200;300"},{"text"})
        if input then
            gg.clearResults()
            Memory.setRanges("all")
            gg.searchNumber(input[1], gg.TYPE_DWORD)
            Utils.toast("Grupos encontrados: " .. gg.getResultsCount())
        end
        
    elseif menu == 4 then
        local input = Utils.input(
            {"Valor mínimo:", "Valor máximo:"},
            {"0", "1000"},
            {"number", "number"}
        )
        if input then
            local range = input[1] .. "~" .. input[2]
            gg.clearResults()
            Memory.setRanges("all")
            gg.searchNumber(range, gg.TYPE_DWORD)
            Utils.toast("Encontrados: " .. gg.getResultsCount())
        end
        
    elseif menu == 5 then
        local input = Utils.input(
            {"Valor base:", "Offset (hex):"},
            {"100", "0x10"},
            {"number", "text"}
        )
        if input then
            local base = tonumber(input[1])
            local offset = tonumber(input[2])
            
            Memory.search(base, gg.TYPE_DWORD)
            local results = Memory.getResults(100)
            
            Utils.toast("Base: " .. #results .. " resultados. Verificando offsets...")
        end
    end
end

-- Editar resultados
function Hacks.editResults()
    local count = gg.getResultsCount()
    
    if count == 0 then
        Utils.toast("Nenhum resultado para editar!")
        return
    end
    
    local menu = Utils.choice({
        "✏️ Editar todos (" .. count .. ")",
        "❄️ Congelar todos",
        "🗑️ Limpar resultados"
    }, "Editar Resultados")
    
    if menu == 1 then
        local input = Utils.input({"Novo valor:"},{"999999"},{"text"})
        if input then
            Memory.editResults(input[1])
            Utils.toast("Editados " .. count .. " valores!")
        end
        
    elseif menu == 2 then
        local results = Memory.getResults()
        Memory.freeze(results)
        Utils.toast("Congelados " .. #results .. " valores!")
        
    elseif menu == 3 then
        Memory.clear()
        Utils.toast("Resultados limpos!")
    end
end

-- ========== MENU DE CONFIGURAÇÕES ==========
function menuConfig()
    local menu = Utils.choice({
        "🔄 Auto Refresh: " .. (Config.autoRefresh and "ON" or "OFF"),
        "🛡️ Safe Mode: " .. (Config.safeMode and "ON" or "OFF"),
        "📝 Log: " .. (Config.logEnabled and "ON" or "OFF"),
        "🗑️ Limpar Lista",
        "↩️ Reset Speed",
        "⬅️ Voltar"
    }, "Configurações")
    
    if menu == 1 then
        Config.autoRefresh = not Config.autoRefresh
        Utils.toast("Auto Refresh: " .. (Config.autoRefresh and "ON" or "OFF"))
        menuConfig()
        
    elseif menu == 2 then
        Config.safeMode = not Config.safeMode
        Utils.toast("Safe Mode: " .. (Config.safeMode and "ON" or "OFF"))
        menuConfig()
        
    elseif menu == 3 then
        Config.logEnabled = not Config.logEnabled
        Utils.toast("Log: " .. (Config.logEnabled and "ON" or "OFF"))
        menuConfig()
        
    elseif menu == 4 then
        Memory.unfreezeAll()
        Utils.toast("Lista limpa!")
        
    elseif menu == 5 then
        gg.setSpeed(1)
        Utils.toast("Velocidade resetada!")
    end
end

-- ========== MENU PRINCIPAL ==========
function mainMenu()
    local menu = Utils.choice({
        "💰 Recursos",
        "📊 Stats",
        "⚡ Velocidade do Jogo",
        "⏱️ Controle de Tempo",
        "🔍 Busca Avançada",
        "✏️ Editar Resultados",
        "⚙️ Configurações",
        "ℹ️ Sobre",
        "❌ Sair"
    }, SCRIPT_NAME .. " v" .. SCRIPT_VERSION)
    
    if menu == 1 then
        Hacks.resources()
    elseif menu == 2 then
        Hacks.stats()
    elseif menu == 3 then
        Hacks.gameSpeed()
    elseif menu == 4 then
        Hacks.time()
    elseif menu == 5 then
        Hacks.advancedSearch()
    elseif menu == 6 then
        Hacks.editResults()
    elseif menu == 7 then
        menuConfig()
    elseif menu == 8 then
        Utils.alert(
            "📱 " .. SCRIPT_NAME .. "\\n" ..
            "📌 Versão: " .. SCRIPT_VERSION .. "\\n" ..
            "👤 Autor: " .. SCRIPT_AUTHOR .. "\\n\\n" ..
            "⚠️ Use com responsabilidade!\\n" ..
            "Apenas para fins educacionais."
        )
    elseif menu == 9 then
        if Utils.confirm("Deseja realmente sair?") then
            gg.setSpeed(1)
            Memory.unfreezeAll()
            Utils.toast("Até logo!")
            os.exit()
        end
    end
end

-- ========== LOOP PRINCIPAL ==========
Utils.toast("Script iniciado!")
Log.add("Script " .. SCRIPT_NAME .. " v" .. SCRIPT_VERSION .. " carregado")

while true do
    if gg.isVisible() then
        gg.setVisible(false)
        mainMenu()
    end
    
    if Config.autoRefresh then
        -- Código de auto-refresh aqui se necessário
    end
    
    Utils.sleep(100)
end
''',
            "lang": "lua",
            "ext": ".lua"
        }
    },
    
    "🤖 Discord Bot": {
        "Bot Completo com Slash Commands": {
            "code": '''import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
from datetime import datetime, timedelta
import random

# ========== CONFIGURAÇÃO ==========
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========== SISTEMA DE DADOS ==========
class Database:
    def __init__(self):
        self.data = {"users": {}, "guilds": {}}
        self.load()
    
    def load(self):
        try:
            with open("database.json", "r") as f:
                self.data = json.load(f)
        except:
            pass
    
    def save(self):
        with open("database.json", "w") as f:
            json.dump(self.data, f, indent=4)
    
    def get_user(self, user_id: int):
        uid = str(user_id)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "balance": 0,
                "xp": 0,
                "level": 1,
                "daily_last": None,
                "inventory": []
            }
        return self.data["users"][uid]
    
    def update_user(self, user_id: int, key: str, value):
        self.get_user(user_id)[key] = value
        self.save()

db = Database()

# ========== EVENTOS ==========
@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} está online!")
    print(f"📊 Servidores: {len(bot.guilds)}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servidores"
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
        embed.add_field(name="📅 Conta criada", value=member.created_at.strftime("%d/%m/%Y"))
        embed.add_field(name="👥 Membro #", value=str(member.guild.member_count))
        await channel.send(embed=embed)

# ========== COMANDOS BÁSICOS ==========
@bot.tree.command(name="ping", description="Mostra a latência do bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(title="🏓 Pong!", color=discord.Color.blue())
    embed.add_field(name="Latência", value=f"{latency}ms")
    embed.add_field(name="Status", value="✅ Online" if latency < 200 else "⚠️ Lento")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="Mostra o avatar de um usuário")
async def avatar(interaction: discord.Interaction, membro: discord.Member = None):
    membro = membro or interaction.user
    
    embed = discord.Embed(title=f"Avatar de {membro.name}", color=membro.color)
    embed.set_image(url=membro.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Informações do servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.gold())
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="👑 Dono", value=guild.owner.mention if guild.owner else "N/A")
    embed.add_field(name="👥 Membros", value=guild.member_count)
    embed.add_field(name="💬 Canais", value=len(guild.channels))
    embed.add_field(name="🎭 Cargos", value=len(guild.roles))
    embed.add_field(name="📅 Criado em", value=guild.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="🔒 Verificação", value=str(guild.verification_level))
    
    await interaction.response.send_message(embed=embed)

# ========== SISTEMA DE ECONOMIA ==========
@bot.tree.
