import pygame
import pygame.gfxdraw
import random

class Ant:
    def __init__(self, screen, nodes):
        self.screen = screen
        self.nodes = nodes
        self.visited_nodes = list()
        self.unvisited_nodes = set(nodes)
        self.current_node = random.choice(self.nodes)
        self.visit_node(self.current_node)
        self.pos = (None, None)

    def visit_node(self, node):
        self.visited_nodes.append(node)
        self.unvisited_nodes.remove(node)
        self.current_node = node
