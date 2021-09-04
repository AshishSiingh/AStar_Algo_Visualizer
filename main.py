import pygame
import math
import random
from queue import PriorityQueue
from pygame.sprite import RenderUpdates

WIDTH = 750
windows = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Pathfinding Algorithm")

start = pygame.image.load('Start.png')
end = pygame.image.load('End.png')

RED = (255, 0, 0)
PURPLE = (178, 102, 255)
BLUE = (0, 162, 232)
GREEN = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (225, 225, 225)
YELLOW = (255, 242, 0)
ORANGE = (255, 165, 0)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.prevColor = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.animCount = width//2
        self.countAnim = 0
        self.animSize = 0
        self.secColor = WHITE
    
    def getPos(self):
        return self.row, self.col

    def isVisited(self):
        return self.color == BLUE
    
    def isOpen(self):
        return self.color == PURPLE

    def isBlocked(self):
        return self.color == BLACK
    
    def isStart(self):
        return self.color == RED

    def isEnd(self):
        return self.color == GREEN

    def reset(self):
        if self.prevColor != WHITE and self.countAnim < self.animCount:
            pass
        else:
            self.prevColor = self.color
            self.countAnim = 0
        self.color = WHITE
        self.secColor = WHITE
        self.animCount = self.width//2
        self.animSize = 0

    def setStart(self):
        self.color = RED

    def setVisited(self):
        self.color = BLUE

    def setOpen(self):
        self.color = PURPLE

    def setBlocked(self):
        self.color = BLACK

    def setStart(self):
        self.color = RED

    def setEnd(self):
        self.color = GREEN

    def setPath(self):
        self.color = YELLOW

    def draw(self, windows):
        count = int(self.animCount)

        if self.color == WHITE and (self.prevColor == BLACK or self.prevColor == BLUE or self.prevColor == PURPLE or self.prevColor == YELLOW):
            count = int(self.countAnim)
            pygame.draw.rect(windows, self.prevColor, (self.x+count//2, self.y+count//2, self.width-count, self.width-count))
            self.countAnim += 0.15
            if self.countAnim >= self.animCount:
                self.countAnim = self.animCount
                self.prevColor = WHITE

        elif self.color == WHITE and self.prevColor == RED:
            count = int(self.countAnim)
            self.start = pygame.transform.scale(start, (self.width-count, self.width-count))
            windows.blit(self.start, (self.x+count//2, self.y+count//2))
            self.countAnim += 0.15
            if self.countAnim >= self.animCount:
                self.countAnim = self.animCount
                self.prevColor = WHITE

        elif self.color == WHITE and self.prevColor == GREEN:
            count = int(self.countAnim)
            self.end = pygame.transform.scale(end, (self.width-count, self.width-count))
            windows.blit(self.end, (self.x+count//2, self.y+count//2))
            self.countAnim += 0.2
            if self.countAnim >= self.animCount:
                self.countAnim = self.animCount
                self.prevColor = WHITE

        elif self.color == WHITE:
            pass
        
        elif self.color == RED:
            self.start = pygame.transform.scale(start, (self.width-count, self.width-count))
            if self.secColor != WHITE:
                pygame.draw.rect(windows, self.secColor, (self.x+count//2, self.y+count//2, self.width-count, self.width-count))
            windows.blit(self.start, (self.x+count//2, self.y+count//2))
            if self.secColor == WHITE:
                self.animCount -= 0.2
            else:
                self.animCount -= 0.1
            if self.animCount <= 0:
                self.animCount = 0

        elif self.color == GREEN:
            self.end = pygame.transform.scale(end, (self.width-count, self.width-count))
            if self.secColor != WHITE:
                pygame.draw.rect(windows, self.secColor, (self.x+count//2, self.y+count//2, self.width-count, self.width-count))
            windows.blit(self.end, (self.x+count//2, self.y+count//2))
            if self.secColor == WHITE:
                self.animCount -= 0.2
            else:
                self.animCount -= 0.1
            if self.animCount <= 0:
                self.animCount = 0

        elif self.color == BLACK:
            pygame.draw.rect(windows, self.color, (self.x+count//2, self.y+count//2, self.width-count, self.width-count))
            if self.animSize == 0:
                self.animCount -= 0.2
            if self.animCount <= -self.width//4:
                self.animSize = 1
            if self.animSize == 1:
                self.animCount +=0.2
                if self.animCount > 0:
                    self.animSize = 2
                    self.animCount = 0

        else:
            pygame.draw.rect(windows, self.color, (self.x+count//2, self.y+count//2, self.width-count, self.width-count))
            self.animCount -= 0.1
            if self.animCount <= 0:
                self.animCount = 0
    
    def updateNeighbors(self, grid):
        self.neighbors = []

        if self.row > 0 and not grid[self.row - 1][self.col].isBlocked():   # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isBlocked():   # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].isBlocked():   # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isBlocked():   # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconPath(cameFrom, current, draw):
    while current in cameFrom:
        current = cameFrom[current]
        current.reset()
        current.setPath()
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    cameFrom = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.getPos(), end.getPos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconPath(cameFrom, end, draw)
            start.setStart()
            end.setEnd()
            start.secColor = YELLOW
            end.secColor = YELLOW
            return True
        
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                cameFrom[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.getPos(), end.getPos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.setOpen()
        draw()

        if current != start:
            current.setVisited()

    return False

def createGrid(rows, width):
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid

def drawGrid(windows, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(windows, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(windows, GREY, (j * gap, 0), (j * gap, width))

def draw(windows, grid, rows, width):
    windows.fill(WHITE)

    for row in grid:
        for node in row:
            if node.color == BLUE or node.color == PURPLE:
                node.draw(windows)

    drawGrid(windows, rows, width)

    for row in grid:
        for node in row:
            if node.color != BLUE and node.color != PURPLE:
                node.draw(windows)

    pygame.display.update()

def getClickedPos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def main(windows, width):
    ROWS = 30
    grid = createGrid(ROWS, width)

    start = None
    end = None

    run = True
    started = False
    output = False

    while run:
        draw(windows, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue
        
            if pygame.mouse.get_pressed()[0]:    #LEFT M_BUTTON
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.setStart()

                elif not end and node != start:
                    end = node
                    end.setEnd()

                elif node != end and node != start:
                    node.setBlocked()

            elif pygame.mouse.get_pressed()[2]:  #RIGHT M_BUTTON
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    for row in grid:
                        for node in row:
                            node.reset()
                            if node == start:
                                start = None
                            elif node == end:
                                end = None
                
                elif event.key == pygame.K_r and not start and not end:
                    for row in grid:
                        for node in row:
                            num = random.randrange(0, 2)
                            if num == 1:
                                node.setBlocked()

                elif event.key == pygame.K_SPACE and not started:
                    if not start or not end:
                        continue
                    if output == False:
                        for row in grid:
                            for node in row:
                                node.updateNeighbors(grid)

                        algorithm(lambda: draw(windows, grid, ROWS, width), grid, start, end)
                        output = True
                    else:
                        for row in grid:
                            for node in row:
                                if node.color == BLUE or node.color == PURPLE or node.color == YELLOW:
                                    node.reset()
                                else:
                                    node.secColor = WHITE
                        output = False
                        for row in grid:
                            for node in row:
                                node.updateNeighbors(grid)

                        algorithm(lambda: draw(windows, grid, ROWS, width), grid, start, end)
                        output = True
        
    pygame.quit()

main(windows, WIDTH)
