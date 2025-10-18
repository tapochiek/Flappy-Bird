"""
Конфигурационный файл для Flappy Bird
Содержит все константы игры для удобной настройки
"""

# Размеры экрана
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Физика птицы
GRAVITY = 0.25
BIRD_JUMP = -6.0
DEATH_GRAVITY_MULTIPLIER = 1.5  # Ускоренное падение при смерти
ROTATION_SPEED = 3  # Скорость вращения при падении

# Размеры птицы
BIRD_WIDTH = 34
BIRD_HEIGHT = 24

# Параметры труб
PIPE_GAP = 150
PIPE_WIDTH = 52
PIPE_HEIGHT = 500
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 1500  # миллисекунды
PIPE_MIN_OFFSET = 50  # минимальное расстояние от края экрана

# Размеры базы
BASE_HEIGHT = 133
BASE_SPEED = 3

# Размеры UI элементов
GAME_OVER_WIDTH = 192
GAME_OVER_HEIGHT = 42
MESSAGE_WIDTH = 184
MESSAGE_HEIGHT = 267

# Углы вращения птицы
ROTATE_UP = 25
ROTATE_DOWN = -90

# Настройки игры
FPS = 60

# Пути к ресурсам
ASSET_PATH = "assets"
BACKGROUND_IMAGE = f"{ASSET_PATH}/background.png"
BIRD_IMAGE = f"{ASSET_PATH}/bird.png"
PIPE_IMAGE = f"{ASSET_PATH}/pipe.png"
BASE_IMAGE = f"{ASSET_PATH}/base.png"
GAME_OVER_IMAGE = f"{ASSET_PATH}/gameover.png"
MESSAGE_IMAGE = f"{ASSET_PATH}/message.png"
JUMP_SOUND = f"{ASSET_PATH}/jump.wav"
HIT_SOUND = f"{ASSET_PATH}/hit.wav"
POINT_SOUND = f"{ASSET_PATH}/point.wav"

# Консоль
CONSOLE_HEIGHT = 30
CONSOLE_FONT_SIZE = 30
CONSOLE_BG_COLOR = (0, 0, 0)
CONSOLE_TEXT_COLOR = (255, 255, 255)

# FPS Display
FPS_FONT_SIZE = 24
FPS_COLOR = (255, 255, 255)
FPS_POSITION = (5, 5)
