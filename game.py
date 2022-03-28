import time

import pygame
import random
import os
import sys

# 常量
# 背景图宽， 高
W, H = 288, 512
# 游戏帧率
FPS = 30

# setup 设置
pygame.init()

SCREEN = pygame.display.set_mode((W, H))

pygame.display.set_caption('现象级3A大作-By ACE')

CLOCK = pygame.time.Clock()

# bird
IMAGES = {}
for image in os.listdir('.'):
    name, extension = os.path.splitext(image)
    path = os.path.join('.', image)
    if extension == '.png':
        IMAGES[name] = pygame.image.load(path)

# bird_yellow_up = pygame.image.load('flappybird/bird0_0.png')
# bird_yellow_mid = pygame.image.load('flappybird/bird0_1.png')
# bird_yellow_down = pygame.image.load('flappybird/bird0_2.png')
# bird_blue_up = pygame.image.load('flappybird/bird1_0.png')
# bird_blue_mid = pygame.image.load('flappybird/bird1_1.png')
# bird_blue_down = pygame.image.load('flappybird/bird1_2.png')
# bird_red_up = pygame.image.load('flappybird/bird2_0.png')
# bird_red_mid = pygame.image.load('flappybird/bird2_1.png')
# bird_red_down = pygame.image.load('flappybird/bird2_2.png')


FLOOR_Y = H - IMAGES['land'].get_height()

AUDIOS = {}
for audio in os.listdir('.'):
    name, extension = os.path.splitext(audio)
    if extension in ['.mp3', '.wav']:
        AUDIOS[name] = pygame.mixer.Sound(audio)


# start_music = pygame.mixer.Sound('hero.mp3')
# die = pygame.mixer.Sound('碰撞音.wav')
# hit = pygame.mixer.Sound('飞.wav')
# score = pygame.mixer.Sound('提示音.wav')


def main():
    AUDIOS['hero'].play()

    while True:
        IMAGES['bgpic'] = IMAGES[random.choice(['bg_day', 'bg_night'])]
        color = random.choice(['bird0', 'bird1', 'bird2'])
        IMAGES['birds'] = [IMAGES[color + '_0'], IMAGES[color + '_1'], IMAGES[color + '_2']]
        pipe = IMAGES[random.choice(['pipe_up', 'pipe2_up'])]
        IMAGES['pipes'] = [pipe, pygame.transform.flip(pipe, False, True)]
        menu_window()
        result = game_window()
        end_window(result)


def menu_window():
    floor_gap = IMAGES['land'].get_width() - W
    floor_x = 0

    guide_text_x = (W - IMAGES['text_ready'].get_width()) / 2
    guide_text_y = (FLOOR_Y - IMAGES['text_ready'].get_height()) / 2

    game_name_x = (W - IMAGES['title'].get_width()) / 2
    game_name_y = guide_text_y / 2

    guide_hand_x = (W - IMAGES['tutorial'].get_width()) / 2
    guide_hand_y = guide_text_y + (FLOOR_Y - guide_text_y) / 2

    bird_x = W * 0.2
    bird_y = (H - IMAGES['bird2_0'].get_height()) / 2

    bird_y_vel = 1
    bird_y_range = [bird_y - 8, bird_y + 8]

    idx = 0
    repeat = 5
    frames = [0] * repeat + [1] * repeat + [2] * repeat + [1] * repeat
    # frames = [0,0,0,0,0,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

        bird_y += bird_y_vel

        if bird_y < bird_y_range[0] or bird_y > bird_y_range[1]:
            bird_y_vel *= -1

        floor_x -= 4
        if floor_x <= -floor_gap:
            floor_x = 0

        idx += 1
        idx %= len(frames)

        SCREEN.blit(IMAGES['bgpic'], (0, 0))
        SCREEN.blit(IMAGES['land'], (floor_x, FLOOR_Y))
        SCREEN.blit(IMAGES['text_ready'], (guide_text_x, guide_text_y))
        SCREEN.blit(IMAGES['title'], (game_name_x, game_name_y))
        SCREEN.blit(IMAGES['tutorial'], (guide_hand_x, guide_hand_y))
        SCREEN.blit(IMAGES['birds'][frames[idx]], (bird_x, bird_y))
        pygame.display.update()

        CLOCK.tick(FPS)


def game_window():
    score = 0
    AUDIOS['fly'].play()
    floor_gap = IMAGES['land'].get_width() - W
    floor_x = 0

    # frames = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]

    bird = Bird(W * 0.2, H * 0.4)

    distance = 150
    pipe_gap = 100

    n = 4
    # pipes = []
    pipe_group = pygame.sprite.Group()
    for i in range(n):
        pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
        pipe_up = Pipe(W + i * distance, pipe_y, True)
        pipe_down = Pipe(W + i * distance, pipe_y - pipe_gap, False)

        pipe_group.add(pipe_up)
        pipe_group.add(pipe_down)

    # pipe = Pipe(W, H*0.5)

    while True:
        flap = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    flap = True
                    AUDIOS['fly'].play()

        floor_x -= 4
        if floor_x <= -floor_gap:
            floor_x = 0

        bird.update(flap)

        first_pipe_up = pipe_group.sprites()[0]
        first_pipe_down = pipe_group.sprites()[1]
        if first_pipe_up.rect.right < 0:
            pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
            new_pipe_up = Pipe(first_pipe_up.rect.x + n * distance, pipe_y, True)
            new_pipe_down = Pipe(first_pipe_down.rect.x + n * distance, pipe_y - pipe_gap, False)
            pipe_group.add(new_pipe_up)
            pipe_group.add(new_pipe_down)
            first_pipe_up.kill()
            first_pipe_down.kill()

        pipe_group.update()

        if bird.rect.y > FLOOR_Y or bird.rect.y < 0 or pygame.sprite.spritecollideany(bird, pipe_group):
            bird.dying = True
            AUDIOS['die'].play()
            result = {'bird': bird, 'pipe_group': pipe_group, 'score': score}
            return result

        if bird.rect.left + first_pipe_up.x_vel < first_pipe_up.rect.centerx < bird.rect.left:
            AUDIOS['hit'].play()
            score += 1

        # for pipe in pipe_group.sprites():
        #     right_to_left = max(bird.rect.right, pipe.rect.right) - min(bird.rect.left, pipe.rect.left)
        #     bottom_to_top = max(bird.rect.bottom, pipe.rect.bottom) - min(bird.rect.top, pipe.rect.top)
        #     if right_to_left < bird.rect.width + pipe.rect.width and bottom_to_top < bird.rect.height + pipe.rect.height:
        #         AUDIOS['hit'].play()
        #         AUDIOS['die'].play()
        #         result = {'bird': bird, 'pipe_group': pipe_group}
        #         return result

        SCREEN.blit(IMAGES['bgpic'], (0, 0))
        pipe_group.draw(SCREEN)
        show_score(score)
        SCREEN.blit(IMAGES['land'], (floor_x, FLOOR_Y))
        SCREEN.blit(bird.image, bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)


def end_window(result):
    gameover_x = (W - IMAGES['text_game_over'].get_width()) / 2
    gameover_y = (FLOOR_Y - IMAGES['text_game_over'].get_height()) / 2

    bird = result['bird']
    pipe_group = result['pipe_group']
    while True:

        if bird.dying:
            bird.go_die()

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return

        SCREEN.blit(IMAGES['bgpic'], (0, 0))
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGES['land'], (0, FLOOR_Y))

        show_score(result['score'])

        SCREEN.blit(IMAGES['text_game_over'], (gameover_x, gameover_y))
        SCREEN.blit(bird.image, bird.rect)
        pygame.display.update()

        CLOCK.tick(FPS)


def show_score(score):
    score_str = str(score)
    n = len(score_str)
    w = IMAGES['number_score_00'].get_width()
    x = (W - n * w) / 2
    y = H * 0.1
    for number in score_str:
        SCREEN.blit(IMAGES['number_score_0' + str(number)], (x, y))
        x += w


class Bird:
    def __init__(self, x, y):
        self.frames = [0] * 5 + [1] * 5 + [2] * 5 + [1] * 5
        self.idx = 0
        self.image = IMAGES['birds'][self.frames[self.idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y_vel = -10
        self.max_y_vel = 10
        self.gravity = 1
        self.rotate = 45
        self.max_rotate = -20
        self.rotate_vel = -3
        self.y_vel_after_flap = -10
        self.rotate_after_flap = 45
        self.dying = False

    def update(self, flap=False):
        if flap:
            self.y_vel = self.y_vel_after_flap
            self.rotate = self.rotate_after_flap

        self.y_vel = min(self.y_vel + self.gravity, self.max_y_vel)
        self.rect.y += self.y_vel
        self.rotate = max(self.rotate + self.rotate_vel, self.max_rotate)
        self.idx += 1
        self.idx %= len(self.frames)
        self.image = IMAGES['birds'][self.frames[self.idx]]

        self.image = pygame.transform.rotate(self.image, self.rotate)

    def go_die(self):
        if self.rect.y < FLOOR_Y:
            self.rect.y += self.max_y_vel
            self.rotate = -90
            self.image = IMAGES['birds'][self.frames[self.idx]]
            self.image = pygame.transform.rotate(self.image, self.rotate)
        else:
            self.dying = False


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, upwards=True):
        pygame.sprite.Sprite.__init__(self)
        if upwards:
            self.image = IMAGES['pipes'][0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.top = y
        else:
            self.image = IMAGES['pipes'][1]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
        self.x_vel = -4

    def update(self):
        self.rect.x += self.x_vel


if __name__ == '__main__':
    main()
