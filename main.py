import os
import sys

import pygame
import random

colours_of_blocks = [
    (0, 0, 0),
    (113, 9, 170),
    (18, 10, 143),
    (75, 0, 130),
    (61, 40, 181),
    (173, 0, 95),
    (74, 60, 181),
    (179, 36, 86),
    (219, 92, 72)
]


# Класс блоков, отвечает за вид блока и его повороты
class Block:
    x = 0
    y = 0
    # Список видов блоков: списки определяют сам блок, а вложенные в них определяют положение при поворотах блока
    kinds_of_blocks = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Определяем цвет блока
        self.colour_of_one_block = random.randint(1, len(colours_of_blocks) - 1)
        # Определяем вид блока
        self.kind_of_one_block = random.randint(0, len(self.kinds_of_blocks) - 1)
        # Начальный поворот блока(первый вложенный список в списке вида блока)
        self.rotation = 0

    # Функция, которая возвращает текущее вид и положение блока
    def get_current_block(self):
        return self.kinds_of_blocks[self.kind_of_one_block][self.rotation]

    # Поворот блока
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.kinds_of_blocks[self.kind_of_one_block])


# Создаём переменную которая будет хранить рекорд пользователя(она понадобится, чтобы выводить рекорд на экран)
# Открываем текстовый файл с рекордом предыдущих игр
with open('scores.txt', 'r') as f:
    lines = f.readlines()
    old_record = lines[0].strip()
    record_of_all_games = old_record


# Класс, отвечающий за уровни, очки, рекорды, первижение блоков, заполненные линии, касания блоков с другими элементами
# поля, в общем за всю логику игры
class Tetris:
    # Уровень игры(от него зависит начальная скорость блоков)
    level = 1
    # Количество разрушенных линий
    number_of_all_ruined_lines = 0
    # Поле игры. Будет содержать нули, если клетка пуста, и цвет, если нет.
    pole = []
    # Высота и ширина поля(измеряется в количестве клеток в нём). Т.е. поле в нашей игре высотой 20 клеток, шириной 10
    height, width = 20, 10
    # Координаты верхнего левого угла поля
    x, y = 160, 30
    coefficient_of_size = 22
    # Очки за игру(определяются по разрушенным линиям)
    score = 0
    # Состояние игры(начало либо конец)
    condition = "начало"
    one_block = None

    def __init__(self):
        self.pole = []
        self.score = 0
        self.condition = "начало"
        # Заполняем поле нулями
        for i in range(self.height):
            new_line = []
            for j in range(self.width):
                new_line.append(0)
            self.pole.append(new_line)

    # Создание новых блоков
    def new_block(self):
        self.one_block = Block(3, 0)

    # Функция, которая проверяет касается ли блок других блоков или краёв поля
    def get_touching_others_blocks_or_not(self):
        touching = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.one_block.get_current_block():
                    if i + self.one_block.y > self.height - 1 or \
                            j + self.one_block.x > self.width - 1 or \
                            j + self.one_block.x < 0 or \
                            self.pole[i + self.one_block.y][j + self.one_block.x] > 0:
                        touching = True
        return touching

    # Функция, проверяющая заполненны ли какие-то линни на игровом поле
    def ruin_line(self):
        ruined_lines = 0
        for i in range(1, self.height):
            # Считаем кол-во пустых клеток в линии
            empty_kletki = 0
            for j in range(self.width):
                if self.pole[i][j] == 0:
                    empty_kletki += 1
            # Если пустых клеток в линии нет, то увеличиваем переменную number_of_all_ruined_lines,
            # которая отвечает за переход на новый уровень и меняем расположение всех блоков
            if empty_kletki == 0:
                ruined_lines += 1
                self.number_of_all_ruined_lines += 1
                for i_1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.pole[i_1][j] = self.pole[i_1 - 1][j]
                # Засчисляем очки игроку
                self.score += ruined_lines * self.level
                # Обновяем рекорд всей игры
                self.update_record()
                # Если количество разрушенных линий является 10, то игрок переходит на другой уровень
                # (скорость блоков увеличивается)
                if self.number_of_all_ruined_lines == 10:
                    self.level += 1
                    self.score = 0
                    self.number_of_all_ruined_lines = 0
                    # В игре всего 12 уровней, так что когда уровень становится 13,
                    # мы изменяем состояние игры на "пройдена"
                    if self.level == 13:
                        self.condition = "пройдена"

    def update_record(self):
        global record_of_all_games
        # Если игрок достиг нового рекорда обновляем старый - открываем текстовый файл с рекордом
        with open('scores.txt', 'r') as f:
            lines = f.readlines()
            old_record = lines[0].strip()
        with open('scores.txt', 'w') as f:
            if self.score > int(old_record):
                f.write(str(self.score))
                record_of_all_games = self.score
            else:
                f.write(str(record_of_all_games))

    # Функция, которая передвигает блок вниз сразу, пока он чего-то не коснётся (вызывается нажатием на клавишу space)
    def move_down_until_touch_smth(self):
        while not self.get_touching_others_blocks_or_not():
            self.one_block.y += 1
        self.one_block.y -= 1
        self.stop_and_set_block()

    # Функция, которая передвигает блок вниз, пока игрок зажимает page down)
    def move_down_simple(self):
        self.one_block.y += 1
        if self.get_touching_others_blocks_or_not():
            self.one_block.y -= 1
            self.stop_and_set_block()

    def stop_and_set_block(self):
        # Функция, которая останавливает блок, когда он коснулся другого блока или края поля
        # А также закрепляет за ним эту позицию, закрашивая клетку, т.е. меняя ноль на цвет блока
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.one_block.get_current_block():
                    self.pole[i + self.one_block.y][j + self.one_block.x] = self.one_block.colour_of_one_block
        # Проверяем есть ли заполненные линии, которые можно разрушить
        self.ruin_line()
        # Создаём новый блок; если он сразу касается с другим блоком, меняем состояние игры
        self.new_block()
        if self.get_touching_others_blocks_or_not():
            self.condition = "конец"

    # Функция, которая передвигает блок вправо или влево, смотря на какую клавишу наживает игрок: page left или right)
    def move_to_the_side(self, which_side):
        previous_coord_of_x = self.one_block.x
        self.one_block.x += which_side
        if self.get_touching_others_blocks_or_not():
            self.one_block.x = previous_coord_of_x

    # Функция, которая поворачивает блок, когда игрок нажимает на page up)
    def rotate(self):
        previous_coord_of_x = self.one_block.rotation
        self.one_block.rotate()
        if self.get_touching_others_blocks_or_not():
            self.one_block.rotation = previous_coord_of_x


# Игровой цикл
pygame.init()
pygame.mixer.init()
pygame.mixer.init()


# Загружаем музыку
def fullname_for_music_file(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с аудио '{fullname}' не найден")
        sys.exit()
    return fullname


pygame.mixer.music.load(fullname_for_music_file('main_music.mp3'))
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0.0)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def main(screen):
    running = True
    fps = 25
    clock = pygame.time.Clock()

    game = Tetris()
    counter = 0
    pressing_down = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Поворот блока
                if event.key == pygame.K_UP:
                    game.rotate()
                # Ускорение блока
                if event.key == pygame.K_DOWN:
                    pressing_down = True
                # Передвижение блока влево
                if event.key == pygame.K_LEFT:
                    game.move_to_the_side(-1)
                # Передвижение блока вправо
                if event.key == pygame.K_RIGHT:
                    game.move_to_the_side(1)
                # Возможность опустить блок сразу в самый низ
                if event.key == pygame.K_SPACE:
                    game.move_down_until_touch_smth()
                # Возможность начать игру с начала
                if event.key == pygame.K_ESCAPE:
                    game.__init__()
                # Возможность преждевременно закончить игру - нажатие клавиши Tab
                if event.key == pygame.K_TAB:
                    game.condition = "конец"

            # Прекращение ускорения блока
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

        # Располагаем фон игры
        image_of_background = load_image("background.jpg")
        image_of_background = pygame.transform.scale(image_of_background, (500, 500))
        screen.blit(image_of_background, (0, 0))

        # Пишем нужные измерения прогресса игры
        font_in_game_process = pygame.font.SysFont('Arial', 25, True, False)
        text_level = font_in_game_process.render("Уровень: " + str(game.level), True, (255, 255, 255))
        screen.blit(text_level, [5, 30])
        text_score = font_in_game_process.render("Очки: " + str(game.score), True, (255, 255, 255))
        screen.blit(text_score, [5, 65])
        text_record = font_in_game_process.render("Рекорд: " + str(record_of_all_games), True, (255, 255, 255))
        screen.blit(text_record, [5, 100])

        # Прорисовываем поле и уже приземлившиеся блоки, запускаем игру
        if game.one_block is None:
            game.new_block()
        counter += 1
        if counter > 100000:
            counter = 0
        if counter % (fps // game.level) == 0 or pressing_down:
            if game.condition == "начало":
                game.move_down_simple()

        for i in range(game.height):
            for j in range(game.width):
                pygame.draw.rect(screen, (120, 120, 120), [game.x + game.coefficient_of_size * j,
                                                           game.y + game.coefficient_of_size * i,
                                                           game.coefficient_of_size, game.coefficient_of_size], 1)
                if game.pole[i][j] > 0:
                    pygame.draw.rect(screen, colours_of_blocks[game.pole[i][j]],
                                     [game.x + game.coefficient_of_size * j + 1,
                                      game.y + game.coefficient_of_size * i + 1,
                                      game.coefficient_of_size - 2, game.coefficient_of_size - 1])

        if game.one_block is not None:
            for i in range(4):
                for j in range(4):
                    summa = i * 4 + j
                    if summa in game.one_block.get_current_block():
                        pygame.draw.rect(screen, colours_of_blocks[game.one_block.colour_of_one_block],
                                         [game.x + game.coefficient_of_size * (j + game.one_block.x) + 1,
                                          game.y + game.coefficient_of_size * (i + game.one_block.y) + 1,
                                          game.coefficient_of_size - 2, game.coefficient_of_size - 2])

        # Если игрок прошёл все уровни, сообщаем ему это
        font_of_passed = pygame.font.SysFont('Arial', 65, True, False)
        text_game_passed = font_of_passed.render("Игра пройдена", True, (25, 25, 112))
        if game.condition == "пройдена":
            screen.blit(text_game_passed, [20, 200])

        # Если игрок проиграл, сообщаем ему это и предлагаем начать сначала
        font_of_ending = pygame.font.SysFont('Arial', 65, True, False)
        text_game_over = font_of_ending.render("Игра окончена", True, (25, 25, 112))
        text_game_over2 = font_of_ending.render("Нажмите ESC", True, (25, 25, 112))
        if game.condition == "конец":
            screen.blit(text_game_over, [20, 200])
            screen.blit(text_game_over2, [25, 265])
        pygame.display.flip()
        clock.tick(fps)


def start_screen(screen):
    run = True
    while run:
        intro_text = ["ИГРА КОСМОТЕТРИС", '',
                      "Правила игры:",
                      "В игре 12 уровней, чтобы перейти на следующий",
                      "уровень, разбейте 10 линий.",
                      'Блок можно ускорить, нажав на page down.',
                      'Чтобы закончить игру преждевременно,',
                      'нажмите Tab.', '',
                      'Для начала игры нажмите клавишу мыши или',
                      'любую клавишу клавиатуры', '', '',
                      'игру разработали Милогородская В.,',
                      'Бугаева Д., Сорокина В.']

        fon = pygame.transform.scale(load_image('fon.jpg'), (500, 500))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 29)
        text_coord = 40
        for line in intro_text:
            string_rendered = font.render(line, 1, (255, 255, 255))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                main(screen)


pygame.mixer.stop()

size = 500, 500
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Космотетрис")
start_screen(screen)

pygame.quit()
