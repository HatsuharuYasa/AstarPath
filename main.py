import pygame
import math
from queue import PriorityQueue

WIDTH = 800

WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208) 


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.color = WHITE
        self.neighbours = []
        self.total_rows = total_rows
    
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_start(self):
        return self.color == TURQUOISE
    
    def is_end(self):
        return self.color == ORANGE
    
    def is_barrier(self):
        return self.color == BLACK
    
    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK
    
    def make_start(self):
        self.color = TURQUOISE
    
    def make_end(self):
        self.color = ORANGE
    
    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbour(self, grid):
        self.neighbours = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (self.row + i) >= 0 and (self.row + i) < self.total_rows and (self.col + j) >= 0 and (self.col + j) < self.total_rows:
                    if not(i == 0 and j == 0) and not grid[self.row + i][self.col + j].is_barrier():
                        self.neighbours.append(grid[self.row + i][self.col + j])
    
    def __lt__(self, other):
        return False

def dist(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt(pow(x2-x1, 2) + pow(y2-y1, 2))

def make_grids(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        row = []
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            row.append(spot)
        grid.append(row)
    return grid
    
def draw_grids(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grids(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos

    row = x // gap
    col = y // gap
    return row, col

def wall_check(current, neighbour, grid):
    x1, y1 = current.get_pos()
    x2, y2 = neighbour.get_pos()
    if grid[x1][y2].is_barrier() and grid[x2][y1].is_barrier():
        return False
    return True

def reconstruct_path(previous, current, draw):
    while current in previous:
        print(current.get_pos())
        current = previous[current]
        current.make_path()
        draw()
        
def algorithm(draw, grid, start, end):
    open_set = PriorityQueue()
    open_set.put((0, start))
    previous = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = dist(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[1]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(previous, end, draw)
            end.make_end()
            start.make_start()
            return True

        blocked = False

        for neighbour in current.neighbours: #checking the surrounding neighbours
            g_tmp = g_score[current] + dist(current.get_pos(), neighbour.get_pos())

            if g_tmp < g_score[neighbour]:
                previous[neighbour] = current
                g_score[neighbour] = g_tmp
                f_score[neighbour] = g_tmp + dist(neighbour.get_pos(), end.get_pos()) #heuristic
                if neighbour not in open_set_hash and wall_check(current, neighbour, grid): #register the new neighbour
                    open_set.put((f_score[neighbour], neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
        
        
        draw()

        if current != start:    
            current.make_closed()
        
    
    return False

            
def main(win, width):
    ROWS = 25
    grid = make_grids(ROWS, width)

    pos_start = None
    pos_end = None

    run  = True
    started = False
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if pygame.mouse.get_pressed()[0]: #Setting the interaction
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not pos_start and spot != pos_end:
                    pos_start = spot
                    pos_start.make_start()
                elif not pos_end and spot != pos_start:
                    pos_end = spot
                    pos_end.make_end()
                elif spot != pos_end and spot != pos_start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # Setting the interaction
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == pos_start:
                    pos_start = None
                elif spot == pos_end:
                    pos_end = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbour(grid)
                    
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, pos_start, pos_end)
                
                if event.key == pygame.K_c:
                    pos_end = None
                    pos_start = None
                    grid = make_grids(ROWS, width)



    pygame.quit()

if __name__ == "__main__":
    main(WIN, WIDTH)