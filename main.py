"""
Flappy Bird - улучшенная версия с оптимизированной архитектурой
"""
import pygame
import random
from config import *

pygame.init()


def load_image(path, size=None):
    """Загружает изображение с опциональным изменением размера"""
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Ошибка загрузки изображения {path}: {e}")
        # Создаём заглушку
        surface = pygame.Surface(size if size else (50, 50))
        surface.fill((255, 0, 255))
        return surface


def load_assets():
    """Централизованная загрузка всех ресурсов игры"""
    assets = {}
    
    # Изображения
    assets["background"] = load_image(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
    assets["bird"] = load_image(BIRD_IMAGE, (BIRD_WIDTH, BIRD_HEIGHT))
    assets["pipe"] = load_image(PIPE_IMAGE, (PIPE_WIDTH, PIPE_HEIGHT))
    assets["base"] = load_image(BASE_IMAGE, (SCREEN_WIDTH, BASE_HEIGHT))
    assets["game_over"] = load_image(GAME_OVER_IMAGE, (GAME_OVER_WIDTH, GAME_OVER_HEIGHT))
    assets["message"] = load_image(MESSAGE_IMAGE, (MESSAGE_WIDTH, MESSAGE_HEIGHT))
    
    # Цифры для счёта
    assets["numbers"] = []
    for i in range(10):
        try:
            assets["numbers"].append(load_image(f"{ASSET_PATH}/{i}.png"))
        except Exception as e:
            print(f"Ошибка загрузки цифры {i}: {e}")
            assets["numbers"].append(load_image(BIRD_IMAGE))  # Заглушка
    
    # Звуки
    try:
        assets["jump_sfx"] = pygame.mixer.Sound(JUMP_SOUND)
        assets["hit_sfx"] = pygame.mixer.Sound(HIT_SOUND)
        assets["point_sfx"] = pygame.mixer.Sound(POINT_SOUND)
    except pygame.error as e:
        print(f"Ошибка загрузки звуков: {e}")
        # Создаём пустые звуки
        assets["jump_sfx"] = pygame.mixer.Sound(buffer=b'\x00\x00' * 100)
        assets["hit_sfx"] = pygame.mixer.Sound(buffer=b'\x00\x00' * 100)
        assets["point_sfx"] = pygame.mixer.Sound(buffer=b'\x00\x00' * 100)
    
    return assets


class Bird(pygame.sprite.Sprite):
    """Класс птицы с улучшенной физикой"""
    
    def __init__(self, image):
        super().__init__()
        self.original_image = image
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)  # Маска для точных коллизий
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT // 2))
        self.velocity = 0
        self.angle = 0
        self.dead = False

    def update(self, noclip=False):
        if not self.dead:
            self.velocity += GRAVITY
            self.rect.y += self.velocity
            self.angle = max(ROTATE_DOWN, min(ROTATE_UP, self.velocity * -3))
        else:
            # Улучшенная физика падения после смерти
            self.velocity += GRAVITY * DEATH_GRAVITY_MULTIPLIER
            self.rect.y += self.velocity
            self.angle = max(ROTATE_DOWN, self.angle - ROTATION_SPEED)

        # Ограничение верхней границы
        if self.rect.y < 0:
            self.rect.y = 0
            self.velocity = 0

        # Вращение птицы
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        """Прыжок птицы"""
        self.velocity = BIRD_JUMP

    def die(self):
        """Смерть птицы"""
        self.dead = True

    def reset(self):
        """Сброс состояния птицы"""
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.velocity = 0
        self.angle = 0
        self.dead = False
        self.image = self.original_image
        self.mask = pygame.mask.from_surface(self.image)


class Pipe(pygame.sprite.Sprite):
    """Класс трубы с улучшенной системой подсчёта очков"""
    
    def __init__(self, image, x, y, is_bottom):
        super().__init__()
        self.original_image = image
        self.is_bottom = is_bottom
        self.passed = False
        
        if not is_bottom:
            self.image = pygame.transform.flip(image, False, True)
            self.rect = self.image.get_rect(midbottom=(x, y - PIPE_GAP // 2))
        else:
            self.image = image
            self.rect = self.image.get_rect(midtop=(x, y + PIPE_GAP // 2))
        
        self.mask = pygame.mask.from_surface(self.image)  # Маска для точных коллизий

    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.x < -self.rect.width:
            self.kill()


class Base:
    """Класс движущейся базы (земли)"""
    
    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(0, SCREEN_HEIGHT - BASE_HEIGHT))
        self.x = 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.rect.y))
        screen.blit(self.image, (self.x + self.image.get_width(), self.rect.y))

    def update(self):
        self.x -= BASE_SPEED
        if self.x <= -self.image.get_width():
            self.x = 0

    def reset(self):
        """Сброс позиции базы"""
        self.x = 0


class GameState:
    """Класс для хранения состояния игры"""
    
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.show_message = True
        self.noclip = False
        self.show_console = False
        self.console_input = ""
        self.show_fps = False
        self.last_pipe_time = 0
        self.pipe_interval = PIPE_SPAWN_INTERVAL


def handle_input(event, state, bird, assets):
    """Обработка ввода пользователя"""
    if event.type == pygame.KEYDOWN:
        # Консоль
        if event.key == pygame.K_BACKQUOTE:
            state.show_console = not state.show_console
            return
        
        if state.show_console:
            if event.key == pygame.K_RETURN:
                process_console_command(state.console_input, state, assets)
                state.console_input = ""
            elif event.key == pygame.K_BACKSPACE:
                state.console_input = state.console_input[:-1]
            else:
                state.console_input += event.unicode
        else:
            # Игровое управление
            if event.key == pygame.K_SPACE:
                if state.game_over:
                    return "reset"
                elif not state.show_message:
                    bird.jump()
                    assets["jump_sfx"].play()
                if state.show_message:
                    state.show_message = False
    
    elif event.type == pygame.MOUSEBUTTONDOWN and not state.show_console:
        if state.game_over:
            return "reset"
        elif not state.show_message:
            bird.jump()
            assets["jump_sfx"].play()
        if state.show_message:
            state.show_message = False
    
    return None


def process_console_command(command, state, assets):
    """Обработка команд консоли"""
    command = command.strip().lower()
    
    if command == "noclip":
        state.noclip = not state.noclip
        print(f"Noclip: {'ON' if state.noclip else 'OFF'}")
    
    elif command == "fps":
        state.show_fps = not state.show_fps
        print(f"FPS Display: {'ON' if state.show_fps else 'OFF'}")
    
    elif command.startswith("speed "):
        try:
            new_speed = int(command.split()[1])
            if 100 <= new_speed <= 5000:
                state.pipe_interval = new_speed
                print(f"Pipe interval set to {new_speed}ms")
            else:
                print("Speed must be between 100 and 5000")
        except (ValueError, IndexError):
            print("Usage: speed <milliseconds>")
    
    elif command == "help":
        print("\nAvailable commands:")
        print("  noclip - Toggle collision")
        print("  fps - Toggle FPS display")
        print("  speed <ms> - Set pipe spawn interval")
        print("  help - Show this message\n")
    
    elif command:
        print(f"Unknown command: {command}")


def update_game_state(state, bird, pipes, base, all_sprites, assets):
    """Обновление состояния игры"""
    if state.game_over or state.show_message:
        return
    
    # Обновление спрайтов
    for sprite in all_sprites:
        if isinstance(sprite, Bird):
            sprite.update(state.noclip)
        else:
            sprite.update()
    
    base.update()
    
    # Проверка столкновений с трубами (с использованием масок)
    if not state.noclip:
        if pygame.sprite.spritecollideany(bird, pipes, pygame.sprite.collide_mask):
            bird.die()
            assets["hit_sfx"].play()
            state.game_over = True
    
    # Проверка столкновения с землёй
    if bird.rect.y >= SCREEN_HEIGHT - BASE_HEIGHT - bird.rect.height:
        if not state.noclip and not bird.dead:
            bird.die()
            assets["hit_sfx"].play()
            bird.rect.y = SCREEN_HEIGHT - BASE_HEIGHT - bird.rect.height
            state.game_over = True
    
    # Подсчёт очков (улучшенная система - привязка к паре труб)
    for pipe in pipes:
        if not pipe.passed and pipe.rect.right < bird.rect.left:
            pipe.passed = True
            # Очко начисляется только для нижней трубы (чтобы не дублировать)
            if pipe.is_bottom:
                state.score += 1
                assets["point_sfx"].play()


def create_pipes(x, pipe_image):
    """Создание пары труб"""
    gap_y = random.randint(
        PIPE_GAP + PIPE_MIN_OFFSET,
        SCREEN_HEIGHT - PIPE_GAP - BASE_HEIGHT - PIPE_MIN_OFFSET
    )
    top_pipe = Pipe(pipe_image, x, gap_y, False)
    bottom_pipe = Pipe(pipe_image, x, gap_y, True)
    return top_pipe, bottom_pipe


def draw_game_state(screen, assets, state, bird, pipes, base, all_sprites, clock):
    """Отрисовка игры"""
    # Фон
    screen.blit(assets["background"], (0, 0))
    
    # Спрайты
    all_sprites.draw(screen)
    
    # База
    base.draw(screen)
    
    # Счёт
    draw_score(screen, assets, state.score)
    
    # Game Over экран
    if state.game_over:
        screen.blit(
            assets["game_over"],
            (SCREEN_WIDTH // 2 - GAME_OVER_WIDTH // 2,
             SCREEN_HEIGHT // 2 - GAME_OVER_HEIGHT // 2)
        )
    
    # Стартовое сообщение
    if state.show_message:
        screen.blit(
            assets["message"],
            (SCREEN_WIDTH // 2 - MESSAGE_WIDTH // 2,
             SCREEN_HEIGHT // 2 - MESSAGE_HEIGHT // 2)
        )
    
    # Консоль
    if state.show_console:
        pygame.draw.rect(
            screen,
            CONSOLE_BG_COLOR,
            (0, SCREEN_HEIGHT - CONSOLE_HEIGHT, SCREEN_WIDTH, CONSOLE_HEIGHT)
        )
        font = pygame.font.Font(None, CONSOLE_FONT_SIZE)
        console_text = font.render("> " + state.console_input, True, CONSOLE_TEXT_COLOR)
        screen.blit(console_text, (10, SCREEN_HEIGHT - CONSOLE_HEIGHT + 5))
    
    # FPS
    if state.show_fps:
        font = pygame.font.Font(None, FPS_FONT_SIZE)
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, FPS_COLOR)
        screen.blit(fps_text, FPS_POSITION)
    
    pygame.display.flip()


def draw_score(screen, assets, score):
    """Отрисовка счёта"""
    score_str = str(score)
    score_width = sum([assets["numbers"][int(digit)].get_width() for digit in score_str])
    x_offset = (SCREEN_WIDTH - score_width) / 2
    
    for digit in score_str:
        screen.blit(assets["numbers"][int(digit)], (x_offset, 20))
        x_offset += assets["numbers"][int(digit)].get_width()


def reset_game(state, bird, pipes, base, all_sprites):
    """Сброс игры без пересоздания объектов"""
    state.game_over = False
    state.show_message = False
    state.score = 0
    state.last_pipe_time = 0
    
    # Очищаем трубы
    pipes.empty()
    
    # Пересоздаём группу спрайтов
    all_sprites.empty()
    all_sprites.add(bird)
    
    # Сброс состояния объектов
    bird.reset()
    base.reset()


def main():
    """Главная функция игры"""
    # Инициализация
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird - Improved')
    clock = pygame.time.Clock()
    
    # Загрузка ресурсов
    print("Loading assets...")
    assets = load_assets()
    print("Assets loaded successfully!")
    
    # Создание игровых объектов
    bird = Bird(assets["bird"])
    all_sprites = pygame.sprite.Group()
    all_sprites.add(bird)
    pipes = pygame.sprite.Group()
    base = Base(assets["base"])
    state = GameState()
    
    # Главный игровой цикл
    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                action = handle_input(event, state, bird, assets)
                if action == "reset":
                    reset_game(state, bird, pipes, base, all_sprites)
        
        # Спавн труб (с использованием get_ticks вместо таймера)
        current_time = pygame.time.get_ticks()
        if not state.game_over and not state.show_message:
            if current_time - state.last_pipe_time > state.pipe_interval:
                top_pipe, bottom_pipe = create_pipes(SCREEN_WIDTH, assets["pipe"])
                pipes.add(top_pipe, bottom_pipe)
                all_sprites.add(top_pipe, bottom_pipe)
                state.last_pipe_time = current_time
        
        # Обновление игры
        update_game_state(state, bird, pipes, base, all_sprites, assets)
        
        # Отрисовка
        draw_game_state(screen, assets, state, bird, pipes, base, all_sprites, clock)
        
        # Ограничение FPS
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()
