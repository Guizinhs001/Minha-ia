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
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .code-output {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 1.5rem;
        border-radius: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        border-left: 4px solid #667eea;
        max-height: 600px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_master" not in st.session_state:
    st.session_state.is_master = False
if "vip_until" not in st.session_state:
    st.session_state.vip_until = None
if "username" not in st.session_state:
    st.session_state.username = None
if "current_script" not in st.session_state:
    st.session_state.current_script = ""
if "saved_scripts" not in st.session_state:
    st.session_state.saved_scripts = []
if "created_codes" not in st.session_state:
    st.session_state.created_codes = {}

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
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Login")
        username = st.text_input("👤 Nome", placeholder="Seu nome")
        access_code = st.text_input("🎫 Código de acesso", type="password", placeholder="MASTER ou código VIP")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Entrar VIP", use_container_width=True):
                if access_code == MASTER_CODE:
                    st.session_state.authenticated = True
                    st.session_state.is_master = True
                    st.session_state.username = username or "Master"
                    st.success("✅ MASTER ativado!")
                    st.balloons()
                    st.rerun()
                elif access_code in st.session_state.created_codes:
                    code_info = st.session_state.created_codes[access_code]
                    if not code_info.get("used"):
                        st.session_state.created_codes[access_code]["used"] = True
                        days = code_info["days"]
                        st.session_state.vip_until = datetime.now() + timedelta(days=days if days != 999 else 3650)
                        st.session_state.authenticated = True
                        st.session_state.username = username or "Dev"
                        st.success("✅ VIP ativado!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Código já usado!")
                else:
                    st.error("❌ Código inválido!")
        
        with col_btn2:
            if st.button("🆓 Modo Grátis", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.username = username or "Visitante"
                st.info("ℹ️ Modo gratuito ativado")
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 O que você pode criar:")
        st.markdown("""
        **🎮 Jogos:**
        - Godot 4.6 (GDScript/C#)
        - Unity (C#)
        - HTML5 (Phaser, Canvas)
        - Mobile (React Native)
        
        **💻 Scripts:**
        - Python (Bot, Web Scraping, API)
        - JavaScript (Discord, Node.js)
        - SQL, Bash, PowerShell
        
        **👑 VIP tem acesso ilimitado!**
        """)
    
    st.stop()

# ====== SIDEBAR ======
with st.sidebar:
    # Badge de status
    if st.session_state.is_master:
        st.markdown('<div class="master-badge">🔥 MASTER</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 🎫 Criar Códigos VIP")
        
        with st.expander("➕ Novo Código"):
            novo_codigo = st.text_input("📝 Nome do código", key="new_code", placeholder="Ex: VIP2024")
            tipo = st.selectbox("⏱️ Duração", ["1 dia", "7 dias", "30 dias", "Ilimitado"])
            
            if st.button("✨ Gerar Código", use_container_width=True):
                if novo_codigo:
                    if novo_codigo not in st.session_state.created_codes:
                        days_map = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                        st.session_state.created_codes[novo_codigo] = {
                            "days": days_map[tipo],
                            "created_at": datetime.now().isoformat(),
                            "used": False
                        }
                        st.success(f"✅ Código '{novo_codigo}' criado!")
                        st.code(novo_codigo, language=None)
                    else:
                        st.error("❌ Código já existe!")
                else:
                    st.error("❌ Digite um nome para o código!")
        
        if st.session_state.created_codes:
            st.markdown("### 📋 Códigos Ativos")
            for code, info in list(st.session_state.created_codes.items()):
                status = "✅ USADO" if info.get("used") else "🎫 ATIVO"
                days_text = "♾️" if info["days"] == 999 else f"{info['days']}d"
                st.text(f"{status[:2]} {code} ({days_text})")
        
        st.divider()
    
    elif is_vip_active():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<div class="vip-badge">👑 VIP - {dias} dias</div>', unsafe_allow_html=True)
        st.divider()
    
    st.markdown(f"**👤 {st.session_state.username}**")
    
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.is_master = False
        st.rerun()
    
    st.divider()
    
    # Templates rápidos
    st.markdown("### 📚 Templates Rápidos")
    
    templates = {
        "🎮 Godot - Jogo Mobile": "godot_mobile",
        "🌐 HTML5 - Jogo Canvas": "html5_game",
        "🐍 Python - Web Scraper": "python_scraper",
        "🤖 Discord Bot": "discord_bot",
        "📱 React Native Game": "react_native"
    }
    
    for name, key in templates.items():
        if st.button(name, use_container_width=True, key=f"temp_{key}"):
            # Definir template escolhido
            st.session_state.selected_template = key
            st.rerun()
    
    st.divider()
    
    # Scripts salvos
    if st.session_state.saved_scripts:
        st.markdown("### 💾 Scripts Salvos")
        for idx, script in enumerate(st.session_state.saved_scripts[-5:]):
            if st.button(f"📄 {script['name']}", key=f"saved_{idx}", use_container_width=True):
                st.session_state.current_script = script['code']
                st.rerun()
    
    st.divider()
    st.caption(f"📊 {len(st.session_state.saved_scripts)} scripts salvos")

# ====== ÁREA PRINCIPAL ======

st.markdown("""
<div class="header-premium">
    <h1>🎮 ScriptMaster AI</h1>
    <p style="color: white;">Gerador Profissional de Scripts e Jogos</p>
</div>
""", unsafe_allow_html=True)

# Tabs principais
tab1, tab2, tab3 = st.tabs(["🤖 Gerar Script", "💻 Editor", "📚 Biblioteca"])

# ====== TAB 1: GERAR SCRIPT ======
with tab1:
    st.markdown("### 🎯 Descreva o que você precisa")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_prompt = st.text_area(
            "📝 Descrição completa:",
            placeholder="Ex: Crie um jogo endless runner em Godot 4.6 para mobile com controles touch, sistema de score e obstáculos aleatórios",
            height=150,
            key="user_input"
        )
    
    with col2:
        tipo_codigo = st.selectbox(
            "🔤 Tipo de código",
            [
                "Godot 4.6 (GDScript)",
                "Godot 4.6 (C#)",
                "Unity (C#)",
                "HTML5 - Phaser 3",
                "HTML5 - Canvas Puro",
                "React Native",
                "Python Script",
                "JavaScript/Node.js",
                "Discord Bot",
                "SQL Database",
                "Bash Script"
            ]
        )
        
        complexidade = st.select_slider(
            "📊 Nível",
            ["Básico", "Intermediário", "Avançado", "Expert"]
        )
    
    # BOTÃO GERAR
    if st.button("⚡ GERAR CÓDIGO AGORA", use_container_width=True, type="primary"):
        if not user_prompt:
            st.error("❌ Escreva o que você precisa!")
        else:
            with st.spinner("🔮 Gerando seu código... Aguarde..."):
                try:
                    # Pegar modelo
                    modelos = get_models()
                    if not modelos:
                        st.error("❌ Nenhum modelo disponível!")
                        st.stop()
                    
                    modelo = modelos[0]
                    model = genai.GenerativeModel(modelo)
                    
                    # Criar prompt especializado
                    prompt_sistema = f"""
Você é um programador EXPERT em {tipo_codigo}.

TAREFA: Criar código COMPLETO e FUNCIONAL baseado nesta descrição:
{user_prompt}

NÍVEL DE COMPLEXIDADE: {complexidade}

REGRAS OBRIGATÓRIAS:
1. Código COMPLETO, pronto para usar
2. Adicione comentários explicativos
3. Use boas práticas da linguagem
4. Inclua tratamento de erros
5. Se for jogo, adicione controles funcionais
6. Se for mobile, otimize para touch
7. NÃO adicione explicações fora do código
8. Retorne APENAS o código puro

FORMATO DE SAÍDA:
Retorne o código diretamente, SEM usar ``` ou markdown.
Comece direto com o código.
"""
                    
                    # Gerar código
                    response = model.generate_content(prompt_sistema)
                    codigo_gerado = response.text
                    
                    # Limpar qualquer markdown que possa ter vindo
                    codigo_gerado = re.sub(r'```[\w]*\n?', '', codigo_gerado)
                    codigo_gerado = codigo_gerado.replace('```', '')
                    codigo_gerado = codigo_gerado.strip()
                    
                    # Salvar no session state
                    st.session_state.current_script = codigo_gerado
                    
                    # Mostrar sucesso
                    st.success("✅ Código gerado com sucesso!")
                    st.balloons()
                    
                    # Mostrar o código IMEDIATAMENTE
                    st.markdown("### 📄 Código Gerado:")
                    
                    # Detectar linguagem
                    if "Godot" in tipo_codigo or "GDScript" in tipo_codigo:
                        lang = "gdscript"
                    elif "Unity" in tipo_codigo or "C#" in tipo_codigo:
                        lang = "csharp"
                    elif "HTML" in tipo_codigo:
                        lang = "html"
                    elif "Python" in tipo_codigo:
                        lang = "python"
                    elif "JavaScript" in tipo_codigo or "Discord" in tipo_codigo:
                        lang = "javascript"
                    elif "SQL" in tipo_codigo:
                        lang = "sql"
                    elif "Bash" in tipo_codigo:
                        lang = "bash"
                    else:
                        lang = "python"
                    
                    # Mostrar código com syntax highlighting
                    st.code(codigo_gerado, language=lang)
                    
                    # Botões de ação
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.download_button(
                            "📥 Download Código",
                            data=codigo_gerado,
                            file_name=f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{lang}",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col_b:
                        if st.button("💾 Salvar na Biblioteca", use_container_width=True):
                            st.session_state.saved_scripts.append({
                                "name": f"Script_{len(st.session_state.saved_scripts)+1}",
                                "code": codigo_gerado,
                                "language": lang,
                                "created_at": datetime.now().isoformat()
                            })
                            st.success("✅ Salvo na biblioteca!")
                            st.rerun()
                    
                    with col_c:
                        if st.button("✏️ Editar no Editor", use_container_width=True):
                            st.info("👉 Vá para a aba 'Editor' para editar!")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar código: {str(e)}")
                    st.info("💡 Tente descrever de forma mais simples ou escolha outro tipo de código")

# ====== TAB 2: EDITOR ======
with tab2:
    st.markdown("### 💻 Editor de Código")
    
    if st.session_state.current_script:
        # Informações do arquivo
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            nome_arquivo = st.text_input("📝 Nome do arquivo", value="meu_script", key="filename")
        
        with col2:
            extensao = st.text_input("📄 Extensão", value=".py", key="ext")
        
        with col3:
            if st.button("💾 Salvar", use_container_width=True):
                st.session_state.saved_scripts.append({
                    "name": f"{nome_arquivo}{extensao}",
                    "code": st.session_state.current_script,
                    "language": "python",
                    "created_at": datetime.now().isoformat()
                })
                st.success("✅ Salvo!")
                st.rerun()
        
        with col4:
            st.download_button(
                "📥 Download",
                data=st.session_state.current_script,
                file_name=f"{nome_arquivo}{extensao}",
                use_container_width=True
            )
        
        # Editor de texto
        codigo_editado = st.text_area(
            "Edite seu código:",
            value=st.session_state.current_script,
            height=500,
            key="code_editor"
        )
        
        # Atualizar o código se foi editado
        if codigo_editado != st.session_state.current_script:
            st.session_state.current_script = codigo_editado
        
        # Preview
        st.markdown("### 👁️ Preview do Código")
        st.code(st.session_state.current_script, language="python")
        
    else:
        st.info("👈 Gere um código primeiro ou carregue um script salvo!")
        
        # Mostrar exemplo
        st.markdown("### 💡 Exemplo de uso:")
        st.code("""# Exemplo: Bot do Discord
import discord

client = discord.Client()

@client.event
async def on_ready():
    print(f'Bot {client.user} online!')

client.run('TOKEN')
""", language="python")

# ====== TAB 3: BIBLIOTECA ======
with tab3:
    st.markdown("### 📚 Biblioteca de Scripts")
    
    if st.session_state.saved_scripts:
        for idx, script in enumerate(reversed(st.session_state.saved_scripts)):
            with st.expander(f"📄 {script['name']} - {datetime.fromisoformat(script['created_at']).strftime('%d/%m/%Y %H:%M')}"):
                st.code(script['code'], language=script.get('language', 'python'))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        "📥 Download",
                        data=script['code'],
                        file_name=script['name'],
                        key=f"download_{idx}",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("📋 Copiar para Editor", key=f"copy_{idx}", use_container_width=True):
                        st.session_state.current_script = script['code']
                        st.success("✅ Copiado para o editor!")
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Deletar", key=f"delete_{idx}", use_container_width=True):
                        real_idx = len(st.session_state.saved_scripts) - 1 - idx
                        st.session_state.saved_scripts.pop(real_idx)
                        st.success("✅ Deletado!")
                        st.rerun()
    else:
        st.info("📭 Nenhum script salvo ainda. Gere e salve scripts para vê-los aqui!")
        
        st.markdown("### 💡 Dica:")
        st.markdown("""
        1. Vá para **Gerar Script**
        2. Descreva o que você quer
        3. Clique em **Salvar na Biblioteca**
        4. Seus scripts aparecerão aqui!
        """)

# Rodapé
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Scripts Salvos", len(st.session_state.saved_scripts))

with col2:
    status = "👑 VIP" if is_vip_active() else "🆓 FREE"
    st.metric("⚡ Status", status)

with col3:
    if st.session_state.current_script:
        linhas = len(st.session_state.current_script.split('\n'))
        st.metric("📏 Linhas", linhas)
    else:
        st.metric("📏 Linhas", 0)

with col4:
    st.metric("🤖 IA", "Gemini")
