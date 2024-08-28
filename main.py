import pygame
import os
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


ASSET_PATH = os.path.join(os.path.dirname(__file__), 'assets')
BACKGROUND_IMG = pygame.image.load(os.path.join(ASSET_PATH, 'background.png'))
ROCKET_IMG = pygame.image.load(os.path.join(ASSET_PATH, 'rocket.png'))
BULLET_IMG = pygame.image.load(os.path.join(ASSET_PATH, 'bullet.png'))
ALIEN_IMG = pygame.image.load(os.path.join(ASSET_PATH, 'alien_ship.png'))
BACKGROUND_MUSIC = os.path.join(ASSET_PATH, 'spaceinvaders1.mpeg')
SHOOT_SOUND = pygame.mixer.Sound(os.path.join(ASSET_PATH, 'shoot.wav'))
INVADER_KILLED_SOUND = pygame.mixer.Sound(os.path.join(ASSET_PATH, 'invaderkilled.wav'))


BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (SCREEN_WIDTH, SCREEN_HEIGHT))
ROCKET_IMG = pygame.transform.scale(ROCKET_IMG, (60, 90))
BULLET_IMG = pygame.transform.scale(BULLET_IMG, (15, 30))
ALIEN_IMG = pygame.transform.scale(ALIEN_IMG, (50, 40))


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")


pygame.mixer.music.load(BACKGROUND_MUSIC)
pygame.mixer.music.play(-1)  


clock = pygame.time.Clock()
FPS = 60


rocket_speed = 5
bullet_speed = 10
alien_speed = 4  
score = 0
level = 1
sound_on = True
resume_game = False  


class Rocket:
    def __init__(self):
        self.image = ROCKET_IMG
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.speed = rocket_speed

    def move(self, direction):
        if direction == 'left' and self.rect.left > 0:
            self.rect.x -= self.speed
        if direction == 'right' and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


class Bullet:
    def __init__(self, x, y):
        self.image = BULLET_IMG
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = bullet_speed

    def move(self):
        self.rect.y -= self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


class Alien:
    def __init__(self, x, y, speed):
        self.image = ALIEN_IMG
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.direction = 1

    def move(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1
            self.rect.y += 20  

    def draw(self):
        screen.blit(self.image, self.rect)


def create_aliens():
    aliens = []
    for i in range(20): 
        x = random.randint(0, SCREEN_WIDTH - 50)
        y = random.randint(50, 150)
        aliens.append(Alien(x, y, alien_speed))
    return aliens


def check_collision(bullets, aliens):
    global score
    bullets_to_remove = []
    aliens_to_remove = []
    for bullet in bullets:
        for alien in aliens:
            if bullet.rect.colliderect(alien.rect):
                bullets_to_remove.append(bullet)
                aliens_to_remove.append(alien)
                score += 1
                INVADER_KILLED_SOUND.play()
    
    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)
    for alien in aliens_to_remove:
        if alien in aliens:
            aliens.remove(alien)


def draw_menu_button():
    menu_button = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 50, 80, 40)
    pygame.draw.rect(screen, WHITE, menu_button)
    font = pygame.font.SysFont(None, 24)
    menu_text = font.render("Menu", True, BLACK)
    screen.blit(menu_text, (SCREEN_WIDTH - 85, SCREEN_HEIGHT - 45))
    return menu_button


def handle_menu():
    global sound_on, resume_game
    menu_running = True
    while menu_running:
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 36)
        resume_text = font.render("Resume", True, WHITE)
        exit_text = font.render("Exit", True, WHITE)
        score_text = font.render(f"High Score: {score}", True, WHITE)
        mute_text = font.render("Mute" if sound_on else "Unmute", True, WHITE)
        
        resume_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 3 - 60, 100, 50)
        exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 3, 100, 50)
        score_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 3 + 60, 200, 50)
        mute_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 3 + 120, 100, 50)
        
        pygame.draw.rect(screen, WHITE, resume_rect, 2)
        pygame.draw.rect(screen, WHITE, exit_rect, 2)
        pygame.draw.rect(screen, WHITE, score_rect, 2)
        pygame.draw.rect(screen, WHITE, mute_rect, 2)

        screen.blit(resume_text, (resume_rect.x + 5, resume_rect.y + 10))
        screen.blit(exit_text, (exit_rect.x + 20, exit_rect.y + 10))
        screen.blit(score_text, (score_rect.x + 20, score_rect.y + 10))
        screen.blit(mute_text, (mute_rect.x + 20, mute_rect.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_rect.collidepoint(event.pos):
                    resume_game = True
                    return  
                elif exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif mute_rect.collidepoint(event.pos):
                    sound_on = not sound_on
                    if sound_on:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                elif score_rect.collidepoint(event.pos):
                    pass 

        pygame.display.flip()
        clock.tick(FPS)


def game_loop():
    global level, menu_button, resume_game
    rocket = Rocket()
    bullets = []
    aliens = create_aliens()
    game_running = True

    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(Bullet(rocket.rect.centerx, rocket.rect.top))
                    if sound_on:
                        SHOOT_SOUND.play()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.collidepoint(event.pos):
                    resume_game = False
                    handle_menu()
                    if resume_game:
                        continue  

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            rocket.move('left')
        if keys[pygame.K_RIGHT]:
            rocket.move('right')


        for bullet in bullets:
            bullet.move()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)


        for alien in aliens:
            alien.move()
            if alien.rect.top > SCREEN_HEIGHT:
                game_running = False  

      
        check_collision(bullets, aliens)

  
        if not aliens:
            level += 1
            aliens = create_aliens()

        
        screen.blit(BACKGROUND_IMG, (0, 0))
        rocket.draw()
        for bullet in bullets:
            bullet.draw()
        for alien in aliens:
            alien.draw()

        
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        level_text = font.render(f'Level: {level}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))

        
        menu_button = draw_menu_button()

        pygame.display.flip()
        clock.tick(FPS)


def start_menu():
    while True:
        screen.blit(BACKGROUND_IMG, (0, 0))
        font = pygame.font.SysFont(None, 72)
        title_text = font.render("SPACE INVADERS", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))

        play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50)
        pygame.draw.rect(screen, WHITE, play_button, 2)
        play_text = font.render("Play", True, WHITE)
        screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, SCREEN_HEIGHT // 2 - play_text.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return

        pygame.display.flip()
        clock.tick(FPS)


start_menu()
game_loop()




