import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
from PIL import Image
import re

# Configuração da página
st.set_page_config(
    page_title="ScriptMaster AI 👑",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CÓDIGO MASTER
MASTER_CODE = "GuizinhsDono"

# Templates de scripts
SCRIPT_TEMPLATES = {
    "🐍 Python - Web Scraper": """import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    '''Extrai dados de um website'''
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Seu código aqui
    
    return soup

if __name__ == "__main__":
    url = "https://example.com"
    data = scrape_website(url)
    print(data)
""",
    
    "🐍 Python - API REST": """from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    '''Endpoint para obter dados'''
    return jsonify({"message": "Success", "data": []})

@app.route('/api/data', methods=['POST'])
def post_data():
    '''Endpoint para enviar dados'''
    data = request.json
    return jsonify({"message": "Created", "data": data}), 201

if __name__ == '__main__':
    app.run(debug=True)
""",

    "🐍 Python - Automação": """import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

def automate_task():
    '''Automação de tarefas com Selenium'''
    driver = webdriver.Chrome()
    
    try:
        driver.get("https://example.com")
        time.sleep(2)
        
        # Seu código de automação aqui
        
    finally:
        driver.quit()

if __name__ == "__main__":
    automate_task()
""",

    "💻 JavaScript - Node.js API": """const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

app.get('/api/data', (req, res) => {
  res.json({ message: 'Success', data: [] });
});

app.post('/api/data', (req, res) => {
  const data = req.body;
  res.status(201).json({ message: 'Created', data });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
""",

    "💾 SQL - Database Schema": """-- Criação de banco de dados completo

CREATE DATABASE IF NOT EXISTS meu_sistema;
USE meu_sistema;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    estoque INT DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email ON usuarios(email);
CREATE INDEX idx_nome_produto ON produtos(nome);
""",

    "🐚 Bash - Deploy Automático": """#!/bin/bash

# Script de deploy automático

echo "🚀 Iniciando deploy..."

# Pull do repositório
git pull origin main

# Instalar dependências
npm install

# Build da aplicação
npm run build

# Restart do serviço
pm2 restart app

echo "✅ Deploy concluído com sucesso!"
""",

    "🤖 Python - Bot Discord": """import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} conectado!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong! 🏓')

@bot.command()
async def ola(ctx):
    await ctx.send(f'Olá, {ctx.author.mention}! 👋')

bot.run('SEU_TOKEN_AQUI')
""",

    "🌐 Python - WebSocket Server": """import asyncio
import websockets

connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Broadcast para todos os clientes
            websockets.broadcast(connected_clients, message)
    finally:
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
"""
}

# Função para detectar linguagem do código
def detect_language(code):
    if code.strip().startswith('#!/bin/bash') or 'bash' in code.lower()[:50]:
        return 'bash'
    elif 'import ' in code or 'def ' in code or 'class ' in code:
        return 'python'
    elif 'const ' in code or 'let ' in code or 'function' in code or 'require(' in code:
        return 'javascript'
    elif 'CREATE TABLE' in code.upper() or 'SELECT ' in code.upper():
        return 'sql'
    elif '<?php' in code:
        return 'php'
    else:
        return 'python'

# Função hash
def hash_code(code):
    return hashlib.sha256(code.encode()).hexdigest()

# Inicializar session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_master" not in st.session_state:
    st.session_state.is_master = False
if "vip_until" not in st.session_state:
    st.session_state.vip_until = None
if "username" not in st.session_state:
    st.session_state.username = None
if "msgs" not in st.session_state:
    st.session_state.msgs = []
if "saved_scripts" not in st.session_state:
    st.session_state.saved_scripts = []
if "current_script" not in st.session_state:
    st.session_state.current_script = ""
if "created_codes" not in st.session_state:
    st.session_state.created_codes = {}

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .script-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .script-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .master-badge {
        background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 700;
        margin: 0.5rem 0;
        animation: pulse 2s infinite;
    }
    
    .vip-badge {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 700;
    }
    
    .code-block {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 1.5rem;
        border-radius: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .template-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .template-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    .script-saved {
        background: #2d2d2d;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Configurar API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def is_vip_active():
    if st.session_state.is_master:
        return True
    if st.session_state.vip_until:
        return datetime.now() < st.session_state.vip_until
    return False

@st.cache_resource
def get_models():
    try:
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return models
    except:
        return []

# ====== TELA DE LOGIN ======
if not st.session_state.authenticated:
    st.markdown("""
    <div class="script-header">
        <h1>⚡ ScriptMaster AI</h1>
        <p style="color: white; font-size: 1.2rem;">Gerador Profissional de Scripts com IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔐 Login")
        username = st.text_input("👤 Nome", placeholder="Digite seu nome")
        access_code = st.text_input("🎫 Código de acesso", type="password", placeholder="Código VIP ou MASTER")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Entrar VIP/Master", use_container_width=True):
                if not username or not access_code:
                    st.error("❌ Preencha todos os campos!")
                elif access_code == MASTER_CODE:
                    st.session_state.authenticated = True
                    st.session_state.is_master = True
                    st.session_state.username = username
                    st.success("✅ MASTER ativado!")
                    st.balloons()
                    st.rerun()
                elif access_code in st.session_state.created_codes:
                    code_info = st.session_state.created_codes[access_code]
                    if not code_info.get("used", False):
                        st.session_state.created_codes[access_code]["used"] = True
                        st.session_state.created_codes[access_code]["used_by"] = username
                        days = code_info["days"]
                        st.session_state.vip_until = datetime.now() + timedelta(days=days if days != 999 else 3650)
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success(f"✅ VIP ativado por {days} dias!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Código já usado!")
                else:
                    st.error("❌ Código inválido!")
        
        with col_btn2:
            if st.button("🆓 Modo Gratuito", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.username = username if username else "Dev"
                st.info("ℹ️ Modo gratuito ativado")
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 Recursos")
        st.markdown("""
        **🆓 Gratuito:**
        - ✅ Templates básicos
        - ✅ Geração de scripts simples
        - ❌ Salvar scripts limitado
        
        **👑 VIP:**
        - ✅ TODOS os templates
        - ✅ IA avançada ilimitada
        - ✅ Salvar scripts ilimitados
        - ✅ Download de scripts
        - ✅ Documentação automática
        
        **🔥 MASTER:**
        - ✅ Tudo do VIP
        - ✅ Criar códigos VIP
        - ✅ Painel de administração
        """)
    
    st.stop()

# ====== SIDEBAR ======
with st.sidebar:
    if st.session_state.is_master:
        st.markdown('<div class="master-badge">🔥 MASTER</div>', unsafe_allow_html=True)
    elif is_vip_active():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<div class="vip-badge">👑 VIP - {dias}d</div>', unsafe_allow_html=True)
    
    st.markdown(f"**👤 {st.session_state.username}**")
    
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    st.divider()
    
    # PAINEL MASTER
    if st.session_state.is_master:
        st.markdown("### 🎫 Criar Códigos VIP")
        
        with st.expander("➕ Novo Código"):
            novo_codigo = st.text_input("📝 Código", key="new_code")
            tipo = st.selectbox("⏱️ Duração", ["1 dia", "7 dias", "30 dias", "Ilimitado"])
            
            if st.button("✨ Gerar", use_container_width=True):
                if novo_codigo and novo_codigo not in st.session_state.created_codes:
                    days_map = {"1 dia": 1, "7 dias": 7, "30 dias": 30, "Ilimitado": 999}
                    st.session_state.created_codes[novo_codigo] = {
                        "days": days_map[tipo],
                        "created_at": datetime.now().isoformat(),
                        "used": False
                    }
                    st.success(f"✅ Código '{novo_codigo}' criado!")
                    st.code(novo_codigo)
        
        if st.session_state.created_codes:
            st.markdown("### 📋 Códigos Ativos")
            for code, info in list(st.session_state.created_codes.items())[:5]:
                status = "✅" if info.get("used") else "🎫"
                st.text(f"{status} {code}")
        
        st.divider()
    
    # Templates
    st.markdown("### 📚 Templates de Scripts")
    
    for template_name in SCRIPT_TEMPLATES.keys():
        if st.button(template_name, use_container_width=True, key=f"temp_{template_name}"):
            st.session_state.current_script = SCRIPT_TEMPLATES[template_name]
            st.rerun()
    
    st.divider()
    
    # Scripts salvos
    if is_vip_active() and st.session_state.saved_scripts:
        st.markdown("### 💾 Scripts Salvos")
        for idx, script_data in enumerate(st.session_state.saved_scripts[-5:]):
            if st.button(f"📄 {script_data['name']}", key=f"saved_{idx}", use_container_width=True):
                st.session_state.current_script = script_data['code']
                st.rerun()
    
    st.divider()
    
    # Estatísticas
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(st.session_state.saved_scripts)}</div>
        <div>Scripts Salvos</div>
    </div>
    """, unsafe_allow_html=True)

# ====== ÁREA PRINCIPAL ======

st.markdown("""
<div class="script-header">
    <h1>⚡ ScriptMaster AI</h1>
    <p style="color: white;">Gerador Profissional de Scripts com Inteligência Artificial</p>
</div>
""", unsafe_allow_html=True)

# Tabs principais
tab1, tab2, tab3 = st.tabs(["🤖 Gerar Script", "💻 Editor", "📚 Biblioteca"])

# TAB 1: Gerar Script
with tab1:
    st.markdown("### 🎯 O que você quer criar?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt_script = st.text_area(
            "Descreva o script que você precisa:",
            placeholder="Ex: Crie um script Python que faz web scraping de notícias e salva em CSV",
            height=150
        )
    
    with col2:
        linguagem = st.selectbox(
            "🔤 Linguagem",
            ["Python", "JavaScript", "Bash", "SQL", "PHP", "PowerShell"]
        )
        
        complexidade = st.select_slider(
            "📊 Complexidade",
            ["Básico", "Intermediário", "Avançado"]
        )
    
    if st.button("⚡ GERAR SCRIPT", use_container_width=True, type="primary"):
        if not prompt_script:
            st.error("❌ Descreva o que você precisa!")
        else:
            with st.spinner("🔮 Gerando script..."):
                try:
                    modelos = get_models()
                    modelo = modelos[0] if modelos else "gemini-pro"
                    
                    model = genai.GenerativeModel(modelo)
                    
                    prompt_completo = f"""
Você é um expert em programação. Crie um script COMPLETO e FUNCIONAL em {linguagem}.

**Requisitos:**
{prompt_script}

**Nível:** {complexidade}

**Instruções:**
1. Gere código COMPLETO e PRONTO para usar
2. Adicione comentários explicativos
3. Inclua tratamento de erros
4. Adicione docstrings/documentação
5. Use boas práticas da linguagem
6. Se necessário, liste as dependências no topo como comentário

Retorne APENAS o código, sem explicações adicionais.
"""
                    
                    response = model.generate_content(prompt_completo)
                    script_gerado = response.text
                    
                    # Limpar markdown
                    script_gerado = re.sub(r'```[\w]*\n', '', script_gerado)
                    script_gerado = script_gerado.replace('```', '')
                    
                    st.session_state.current_script = script_gerado
                    
                    st.success("✅ Script gerado com sucesso!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")

# TAB 2: Editor
with tab2:
    if st.session_state.current_script:
        st.markdown("### 💻 Editor de Código")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            script_name = st.text_input("📝 Nome do arquivo", value="script", key="script_name")
        
        with col2:
            lang = detect_language(st.session_state.current_script)
            extensions = {
                'python': '.py',
                'javascript': '.js',
                'bash': '.sh',
                'sql': '.sql',
                'php': '.php'
            }
            file_ext = st.text_input("📄 Extensão", value=extensions.get(lang, '.txt'))
        
        with col3:
            if is_vip_active():
                if st.button("💾 Salvar Script", use_container_width=True):
                    st.session_state.saved_scripts.append({
                        "name": f"{script_name}{file_ext}",
                        "code": st.session_state.current_script,
                        "language": lang,
                        "created_at": datetime.now().isoformat()
                    })
                    st.success("✅ Script salvo!")
            else:
                st.info("🔒 VIP")
        
        with col4:
            st.download_button(
                "📥 Download",
                data=st.session_state.current_script,
                file_name=f"{script_name}{file_ext}",
                mime="text/plain",
                use_container_width=True
            )
        
        # Editor
        edited_script = st.text_area(
            "Edite seu código:",
            value=st.session_state.current_script,
            height=400,
            key="editor"
        )
        
        st.session_state.current_script = edited_script
        
        # Preview com syntax highlighting
        st.markdown("### 👁️ Preview")
        st.code(st.session_state.current_script, language=lang)
        
    else:
        st.info("👈 Selecione um template ou gere um script para começar!")

# TAB 3: Biblioteca
with tab3:
    if is_vip_active():
        st.markdown("### 📚 Biblioteca de Scripts Salvos")
        
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
                            key=f"download_{idx}"
                        )
                    
                    with col2:
                        if st.button("📋 Copiar para Editor", key=f"copy_{idx}"):
                            st.session_state.current_script = script['code']
                            st.success("✅ Copiado!")
                    
                    with col3:
                        if st.button("🗑️ Deletar", key=f"del_{idx}"):
                            real_idx = len(st.session_state.saved_scripts) - 1 - idx
                            st.session_state.saved_scripts.pop(real_idx)
                            st.rerun()
        else:
            st.info("📭 Nenhum script salvo ainda. Comece gerando scripts!")
    else:
        st.warning("🔒 Biblioteca disponível apenas para usuários VIP")
        st.markdown("### 🎁 Faça upgrade para VIP e tenha:")
        st.markdown("""
        - ✅ Salvar scripts ilimitados
        - ✅ Organização automática
        - ✅ Busca inteligente
        - ✅ Versionamento de código
        - ✅ Compartilhamento de scripts
        """)

# Rodapé
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📝 Scripts", len(st.session_state.saved_scripts))

with col2:
    st.metric("⚡ Status", "VIP" if is_vip_active() else "FREE")

with col3:
    if st.session_state.current_script:
        lines = len(st.session_state.current_script.split('\n'))
        st.metric("📏 Linhas", lines)
    else:
        st.metric("📏 Linhas", 0)

with col4:
    lang = detect_language(st.session_state.current_script) if st.session_state.current_script else "N/A"
    st.metric("🔤 Linguagem", lang.upper())
