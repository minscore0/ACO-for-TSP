import pygame
import pygame.gfxdraw

class Node:
    def __init__(self, screen, number, coords, color=(255, 255, 255), radius=10, is_best=False):
        self.screen = screen
        self.number = number
        self.coords = coords
        self.color = color
        self.radius = radius
        self.is_best = is_best

    def draw_node(self):
        self.pheromone = 1
        pygame.gfxdraw.filled_circle(self.screen, self.coords[0], self.coords[1], self.radius, self.color)
        pygame.gfxdraw.aacircle(self.screen, self.coords[0], self.coords[1], self.radius, self.color)

    def __repr__(self):
        return "Node"+str(self.number)
    
    def __str__(self):
        return "Node"+str(self.number)
