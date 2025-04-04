import pygame
import random
import os

pygame.init()

# Размеры блоков и игрового поля
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Размеры экрана
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Определяем фигуры (тетромино) в виде строковых шаблонов
S_SHAPE = [['.....',
            '.....',
            '..00.',
            '.00..',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '...0.',
            '.....']]

Z_SHAPE = [['.....',
            '.....',
            '.00..',
            '..00.',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '.0...',
            '.....']]

I_SHAPE = [['..0..',
            '..0..',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '0000.',
            '.....',
            '.....',
            '.....']]

O_SHAPE = [['.....',
            '.....',
            '.00..',
            '.00..',
            '.....']]

J_SHAPE = [['.....',
            '.0...',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..00.',
            '..0..',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '...0.',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '.00..',
            '.....']]

L_SHAPE = [['.....',
            '...0.',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '..00.',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '.0...',
            '.....'],
           ['.....',
            '.00..',
            '..0..',
            '..0..',
            '.....']]

T_SHAPE = [['.....',
            '..0..',
            '.000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '..0..',
            '.....'],
           ['.....',
            '.....',
            '.000.',
            '..0..',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '..0..',
            '.....']]

SHAPES = [S_SHAPE, Z_SHAPE, I_SHAPE, O_SHAPE, J_SHAPE, L_SHAPE, T_SHAPE]
SHAPE_COLORS = [(0, 255, 0), (255, 0, 0), (0, 255, 255),
                (255, 255, 0), (255, 165, 0), (0, 0, 255),
                (128, 0, 128)]  # Цвета для фигур


# Класс для представления падающей фигуры
class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0


# Создание игрового поля: пустой двумерный список, где каждая ячейка — кортеж с цветом
def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid


# Преобразование шаблона фигуры в список координат с учетом текущей позиции и вращения
def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # Смещение -2 по X и -4 по Y для корректного позиционирования
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


# Проверка, находится ли фигура в допустимых пределах поля
def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(GRID_WIDTH) if grid[i][j] == (0, 0, 0)] for i in range(GRID_HEIGHT)]
    accepted_positions = [j for sub in accepted_positions for j in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


# Проверка, не вышли ли фигуры за верхнюю границу (игра окончена)
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


# Случайный выбор следующей фигуры
def get_shape():
    return Piece(GRID_WIDTH // 2, 0, random.choice(SHAPES))


# Вывод текста по центру экрана
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (SCREEN_WIDTH / 2 - label.get_width() / 2,
                         SCREEN_HEIGHT / 2 - label.get_height() / 2))


# Отрисовка сетки игрового поля
def draw_grid(surface, grid):
    for i in range(GRID_HEIGHT):
        pygame.draw.line(surface, (128, 128, 128), (0, i * BLOCK_SIZE), (SCREEN_WIDTH, i * BLOCK_SIZE))
        for j in range(GRID_WIDTH):
            pygame.draw.line(surface, (128, 128, 128), (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, SCREEN_HEIGHT))


# Удаление заполненных рядов и сдвиг остальных рядов вниз
def clear_rows(grid, locked):
    inc = 0
    ind = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(GRID_WIDTH):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


# Отрисовка игрового окна
def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))
    # Заголовок
    font = pygame.font.SysFont('comicsans', 40)
    label = font.render("Tetris", 1, (255, 255, 255))
    surface.blit(label, (SCREEN_WIDTH / 2 - label.get_width() / 2, 30))

    # Счёт
    font_score = pygame.font.SysFont('comicsans', 30)
    score_label = font_score.render("Score: " + str(score), 1, (255, 255, 255))
    surface.blit(score_label, (SCREEN_WIDTH - score_label.get_width() - 10, SCREEN_HEIGHT / 2 - 100))

    # Отрисовка блоков на поле
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            pygame.draw.rect(surface, grid[i][j],
                             (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    draw_grid(surface, grid)
    pygame.display.update()


# Основная игровая функция
def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Автоматическое падение фигуры
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        shape_positions = convert_shape_format(current_piece)

        # Добавляем фигуру на сетку для отрисовки
        for i in range(len(shape_positions)):
            x, y = shape_positions[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # Если фигура зафиксирована, добавляем её позиции в locked_positions
        if change_piece:
            for pos in shape_positions:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score)

        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False


# Меню игры, ожидающее нажатия клавиши
def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle(win, "Press Any Key To Play", 60, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()


if __name__ == "__main__":
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris в стакане")
    main_menu(win)

