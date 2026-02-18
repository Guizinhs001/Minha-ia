import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import hashlib
from PIL import Image
import re
import base64

# Configuração da página
st.set_page_config(
    page_title="ScriptMaster AI - Game Dev Edition 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CÓDIGO MASTER
MASTER_CODE = "GuizinhsDono"

# ====== TEMPLATES DE JOGOS ======
GAME_TEMPLATES = {
    "🎮 Godot 4.6 - Jogo 2D Mobile": {
        "main": """extends Node2D

# Sistema principal do jogo mobile
# Otimizado para toque (touch)

@onready var player = $Player
@onready var score_label = $UI/ScoreLabel
@onready var touch_detector = $TouchDetector

var score = 0
var game_running = false

func _ready():
    get_tree().get_root().set_content_scale_mode(Window.CONTENT_SCALE_MODE_CANVAS_ITEMS)
    get_tree().get_root().set_content_scale_aspect(Window.CONTENT_SCALE_ASPECT_KEEP)
    setup_mobile_controls()

func setup_mobile_controls():
    # Configurar controles touch
    Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func _input(event):
    if event is InputEventScreenTouch:
        if event.pressed:
            on_screen_touch(event.position)

func on_screen_touch(pos: Vector2):
    if not game_running:
        start_game()
    else:
        player.jump()

func start_game():
    game_running = true
    score = 0
    update_score()

func add_score(points: int):
    score += points
    update_score()

func update_score():
    score_label.text = "Score: " + str(score)

func game_over():
    game_running = false
    # Mostrar tela de game over
    $UI/GameOverPanel.visible = true
""",
        "player": """extends CharacterBody2D

# Player com controles mobile otimizados

const JUMP_FORCE = -600.0
const GRAVITY = 1800.0
const MAX_FALL_SPEED = 1000.0

@export var speed = 300.0

var is_jumping = false

func _ready():
    # Configurar animações
    $AnimatedSprite2D.play("idle")

func _physics_process(delta):
    # Aplicar gravidade
    if not is_on_floor():
        velocity.y = min(velocity.y + GRAVITY * delta, MAX_FALL_SPEED)
    else:
        velocity.y = 0
        is_jumping = false
    
    # Movimento automático (endless runner style)
    velocity.x = speed
    
    # Animações
    if velocity.y < 0:
        $AnimatedSprite2D.play("jump")
    elif velocity.y > 0:
        $AnimatedSprite2D.play("fall")
    else:
        $AnimatedSprite2D.play("run")
    
    move_and_slide()

func jump():
    if is_on_floor() and not is_jumping:
        velocity.y = JUMP_FORCE
        is_jumping = true
        $JumpSound.play()

func die():
    get_parent().game_over()
    queue_free()
""",
        "export": """# CONFIGURAÇÃO DE EXPORT PARA MOBILE

[preset.0]
name="Android"
platform="Android"
runnable=true

[preset.0.options]
custom_template/debug=""
custom_template/release=""
gradle_build/use_gradle_build=true
gradle_build/min_sdk=21
gradle_build/target_sdk=33
architectures/armeabi-v7a=true
architectures/arm64-v8a=true
screen/immersive_mode=true
screen/support_small=true
screen/support_normal=true
screen/support_large=true
screen/support_xlarge=true
permissions/access_network_state=false
permissions/internet=false

# Para iOS - adicione preset separado
[preset.1]
name="iOS"
platform="iOS"
runnable=true
"""
    },
    
    "🎮 Godot 4.6 - Sistema de Combate": {
        "combat": """extends Node

# Sistema de combate RPG

class_name CombatSystem

signal damage_dealt(amount, target)
signal battle_ended(winner)

@export var player: CharacterBody2D
@export var enemy: CharacterBody2D

enum State {IDLE, ATTACKING, DEFENDING, USING_SKILL}
var current_state = State.IDLE

func attack(attacker: Node, defender: Node, damage: float):
    var final_damage = calculate_damage(attacker, defender, damage)
    defender.take_damage(final_damage)
    damage_dealt.emit(final_damage, defender)
    
    # Efeitos visuais
    spawn_damage_number(defender.global_position, final_damage)
    play_hit_effect(defender)

func calculate_damage(attacker, defender, base_damage):
    var attack_power = attacker.get("attack", 10)
    var defense = defender.get("defense", 5)
    var critical = randf() < 0.2  # 20% chance de crítico
    
    var damage = base_damage + attack_power - defense
    if critical:
        damage *= 2
        show_critical_effect()
    
    return max(damage, 1)

func spawn_damage_number(pos: Vector2, damage: float):
    var label = Label.new()
    label.text = str(int(damage))
    label.position = pos
    label.add_theme_font_size_override("font_size", 32)
    add_child(label)
    
    # Animar número
    var tween = create_tween()
    tween.tween_property(label, "position:y", pos.y - 50, 0.5)
    tween.parallel().tween_property(label, "modulate:a", 0, 0.5)
    tween.tween_callback(label.queue_free)

func play_hit_effect(target):
    var flash_tween = create_tween()
    flash_tween.tween_property(target, "modulate", Color.RED, 0.1)
    flash_tween.tween_property(target, "modulate", Color.WHITE, 0.1)
"""
    },
    
    "🌐 HTML5 - Jogo Completo (Phaser 3)": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Meu Jogo HTML5</title>
    <script src="https://cdn.jsdelivr.net/npm/phaser@3.60.0/dist/phaser.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        canvas {
            border-radius: 10px;
        }
    </style>
</head>
<body>

<script>
// Configuração do jogo
const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    backgroundColor: '#2d2d2d',
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    },
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 800 },
            debug: false
        }
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

const game = new Phaser.Game(config);

let player;
let platforms;
let cursors;
let score = 0;
let scoreText;
let gameOver = false;

function preload() {
    // Criar sprites simples (retângulos coloridos)
    this.textures.generate('player', { data: ['2'], pixelWidth: 32 });
    this.textures.generate('platform', { data: ['1'], pixelWidth: 64 });
    this.textures.generate('star', { data: ['3'], pixelWidth: 16 });
}

function create() {
    // Criar plataformas
    platforms = this.physics.add.staticGroup();
    
    // Chão
    platforms.create(400, 568, 'platform').setScale(12.5, 1).refreshBody();
    
    // Plataformas no ar
    platforms.create(600, 400, 'platform').setScale(2, 1).refreshBody();
    platforms.create(50, 250, 'platform').setScale(2, 1).refreshBody();
    platforms.create(750, 220, 'platform').setScale(2, 1).refreshBody();
    
    // Criar player
    player = this.physics.add.sprite(100, 450, 'player');
    player.setTint(0x00ff00);
    player.setBounce(0.2);
    player.setCollideWorldBounds(true);
    
    // Física
    this.physics.add.collider(player, platforms);
    
    // Controles
    cursors = this.input.keyboard.createCursorKeys();
    
    // Controles touch para mobile
    this.input.on('pointerdown', function(pointer) {
        if (pointer.x < 400 && player.body.touching.down) {
            player.setVelocityY(-500); // Pulo
        }
    });
    
    // Estrelas (colecionáveis)
    const stars = this.physics.add.group({
        key: 'star',
        repeat: 11,
        setXY: { x: 12, y: 0, stepX: 70 }
    });
    
    stars.children.iterate(function (child) {
        child.setTint(0xffff00);
        child.setBounceY(Phaser.Math.FloatBetween(0.4, 0.8));
    });
    
    this.physics.add.collider(stars, platforms);
    this.physics.add.overlap(player, stars, collectStar, null, this);
    
    // Texto de pontuação
    scoreText = this.add.text(16, 16, 'Score: 0', { 
        fontSize: '32px', 
        fill: '#fff',
        fontFamily: 'Arial'
    });
    
    // Texto de game over
    this.gameOverText = this.add.text(400, 300, 'GAME OVER', {
        fontSize: '64px',
        fill: '#ff0000',
        fontFamily: 'Arial'
    }).setOrigin(0.5).setVisible(false);
}

function update() {
    if (gameOver) {
        return;
    }
    
    // Movimento do player
    if (cursors.left.isDown) {
        player.setVelocityX(-300);
        player.setTint(0x00ff00);
    }
    else if (cursors.right.isDown) {
        player.setVelocityX(300);
        player.setTint(0x0000ff);
    }
    else {
        player.setVelocityX(0);
        player.setTint(0x00ff00);
    }
    
    // Pulo
    if (cursors.up.isDown && player.body.touching.down) {
        player.setVelocityY(-500);
    }
    
    // Verificar se caiu
    if (player.y > 600) {
        endGame.call(this);
    }
}

function collectStar(player, star) {
    star.disableBody(true, true);
    score += 10;
    scoreText.setText('Score: ' + score);
    
    // Efeito sonoro (vibração no mobile)
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
}

function endGame() {
    gameOver = true;
    this.gameOverText.setVisible(true);
    this.physics.pause();
    player.setTint(0xff0000);
    
    // Reiniciar após 3 segundos
    this.time.delayedCall(3000, () => {
        this.scene.restart();
        score = 0;
        gameOver = false;
    });
}
</script>

</body>
</html>
""",

    "🌐 HTML5 - Jogo Canvas Puro": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jogo Canvas Puro</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #1a1a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: Arial;
        }
        canvas {
            border: 3px solid #fff;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(255,255,255,0.3);
        }
        #gameInfo {
            position: absolute;
            top: 20px;
            color: white;
            font-size: 24px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }
    </style>
</head>
<body>

<div id="gameInfo">Score: <span id="score">0</span></div>
<canvas id="gameCanvas"></canvas>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Ajustar para mobile
canvas.width = window.innerWidth > 800 ? 800 : window.innerWidth - 20;
canvas.height = window.innerHeight > 600 ? 600 : window.innerHeight - 100;

// Variáveis do jogo
let score = 0;
let gameRunning = true;

// Player
const player = {
    x: 50,
    y: canvas.height - 100,
    width: 40,
    height: 40,
    color: '#00ff00',
    velocityY: 0,
    jumping: false,
    
    draw() {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // Olhos
        ctx.fillStyle = '#fff';
        ctx.fillRect(this.x + 10, this.y + 10, 8, 8);
        ctx.fillRect(this.x + 22, this.y + 10, 8, 8);
    },
    
    update() {
        // Gravidade
        this.velocityY += 0.8;
        this.y += this.velocityY;
        
        // Chão
        if (this.y + this.height > canvas.height - 50) {
            this.y = canvas.height - 50 - this.height;
            this.velocityY = 0;
            this.jumping = false;
        }
    },
    
    jump() {
        if (!this.jumping) {
            this.velocityY = -15;
            this.jumping = true;
        }
    }
};

// Obstáculos
const obstacles = [];
let obstacleTimer = 0;

function createObstacle() {
    obstacles.push({
        x: canvas.width,
        y: canvas.height - 80,
        width: 30,
        height: 50,
        color: '#ff0000',
        speed: 5
    });
}

function updateObstacles() {
    obstacleTimer++;
    if (obstacleTimer > 100) {
        createObstacle();
        obstacleTimer = 0;
    }
    
    obstacles.forEach((obs, index) => {
        obs.x -= obs.speed;
        
        // Remover se saiu da tela
        if (obs.x + obs.width < 0) {
            obstacles.splice(index, 1);
            score += 10;
            document.getElementById('score').textContent = score;
        }
        
        // Detectar colisão
        if (checkCollision(player, obs)) {
            gameOver();
        }
    });
}

function drawObstacles() {
    obstacles.forEach(obs => {
        ctx.fillStyle = obs.color;
        ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
    });
}

function checkCollision(rect1, rect2) {
    return rect1.x < rect2.x + rect2.width &&
           rect1.x + rect1.width > rect2.x &&
           rect1.y < rect2.y + rect2.height &&
           rect1.y + rect1.height > rect2.y;
}

function drawGround() {
    ctx.fillStyle = '#654321';
    ctx.fillRect(0, canvas.height - 50, canvas.width, 50);
    
    // Grama
    ctx.fillStyle = '#228B22';
    ctx.fillRect(0, canvas.height - 55, canvas.width, 5);
}

function drawClouds() {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.beginPath();
    ctx.arc(100, 80, 30, 0, Math.PI * 2);
    ctx.arc(140, 80, 35, 0, Math.PI * 2);
    ctx.arc(180, 80, 30, 0, Math.PI * 2);
    ctx.fill();
}

function gameLoop() {
    if (!gameRunning) return;
    
    // Limpar canvas
    ctx.fillStyle = '#87CEEB';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Desenhar elementos
    drawClouds();
    drawGround();
    player.update();
    player.draw();
    updateObstacles();
    drawObstacles();
    
    requestAnimationFrame(gameLoop);
}

function gameOver() {
    gameRunning = false;
    
    // Tela de game over
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#fff';
    ctx.font = '48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2);
    ctx.font = '24px Arial';
    ctx.fillText('Score: ' + score, canvas.width / 2, canvas.height / 2 + 40);
    ctx.fillText('Toque para reiniciar', canvas.width / 2, canvas.height / 2 + 80);
}

function restart() {
    score = 0;
    obstacles.length = 0;
    player.y = canvas.height - 100;
    player.velocityY = 0;
    gameRunning = true;
    document.getElementById('score').textContent = score;
    gameLoop();
}

// Controles
document.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
        if (gameRunning) {
            player.jump();
        } else {
            restart();
        }
    }
});

// Touch para mobile
canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    if (gameRunning) {
        player.jump();
    } else {
        restart();
    }
});

canvas.addEventListener('click', () => {
    if (gameRunning) {
        player.jump();
    } else {
        restart();
    }
});

// Iniciar jogo
gameLoop();
</script>

</body>
</html>
""",

    "📱 React Native - Jogo Mobile": """// App.js - Jogo mobile com React Native
import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, View, Text, TouchableOpacity, 
  Animated, Dimensions, Vibration
} from 'react-native';

const { width, height } = Dimensions.get('window');

export default function GameApp() {
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const [gameStarted, setGameStarted] = useState(false);
  
  const playerY = useRef(new Animated.Value(height - 200)).current;
  const obstacleX = useRef(new Animated.Value(width)).current;
  
  const jump = () => {
    if (!gameStarted) {
      setGameStarted(true);
      startGame();
      return;
    }
    
    Animated.sequence([
      Animated.timing(playerY, {
        toValue: height - 400,
        duration: 300,
        useNativeDriver: true
      }),
      Animated.timing(playerY, {
        toValue: height - 200,
        duration: 300,
        useNativeDriver: true
      })
    ]).start();
    
    Vibration.vibrate(50);
  };
  
  const startGame = () => {
    setScore(0);
    setGameOver(false);
    
    // Animar obstáculo
    obstacleX.setValue(width);
    Animated.loop(
      Animated.timing(obstacleX, {
        toValue: -100,
        duration: 2000,
        useNativeDriver: true
      })
    ).start();
    
    // Incrementar score
    const scoreInterval = setInterval(() => {
      if (!gameOver) {
        setScore(prev => prev + 1);
      }
    }, 100);
    
    return () => clearInterval(scoreInterval);
  };
  
  const checkCollision = () => {
    // Lógica de colisão simplificada
    obstacleX.addListener(({ value }) => {
      if (value < 100 && value > 0) {
        playerY.addListener(({ value: y }) => {
          if (y > height - 250) {
            setGameOver(true);
            Vibration.vibrate([0, 100, 50, 100]);
          }
        });
      }
    });
  };
  
  useEffect(() => {
    if (gameStarted) {
      checkCollision();
    }
  }, [gameStarted]);
  
  return (
    <TouchableOpacity 
      style={styles.container} 
      activeOpacity={1}
      onPress={jump}
    >
      {/* Céu */}
      <View style={styles.sky} />
      
      {/* Score */}
      <Text style={styles.score}>Score: {score}</Text>
      
      {/* Player */}
      <Animated.View 
        style={[
          styles.player, 
          { transform: [{ translateY: playerY }] }
        ]} 
      />
      
      {/* Obstáculo */}
      <Animated.View 
        style={[
          styles.obstacle,
          { transform: [{ translateX: obstacleX }] }
        ]} 
      />
      
      {/* Chão */}
      <View style={styles.ground} />
      
      {/* Game Over */}
      {gameOver && (
        <View style={styles.gameOverContainer}>
          <Text style={styles.gameOverText}>GAME OVER</Text>
          <Text style={styles.finalScore}>Score: {score}</Text>
          <TouchableOpacity 
            style={styles.restartButton}
            onPress={() => {
              setGameStarted(false);
              setGameOver(false);
            }}
          >
            <Text style={styles.restartText}>Reiniciar</Text>
          </TouchableOpacity>
        </View>
      )}
      
      {/* Instruções iniciais */}
      {!gameStarted && !gameOver && (
        <View style={styles.startContainer}>
          <Text style={styles.startText}>Toque para começar</Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#87CEEB',
  },
  sky: {
    flex: 1,
  },
  score: {
    position: 'absolute',
    top: 50,
    alignSelf: 'center',
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    textShadowColor: '#000',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 5,
  },
  player: {
    position: 'absolute',
    left: 50,
    width: 50,
    height: 50,
    backgroundColor: '#00ff00',
    borderRadius: 5,
  },
  obstacle: {
    position: 'absolute',
    bottom: 50,
    width: 40,
    height: 60,
    backgroundColor: '#ff0000',
  },
  ground: {
    position: 'absolute',
    bottom: 0,
    width: '100%',
    height: 50,
    backgroundColor: '#654321',
  },
  gameOverContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  gameOverText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#ff0000',
    marginBottom: 20,
  },
  finalScore: {
    fontSize: 32,
    color: '#fff',
    marginBottom: 40,
  },
  restartButton: {
    backgroundColor: '#00ff00',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 10,
  },
  restartText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
  },
  startContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  startText: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
    textShadowColor: '#000',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 5,
  },
});
""",

    "🎮 Unity C# - Player Controller Mobile": """using UnityEngine;
using UnityEngine.InputSystem;

public class MobilePlayerController : MonoBehaviour
{
    [Header("Movimento")]
    public float moveSpeed = 5f;
    public float jumpForce = 10f;
    public float gravity = -20f;
    
    [Header("Mobile Controls")]
    public Joystick joystick;
    public bool useGyroscope = false;
    
    private CharacterController controller;
    private Vector3 velocity;
    private bool isGrounded;
    private Animator animator;
    
    void Start()
    {
        controller = GetComponent<CharacterController>();
        animator = GetComponent<Animator>();
        
        // Ativar giroscópio se disponível
        if (useGyroscope && SystemInfo.supportsGyroscope)
        {
            Input.gyro.enabled = true;
        }
    }
    
    void Update()
    {
        // Verificar se está no chão
        isGrounded = controller.isGrounded;
        
        if (isGrounded && velocity.y < 0)
        {
            velocity.y = -2f;
        }
        
        // Movimento
        Vector3 move = GetMovementInput();
        controller.Move(move * moveSpeed * Time.deltaTime);
        
        // Rotação baseada no movimento
        if (move != Vector3.zero)
        {
            transform.forward = move;
        }
        
        // Gravidade
        velocity.y += gravity * Time.deltaTime;
        controller.Move(velocity * Time.deltaTime);
        
        // Animações
        UpdateAnimations(move);
    }
    
    Vector3 GetMovementInput()
    {
        Vector3 move = Vector3.zero;
        
        #if UNITY_EDITOR || UNITY_STANDALONE
        // Controles de teclado (para testes)
        move = new Vector3(Input.GetAxis("Horizontal"), 0, Input.GetAxis("Vertical"));
        #else
        // Controles mobile
        if (joystick != null)
        {
            move = new Vector3(joystick.Horizontal, 0, joystick.Vertical);
        }
        else if (useGyroscope && Input.gyro.enabled)
        {
            // Controle por giroscópio
            Vector3 gyro = Input.gyro.rotationRate;
            move = new Vector3(gyro.y, 0, -gyro.x) * 0.1f;
        }
        #endif
        
        return move.normalized;
    }
    
    public void Jump()
    {
        if (isGrounded)
        {
            velocity.y = Mathf.Sqrt(jumpForce * -2f * gravity);
            
            // Vibração
            Handheld.Vibrate();
        }
    }
    
    void UpdateAnimations(Vector3 move)
    {
        if (animator != null)
        {
            animator.SetFloat("Speed", move.magnitude);
            animator.SetBool("IsGrounded", isGrounded);
            animator.SetFloat("VerticalVelocity", velocity.y);
        }
    }
    
    // Método para ser chamado por botão UI
    public void OnJumpButtonPressed()
    {
        Jump();
    }
}
"""
}

# Templates de scripts normais (mantidos do código anterior)
SCRIPT_TEMPLATES = {
    "🐍 Python - Web Scraper": """import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def scrape_website(url):
    '''Extrai dados de um website e salva em CSV'''
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Exemplo: extrair todos os links
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text(strip=True)
            if href:
                links.append({'url': href, 'text': text})
        
        # Salvar em CSV
        filename = f'scraped_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'text'])
            writer.writeheader()
            writer.writerows(links)
        
        print(f"✅ {len(links)} links salvos em {filename}")
        return links
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

if __name__ == "__main__":
    url = "https://example.com"
    data = scrape_website(url)
""",

    "🐍 Python - Bot Telegram": """from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# Token do bot (pegue com @BotFather no Telegram)
TOKEN = 'SEU_TOKEN_AQUI'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Comando /start'''
    await update.message.reply_text(
        '👋 Olá! Eu sou seu bot!\n\n'
        'Comandos disponíveis:\n'
        '/start - Iniciar bot\n'
        '/help - Ajuda\n'
        '/info - Informações'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Comando /help'''
    await update.message.reply_text('📚 Como posso ajudar você?')

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Comando /info'''
    user = update.effective_user
    await update.message.reply_text(
        f'ℹ️ Suas informações:\n'
        f'Nome: {user.first_name}\n'
        f'Username: @{user.username}\n'
        f'ID: {user.id}'
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Responde mensagens de texto'''
    text = update.message.text
    await update.message.reply_text(f'Você disse: {text}')

def main():
    '''Função principal'''
    # Criar aplicação
    app = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Iniciar bot
    print("🤖 Bot iniciado!")
    app.run_polling()

if __name__ == '__main__':
    main()
""",

    "💻 JavaScript - Discord Bot": """// Bot Discord completo
const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');

const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds, 
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ] 
});

const prefix = '!';

client.on('ready', () => {
    console.log(`✅ Bot ${client.user.tag} online!`);
    client.user.setActivity('!help para comandos', { type: 'PLAYING' });
});

client.on('messageCreate', async message => {
    // Ignorar bots
    if (message.author.bot) return;
    
    // Verificar prefix
    if (!message.content.startsWith(prefix)) return;
    
    const args = message.content.slice(prefix.length).trim().split(/ +/);
    const command = args.shift().toLowerCase();
    
    // Comandos
    switch(command) {
        case 'ping':
            const ping = Date.now() - message.createdTimestamp;
            message.reply(`🏓 Pong! Latência: ${ping}ms`);
            break;
            
        case 'hello':
            message.reply(`👋 Olá, ${message.author.username}!`);
            break;
            
        case 'server':
            message.reply(`📊 Servidor: ${message.guild.name}\nMembros: ${message.guild.memberCount}`);
            break;
            
        case 'avatar':
            const user = message.mentions.users.first() || message.author;
            const embed = new EmbedBuilder()
                .setTitle(`Avatar de ${user.username}`)
                .setImage(user.displayAvatarURL({ dynamic: true, size: 1024 }))
                .setColor('#00ff00');
            message.reply({ embeds: [embed] });
            break;
            
        case 'help':
            const helpEmbed = new EmbedBuilder()
                .setTitle('📚 Comandos Disponíveis')
                .setDescription(
                    '`!ping` - Ver latência\n' +
                    '`!hello` - Saudação\n' +
                    '`!server` - Info do servidor\n' +
                    '`!avatar [@user]` - Ver avatar\n' +
                    '`!help` - Esta mensagem'
                )
                .setColor('#0099ff');
            message.reply({ embeds: [helpEmbed] });
            break;
            
        default:
            message.reply('❌ Comando não encontrado! Use `!help`');
    }
});

client.login('SEU_TOKEN_AQUI');
"""
}

# Combinar todos os templates
ALL_TEMPLATES = {**GAME_TEMPLATES, **SCRIPT_TEMPLATES}

# Função para detectar linguagem
def detect_language(code):
    code_lower = code.lower()
    if 'extends' in code and 'func ' in code:
        return 'gdscript'
    elif 'using UnityEngine' in code:
        return 'csharp'
    elif '<!DOCTYPE html>' in code or '<html>' in code:
        return 'html'
    elif 'import React' in code or 'from react' in code_lower:
        return 'jsx'
    elif 'import ' in code or 'def ' in code:
        return 'python'
    elif 'const ' in code or 'function' in code:
        return 'javascript'
    elif 'CREATE TABLE' in code.upper():
        return 'sql'
    return 'python'

# Função hash
def hash_code(code):
    return hashlib.sha256(code.encode()).hexdigest()

# Inicializar session state
default_states = {
    "authenticated": False,
    "is_master": False,
    "vip_until": None,
    "username": None,
    "msgs": [],
    "saved_scripts": [],
    "current_script": "",
    "created_codes": {},
    "current_game_files": {}
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .game-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        text-align: center;
    }
    
    .game-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .master-badge {
        background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 700;
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
    
    .template-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
        border-left: 5px solid #FFD700;
    }
    
    .template-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .code-block {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 1.5rem;
        border-radius: 10px;
        font-family: 'JetBrains Mono', monospace;
        border-left: 4px solid #667eea;
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
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except:
        return []

# ====== TELA DE LOGIN ======
if not st.session_state.authenticated:
    st.markdown("""
    <div class="game-header">
        <h1>🎮 ScriptMaster AI - Game Dev Edition</h1>
        <p style="color: white; font-size: 1.3rem;">Crie Scripts e Jogos Completos com IA</p>
        <p style="color: rgba(255,255,255,0.9);">Godot 4.6 • Unity • HTML5 • Mobile</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔐 Login")
        username = st.text_input("👤 Nome", placeholder="Digite seu nome")
        access_code = st.text_input("🎫 Código", type="password", placeholder="MASTER ou VIP")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Entrar", use_container_width=True):
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
            if st.button("🆓 Grátis", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.username = username or "Dev"
                st.rerun()
    
    with col2:
        st.markdown("### 🎯 Recursos Especiais")
        st.markdown("""
        **🎮 Engines Suportadas:**
        - ✅ Godot 4.6 (GDScript + C#)
        - ✅ Unity (C# completo)
        - ✅ HTML5 (Phaser, Canvas)
        - ✅ Mobile (React Native)
        
        **👑 VIP Exclusivo:**
        - ✅ Templates de jogos prontos
        - ✅ Sistema de múltiplos arquivos
        - ✅ Export configs automáticas
        - ✅ Assets e sprites
        - ✅ Documentação completa
        
        **🔥 MASTER:**
        - ✅ Criar códigos VIP ilimitados
        - ✅ Painel de administração
        - ✅ Acesso vitalício total
        """)
    
    st.stop()

# ====== SIDEBAR ======
with st.sidebar:
    if st.session_state.is_master:
        st.markdown('<div class="master-badge">🔥 MASTER</div>', unsafe_allow_html=True)
        
        st.markdown("### 🎫 Gerenciar Códigos")
        with st.expander("➕ Criar Código VIP"):
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
                    st.success(f"✅ Código criado!")
                    st.code(novo_codigo)
        
        if st.session_state.created_codes:
            st.markdown("### 📋 Códigos Criados")
            for code, info in list(st.session_state.created_codes.items())[:5]:
                status = "✅ USADO" if info.get("used") else "🎫 DISPONÍVEL"
                st.text(f"{status[:2]} {code}")
        
        st.divider()
    
    elif is_vip_active():
        dias = (st.session_state.vip_until - datetime.now()).days
        st.markdown(f'<div class="vip-badge">👑 VIP - {dias}d</div>', unsafe_allow_html=True)
    
    st.markdown(f"**👤 {st.session_state.username}**")
    
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    st.divider()
    
    # Templates
    st.markdown("### 🎮 Templates de Jogos")
    
    for template_name in GAME_TEMPLATES.keys():
        if st.button(template_name, use_container_width=True, key=f"game_{template_name}"):
            template_data = GAME_TEMPLATES[template_name]
            if isinstance(template_data, dict):
                st.session_state.current_game_files = template_data
                st.session_state.current_script = template_data.get('main', list(template_data.values())[0])
            else:
                st.session_state.current_script = template_data
            st.rerun()
    
    st.divider()
    
    st.markdown("### 📚 Templates de Scripts")
    for template_name in SCRIPT_TEMPLATES.keys():
        if st.button(template_name, use_container_width=True, key=f"script_{template_name}"):
            st.session_state.current_script = SCRIPT_TEMPLATES[template_name]
            st.rerun()
    
    st.divider()
    
    # Scripts salvos
    if st.session_state.saved_scripts:
        st.markdown("### 💾 Salvos")
        for idx, script in enumerate(st.session_state.saved_scripts[-5:]):
            if st.button(f"📄 {script['name']}", key=f"saved_{idx}", use_container_width=True):
                st.session_state.current_script = script['code']
                st.rerun()

# ====== ÁREA PRINCIPAL ======

st.markdown("""
<div class="game-header">
    <h1>🎮 ScriptMaster AI - Game Dev Edition</h1>
    <p style="color: white;">Godot • Unity • HTML5 • Mobile</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🤖 Gerar Código", "💻 Editor", "📁 Arquivos do Jogo", "📚 Biblioteca"])

# TAB 1: Gerar
with tab1:
    st.markdown("### 🎯 O que você quer criar?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt_game = st.text_area(
            "Descreva seu projeto:",
            placeholder="Ex: Crie um jogo endless runner em Godot 4.6 para mobile com controles touch",
            height=150
        )
    
    with col2:
        tipo_projeto = st.selectbox(
            "🎮 Tipo",
            ["Godot 4.6 GDScript", "Godot 4.6 C#", "Unity C#", "HTML5 Phaser", "HTML5 Canvas", "React Native", "Script Python", "Script JavaScript"]
        )
        
        plataforma = st.select_slider(
            "📱 Plataforma",
            ["PC", "Mobile", "Web", "Multiplataforma"]
        )
    
    if st.button("⚡ GERAR PROJETO COMPLETO", use_container_width=True, type="primary"):
        if not prompt_game:
            st.error("❌ Descreva o que você precisa!")
        else:
            with st.spinner("🔮 Gerando projeto..."):
                try:
                    modelos = get_models()
                    modelo = modelos[0] if modelos else "gemini-pro"
                    model = genai.GenerativeModel(modelo)
                    
                    # Prompt especializado para jogos
                    if "Godot" in tipo_projeto:
                        linguagem = "GDScript" if "GDScript" in tipo_projeto else "C#"
                        prompt_completo = f"""
Você é um expert em desenvolvimento de jogos com Godot 4.6.

**Requisitos:**
{prompt_game}

**Plataforma:** {plataforma}
**Linguagem:** {linguagem}

**Instruções:**
1. Crie um código COMPLETO e FUNCIONAL para Godot 4.6
2. Use as melhores práticas de Godot 4.x
3. Inclua sistema de input mobile se for para mobile
4. Adicione comentários explicativos
5. Configure exports e signals corretamente
6. Otimize para a plataforma escolhida

Retorne APENAS o código, começando direto com 'extends'.
"""
                    elif "Unity" in tipo_projeto:
                        prompt_completo = f"""
Você é um expert em desenvolvimento Unity.

**Requisitos:**
{prompt_game}

**Plataforma:** {plataforma}

**Instruções:**
1. Crie código C# COMPLETO para Unity
2. Use namespaces e boas práticas
3. Inclua suporte mobile se necessário
4. Adicione comentários XML
5. Implemente MonoBehaviour corretamente

Retorne APENAS o código C#.
"""
                    elif "HTML5" in tipo_projeto:
                        engine = "Phaser 3" if "Phaser" in tipo_projeto else "Canvas puro"
                        prompt_completo = f"""
Você é um expert em jogos HTML5.

**Requisitos:**
{prompt_game}

**Engine:** {engine}

**Instruções:**
1. Crie um jogo HTML5 COMPLETO e funcional
2. Inclua CSS inline para estilização
3. Otimize para mobile (touch controls)
4. Adicione responsividade
5. Código pronto para rodar

Retorne o HTML completo.
"""
                    else:
                        prompt_completo = f"""
Crie um código COMPLETO em {tipo_projeto} para:
{prompt_game}

Plataforma: {plataforma}

Código pronto para usar com comentários.
"""
                    
                    response = model.generate_content(prompt_completo)
                    codigo_gerado = response.text
                    
                    # Limpar markdown
                    codigo_gerado = re.sub(r'```[\w]*\n', '', codigo_gerado)
                    codigo_gerado = codigo_gerado.replace('```', '')
                    
                    st.session_state.current_script = codigo_gerado
                    st.success("✅ Projeto gerado!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")

# TAB 2: Editor
with tab2:
    if st.session_state.current_script:
        st.markdown("### 💻 Editor de Código")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            script_name = st.text_input("📝 Nome", value="main", key="script_name")
        
        with col2:
            lang = detect_language(st.session_state.current_script)
            ext_map = {
                'gdscript': '.gd',
                'csharp': '.cs',
                'html': '.html',
                'jsx': '.jsx',
                'python': '.py',
                'javascript': '.js'
            }
            file_ext = st.text_input("📄 Extensão", value=ext_map.get(lang, '.txt'))
        
        with col3:
            if is_vip_active():
                if st.button("💾 Salvar", use_container_width=True):
                    st.session_state.saved_scripts.append({
                        "name": f"{script_name}{file_ext}",
                        "code": st.session_state.current_script,
                        "language": lang,
                        "created_at": datetime.now().isoformat()
                    })
                    st.success("✅ Salvo!")
            else:
                st.info("🔒 VIP")
        
        with col4:
            st.download_button(
                "📥 Download",
                data=st.session_state.current_script,
                file_name=f"{script_name}{file_ext}",
                use_container_width=True
            )
        
        # Editor
        edited = st.text_area("Código:", value=st.session_state.current_script, height=500, key="editor")
        st.session_state.current_script = edited
        
        # Preview
        st.markdown("### 👁️ Preview")
        st.code(st.session_state.current_script, language=lang)
    else:
        st.info("👈 Escolha um template ou gere código!")

# TAB 3: Arquivos do Jogo (múltiplos arquivos para projetos Godot/Unity)
with tab3:
    if st.session_state.current_game_files:
        st.markdown("### 📁 Arquivos do Projeto")
        
        for filename, code in st.session_state.current_game_files.items():
            with st.expander(f"📄 {filename}.gd"):
                st.code(code, language='gdscript')
                st.download_button(
                    "📥 Download",
                    data=code,
                    file_name=f"{filename}.gd",
                    key=f"download_{filename}"
                )
    else:
        st.info("📭 Nenhum projeto multi-arquivo carregado")

# TAB 4: Biblioteca
with tab4:
    if st.session_state.saved_scripts:
        st.markdown("### 📚 Scripts Salvos")
        for idx, script in enumerate(reversed(st.session_state.saved_scripts)):
            with st.expander(f"📄 {script['name']}"):
                st.code(script['code'], language=script.get('language', 'python'))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("📥 Download", data=script['code'], file_name=script['name'], key=f"dl_{idx}")
                with col2:
                    if st.button("📋 Copiar", key=f"cp_{idx}"):
                        st.session_state.current_script = script['code']
                        st.success("✅ Copiado!")
                with col3:
                    if st.button("🗑️ Deletar", key=f"del_{idx}"):
                        real_idx = len(st.session_state.saved_scripts) - 1 - idx
                        st.session_state.saved_scripts.pop(real_idx)
                        st.rerun()
    else:
        st.info("📭 Nenhum script salvo")

# Rodapé
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🎮 Projetos", len(st.session_state.saved_scripts))

with col2:
    st.metric("⚡ Status", "VIP" if is_vip_active() else "FREE")

with col3:
    if st.session_state.current_script:
        lines = len(st.session_state.current_script.split('\n'))
        st.metric("📏 Linhas", lines)

with col4:
    lang = detect_language(st.session_state.current_script) if st.session_state.current_script else "N/A"
    st.metric("🔤 Lang", lang.upper())
