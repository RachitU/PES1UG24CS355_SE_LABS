import pygame
import random
from .player import Player
from .enemy import EnemyGrid
from .bullet import Bullet
from .sounds import Sounds

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
YELLOW = (240, 220, 80)

# Enemy speed / fire rate per difficulty.
# fire_chance is per enemy, per frame (a full 32-enemy grid at 0.0006 ~ 1 shot/sec).
DIFFICULTIES = {
    "Easy":   {"speed": 1.0, "fire_chance": 0.0003},
    "Medium": {"speed": 1.5, "fire_chance": 0.0006},
    "Hard":   {"speed": 2.5, "fire_chance": 0.0012},
}

# Game states
PLAYING, GAME_OVER, DIFFICULTY_SELECT = "playing", "game_over", "difficulty_select"


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.sounds = Sounds()
        self.quit_requested = False
        self.reset("Medium")

    def reset(self, difficulty):
        """Start a fresh round at the given difficulty."""
        self.difficulty = difficulty
        settings = DIFFICULTIES[difficulty]

        self.player = Player(self.width // 2 - 20, self.height - 50, 40, 20)
        self.enemy_grid = EnemyGrid(self.width, speed=settings["speed"])

        self.player_bullets = []
        self.enemy_bullets = []
        self._shoot_cooldown = 0
        self.enemy_fire_chance = settings["fire_chance"]

        self.score = 0
        self.state = PLAYING
        self.won = False

    @property
    def game_over(self):
        return self.state != PLAYING

    def _end_game(self, won=False):
        self.state = GAME_OVER
        self.won = won
        self.sounds.play("game_over")

    # ---------- input ----------
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.state == PLAYING:
            if event.key == pygame.K_SPACE and self._shoot_cooldown <= 0:
                bullet_x = self.player.center_x() - 2
                self.player_bullets.append(Bullet(bullet_x, self.player.y, direction=-1))
                self._shoot_cooldown = 15
                self.sounds.play("shoot")

        elif self.state == GAME_OVER:
            if event.key == pygame.K_r:
                self.state = DIFFICULTY_SELECT
            elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                self.quit_requested = True

        elif self.state == DIFFICULTY_SELECT:
            choice = {
                pygame.K_1: "Easy", pygame.K_e: "Easy",
                pygame.K_2: "Medium", pygame.K_m: "Medium",
                pygame.K_3: "Hard", pygame.K_h: "Hard",
            }.get(event.key)
            if choice:
                self.reset(choice)
            elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                self.quit_requested = True

    def handle_input(self):
        if self.state != PLAYING:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-self.player.speed, self.width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(self.player.speed, self.width)

    # ---------- update ----------
    def update(self):
        if self.state != PLAYING:
            return

        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

        self.enemy_grid.move()

        for enemy in self.enemy_grid.alive_enemies():
            if random.random() < self.enemy_fire_chance:
                bullet_x = enemy.x + enemy.width // 2
                self.enemy_bullets.append(Bullet(bullet_x, enemy.y + enemy.height, direction=1))

        for bullet in self.player_bullets:
            bullet.move()
        for bullet in self.enemy_bullets:
            bullet.move()

        self.player_bullets = [b for b in self.player_bullets if not b.off_screen(self.height)]
        self.enemy_bullets = [b for b in self.enemy_bullets if not b.off_screen(self.height)]

        # Collision: build a new list of surviving bullets instead of removing
        # from the list we're iterating (that skipped elements before), and use
        # each bullet's swept rect so it can't tunnel through an enemy between
        # frames. One bullet kills at most one enemy.
        surviving = []
        for bullet in self.player_bullets:
            hit_rect = bullet.swept_rect()
            hit = None
            for enemy in self.enemy_grid.alive_enemies():
                if hit_rect.colliderect(enemy.rect()):
                    # If the sweep touches several enemies, take the lowest one
                    # (the one the bullet reaches first).
                    if hit is None or enemy.y > hit.y:
                        hit = enemy
            if hit is not None:
                hit.alive = False
                self.score += 1
                self.sounds.play("explosion")
            else:
                surviving.append(bullet)
        self.player_bullets = surviving

        player_rect = self.player.rect()
        for bullet in self.enemy_bullets:
            if bullet.swept_rect().colliderect(player_rect):
                self._end_game()
                return

        if self.enemy_grid.reached_bottom(self.player.y):
            self._end_game()
            return

        if not self.enemy_grid.alive_enemies():
            self._end_game(won=True)

    # ---------- render ----------
    def _center_text(self, screen, font, text, y, color=WHITE):
        surf = font.render(text, True, color)
        screen.blit(surf, (self.width // 2 - surf.get_width() // 2, y))

    def render(self, screen):
        if self.state == DIFFICULTY_SELECT:
            self._center_text(screen, self.big_font, "Select Difficulty", 200, YELLOW)
            self._center_text(screen, self.font, "1 / E  -  Easy", 320)
            self._center_text(screen, self.font, "2 / M  -  Medium", 370)
            self._center_text(screen, self.font, "3 / H  -  Hard", 420)
            self._center_text(screen, self.small_font, "Q / Esc  -  Quit", 500)
            return

        pygame.draw.rect(screen, GREEN, self.player.rect())

        for enemy in self.enemy_grid.alive_enemies():
            pygame.draw.rect(screen, WHITE, enemy.rect())

        for bullet in self.player_bullets:
            pygame.draw.rect(screen, WHITE, bullet.rect())
        for bullet in self.enemy_bullets:
            pygame.draw.rect(screen, RED, bullet.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        diff_text = self.small_font.render(self.difficulty, True, YELLOW)
        screen.blit(diff_text, (self.width - diff_text.get_width() - 10, 14))

        if self.state == GAME_OVER:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            title = "YOU WIN!" if self.won else "GAME OVER"
            self._center_text(screen, self.big_font, title, 220, GREEN if self.won else RED)
            self._center_text(screen, self.font, f"Final Score: {self.score}", 310)
            self._center_text(screen, self.small_font, "R  -  Play again", 390)
            self._center_text(screen, self.small_font, "Q / Esc  -  Quit", 430)
