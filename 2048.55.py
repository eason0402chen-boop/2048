import pygame
import random
import math

pygame.init()

FPS = 120

WIDTH, HEIGHT = 800, 800
ROWS = 5
COLS = 5

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("Liberation Sans", 45, bold=True)
SCORE_FONT = pygame.font.SysFont("Liberation Sans", 36, bold=True)
MOVE_VEL = 40

WHITE = (255, 255, 255)
gameover_text = FONT.render('Game Over', True, WHITE)
gameover_rect = gameover_text.get_rect()
gameover_rect.center = (WIDTH // 2, HEIGHT // 2)

WINDOW=pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")


class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT    

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color_index = min(color_index, len(self.COLORS) - 1)
        return self.COLORS[color_index]

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))
       
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
            ),
        )

    def set_pass(self,ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]


def draw_grid(window):
    for row in range(1,ROWS):
        y= row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)
   
    for col in range(1,COLS):
        x= col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles, score, over=False):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)
    draw_grid(window)

    score_label = SCORE_FONT.render(f"Score: {score}", True, FONT_COLOR)
    window.blit(score_label, (20, 20))

    if over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        window.blit(overlay, (0,0))
        window.blit(gameover_text, gameover_rect)

    pygame.display.update()


def get_random_pos(tiles):
    row=None
    col=None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)
       
        if f"{row}{col}" not in tiles:
            break

    return row, col

def move_tiles(window, tiles,clock, direction, score):
    update = True
    blocks = set()
    no_move = True
    score_increment = 0

    if direction == "left" :
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check =(
             lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        )
        ceil = True

    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check =(
             lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        )
        ceil = False
    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check =(
             lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        )
        ceil = True
    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check =(
             lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        )
        ceil = False

    no_move = 1;
    while update:
        clock.tick(FPS)
        update = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile) :
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
                no_move = 0
            elif(
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                    no_move = 0
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    score_increment += next_tile.value
                    blocks.add(next_tile)
                    no_move = 0
            elif move_check(tile, next_tile):
                tile.move(delta)
                no_move = 0
            else:
                continue
            tile.set_pass(ceil)
            update = True
        update_tiles(window, tiles, sorted_tiles, score + score_increment)
    if no_move == 0:
        return end_move(tiles), score_increment
    else:
        return "continue", 0

def can_move(tiles):
    for tile in tiles.values():
        row, col = tile.row, tile.col

        if col < COLS - 1:
            next_tile = tiles.get(f"{row}{col+1}")
            if next_tile and next_tile.value == tile.value:
                return True

        if row < ROWS - 1:
            next_tile = tiles.get(f"{row+1}{col}")
            if next_tile and next_tile.value == tile.value:
                return True

    return False

def end_move(tiles):
   
    row, col = get_random_pos(tiles)
    rand = random.random()

    if rand < 0.05:
        value = 8
    elif rand < 0.15:
        value = 4
    else:
        value = 2
    tiles[f"{row}{col}"] = Tile(value, row, col)
   
    if len(tiles) == ROWS * COLS:
        if not can_move(tiles):
            return "GameOver"
   
    return "continue"


def update_tiles(window, tiles, sorted_tiles, score):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles, score)


   
def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)
   
    return tiles



def main(window):
    clock = pygame.time.Clock()
    run = True
    over = False
    score = 0

    tiles = generate_tiles()    

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN and not over:
                runflag  = ""
                if event.key == pygame.K_LEFT:
                    runflag, score_add = move_tiles(window, tiles, clock, "left", score)
                    score += score_add
                elif event.key == pygame.K_RIGHT:
                    runflag, score_add = move_tiles(window, tiles, clock, "right", score)
                    score += score_add
                elif event.key == pygame.K_UP:
                    runflag, score_add = move_tiles(window, tiles, clock, "up", score)
                    score += score_add
                elif event.key == pygame.K_DOWN:
                    runflag, score_add = move_tiles(window, tiles, clock, "down", score)
                    score += score_add

                if  runflag == 'GameOver':
                    over = True

        draw(window, tiles, score, over)
    pygame.quit()


if __name__ == "__main__":
    main(WINDOW)