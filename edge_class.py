import pygame
from math import dist

class Edge:
    def __init__(self, screen, node_a, node_b, is_best=False, pheromone=0.1):
        self.screen = screen
        self.node_a = node_a
        self.node_b = node_b
        self.is_best = is_best
        self.pheromone = pheromone
        self.length = dist(node_a.coords, node_b.coords)
    
    def draw_edge(self):
        print("here", self, self.pheromone)
        if self.is_best:
            pygame.draw.aaline(self.screen, (42, 232, 64), self.node_a.coords, self.node_b.coords)
        else:
            pygame.draw.aaline(self.screen, (0.6 + 38.4*self.pheromone, 34.2 + 136.8*self.pheromone, 51 + 204*self.pheromone), 
                               (self.node_a.coords[0], self.node_a.coords[1]), 
                               (self.node_b.coords[0], self.node_b.coords[1]))
            pygame.draw.aaline(self.screen, (0.6 + 38.4*self.pheromone, 34.2 + 136.8*self.pheromone, 51 + 204*self.pheromone), 
                               (self.node_a.coords[0]+1, self.node_a.coords[1]), 
                               (self.node_b.coords[0]+1, self.node_b.coords[1]))
            pygame.draw.aaline(self.screen, (0.6 + 38.4*self.pheromone, 34.2 + 136.8*self.pheromone, 51 + 204*self.pheromone), 
                               (self.node_a.coords[0], self.node_a.coords[1]+1), 
                               (self.node_b.coords[0], self.node_b.coords[1]+1))
    
    def evaporate_pheromones(self):
        pass

    def __repr__(self):
        return "edge_"+str(self.node_a.number)+"_"+str(self.node_b.number)
    
    def __str__(self):
        return f"edge_{self.node_a.number}_to_{self.node_b.number}_p_{self.pheromone}_b_{self.is_best}"
