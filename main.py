import pygame
import random

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
BIRD_JUMP = -6.0
PIPE_GAP = 150
PIPE_WIDTH = 52
PIPE_HEIGHT = 500
BASE_HEIGHT = 133
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
GAME_OVER_WIDTH = 192
GAME_OVER_HEIGHT = 42
MESSAGE_WIDTH = 184
MESSAGE_HEIGHT = 267
ROTATE_UP = 25
ROTATE_DOWN = -90
FPS = 60

# Загрузка ресурсов
BACKGROUND = pygame.transform.scale(pygame.image.load('assets/background.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
BIRD_IMG = pygame.transform.scale(pygame.image.load('assets/bird.png'), (BIRD_WIDTH, BIRD_HEIGHT))
PIPE_IMG = pygame.transform.scale(pygame.image.load('assets/pipe.png'), (PIPE_WIDTH, PIPE_HEIGHT))
BASE_IMG = pygame.transform.scale(pygame.image.load('assets/base.png'), (SCREEN_WIDTH, BASE_HEIGHT))
GAME_OVER_IMG = pygame.transform.scale(pygame.image.load('assets/gameover.png'), (GAME_OVER_WIDTH, GAME_OVER_HEIGHT))
MESSAGE_IMG = pygame.transform.scale(pygame.image.load('assets/message.png'), (MESSAGE_WIDTH, MESSAGE_HEIGHT))

NUMBERS = [pygame.image.load(f'assets/{i}.png') for i in range(10)]

JUMP_SFX = pygame.mixer.Sound('assets/jump.wav')
HIT_SFX = pygame.mixer.Sound('assets/hit.wav')
POINT_SFX = pygame.mixer.Sound('assets/point.wav')

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')


class Bird(pygame.sprite.Sprite):
    def __init__(self, noclip):
        super().__init__()
        self.image = BIRD_IMG
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT // 2))
        self.velocity = 0
        self.angle = 0
        self.dead = False
        self.noclip = noclip

    def update(self):
        if not self.dead:
            self.velocity += GRAVITY
            self.rect.y += self.velocity
            self.angle = max(ROTATE_DOWN, min(ROTATE_UP, self.velocity * -3))
        elif self.rect.y < SCREEN_HEIGHT - BASE_HEIGHT - self.rect.height:
            self.velocity += GRAVITY
            self.rect.y += self.velocity
            self.angle = ROTATE_DOWN

        if self.rect.y < 0:
            self.rect.y = 0
            self.velocity = 0

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def jump(self):
        self.velocity = BIRD_JUMP
        JUMP_SFX.play()

    def die(self):
        if not self.noclip:
            self.dead = True
            HIT_SFX.play()


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, is_bottom):
        super().__init__()
        self.image = PIPE_IMG
        self.passed = False
        if not is_bottom:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midbottom=(x, y - PIPE_GAP // 2))
        else:
            self.rect = self.image.get_rect(midtop=(x, y + PIPE_GAP // 2))

    def update(self):
        self.rect.x -= 3
        if self.rect.x < -self.rect.width:
            self.kill()


class Base:
    def __init__(self):
        self.image = BASE_IMG
        self.rect = self.image.get_rect(topleft=(0, SCREEN_HEIGHT - BASE_HEIGHT))
        self.x = 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.rect.y))
        screen.blit(self.image, (self.x + self.image.get_width(), self.rect.y))

    def update(self):
        self.x -= 3
        if self.x <= -self.image.get_width():
            self.x = 0


def main():
    clock = pygame.time.Clock()
    noclip = False
    bird = Bird(noclip)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(bird)
    pipes = pygame.sprite.Group()
    base = Base()
    score = 0
    show_console = False
    input_text = ""

    def create_pipe():
        gap = PIPE_GAP
        min_pipe_y = gap + 50
        max_pipe_y = SCREEN_HEIGHT - gap - BASE_HEIGHT - 50
        y = random.randint(min_pipe_y, max_pipe_y) if min_pipe_y <= max_pipe_y else (SCREEN_HEIGHT - BASE_HEIGHT) // 2
        top_pipe = Pipe(SCREEN_WIDTH, y, False)
        bottom_pipe = Pipe(SCREEN_WIDTH, y, True)
        pipes.add(top_pipe, bottom_pipe)
        all_sprites.add(top_pipe, bottom_pipe)

    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1500)

    game_over = False
    show_message = True

    def reset_game():
        nonlocal bird, all_sprites, pipes, base, game_over, show_message, score
        game_over = False
        show_message = False
        score = 0
        bird = Bird(noclip)
        all_sprites = pygame.sprite.Group()
        all_sprites.add(bird)
        pipes = pygame.sprite.Group()
        base = Base()
        pygame.time.set_timer(SPAWNPIPE, 1500)

    def show_game_over():
        screen.blit(GAME_OVER_IMG, (SCREEN_WIDTH // 2 - GAME_OVER_WIDTH // 2, SCREEN_HEIGHT // 2 - GAME_OVER_HEIGHT // 2))

    def show_message_screen():
        screen.blit(MESSAGE_IMG, (SCREEN_WIDTH // 2 - MESSAGE_WIDTH // 2, SCREEN_HEIGHT // 2 - MESSAGE_HEIGHT // 2))

    def draw_score():
        score_str = str(score)
        score_width = sum([NUMBERS[int(digit)].get_width() for digit in score_str])
        x_offset = (SCREEN_WIDTH - score_width) / 2
        for digit in score_str:
            screen.blit(NUMBERS[int(digit)], (x_offset, 20))
            x_offset += NUMBERS[int(digit)].get_width()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKQUOTE: 
                    show_console = not show_console
                elif event.key == pygame.K_RETURN:
                    if show_console:
                        input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    if show_console:
                        input_text = input_text[:-1]
                else:
                    if show_console:
                        input_text += event.unicode
                    else:
                        if event.key == pygame.K_SPACE:
                            if game_over:
                                reset_game()
                            elif not show_message:
                                bird.jump()
                            if show_message:
                                show_message = False
                                pygame.time.set_timer(SPAWNPIPE, 1500)
            if event.type == pygame.MOUSEBUTTONDOWN and not show_console:
                if game_over:
                    reset_game()
                elif not show_message:
                    bird.jump()
                if show_message:
                    show_message = False
                    pygame.time.set_timer(SPAWNPIPE, 1500)
            if event.type == SPAWNPIPE and not game_over and not show_message:
                create_pipe()

        if not game_over and not show_message:
            all_sprites.update()
            base.update()

            # Оптимизация: Проверка столкновений только когда это действительно нужно
            if pygame.sprite.spritecollideany(bird, pipes, pygame.sprite.collide_mask):
                bird.die()
                game_over = True

            if bird.rect.y >= SCREEN_HEIGHT - BASE_HEIGHT - bird.rect.height and not bird.dead:
                bird.die()
                bird.rect.y = SCREEN_HEIGHT - BASE_HEIGHT - bird.rect.height
                game_over = True

            for pipe in pipes:
                if pipe.rect.right < bird.rect.left and not pipe.passed:
                    pipe.passed = True
                    if pipe.rect.bottom > SCREEN_HEIGHT // 2:
                        score += 1
                        POINT_SFX.play()

        # Отрисовка элементов
        screen.blit(BACKGROUND, (0, 0))
        all_sprites.draw(screen)
        base.draw(screen)
        draw_score()

        if game_over:
            show_game_over()
        if show_message:
            show_message_screen()

        if show_console:
            pygame.draw.rect(screen, (0, 0, 0), (0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30))
            font = pygame.font.Font(None, 30)
            console_text = font.render(input_text, True, (255, 255, 255))
            screen.blit(console_text, (10, SCREEN_HEIGHT - 25))

        pygame.display.flip()
        clock.tick(FPS)  # Ограничение FPS до 60

    pygame.quit()

if __name__ == "__main__":
    main()
