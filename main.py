import pygame
import random
import pygame.gfxdraw
from node_class import Node
from edge_class import Edge
from ant_class import Ant

# set-up pygame
pygame.init()
pygame.display.set_caption("And Colony Optimization for TSP")
clock = pygame.time.Clock()
global screen
screen = pygame.display.set_mode((1560, 900))
font = pygame.font.Font("freesansbold.ttf", 15)

# global constants
alpha = 1 #(0.2-1)
global GREEN, BLUE, WHITE, BLACK, NUMBER_OF_ANTS, MAX_PHEROMONE, MIN_PHEROMONE, EVAPORATION_RATE, NUM_INTERATIONS
GREEN = (42, 232, 64)
BLUE = (48, 171, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NUMBER_OF_ANTS = 50
MAX_PHEROMONE = 1
MIN_PHEROMONE = 0.01
EVAPORATION_RATE = 0.35
NUM_ITERATIONS = 10


def run_ACO(screen, nodes, node_names, name_rects, edges, find_edge): # runs the ACO algorithm
    for i in range(NUM_ITERATIONS):
        paths = list()
        for ant in range(NUMBER_OF_ANTS):
            paths.append(create_path(screen, nodes, find_edge))
        walk_ants(nodes, node_names, name_rects, edges, paths)
        local_pheromone_update(find_edge, paths)
        global_pheromone_update(edges)
        update_display(nodes, node_names, name_rects, edges)


def route_cost(find_edge, route): # returns the total cost of a route and the edges that make up the route
    edges = list()
    cost = 0
    for i in range(len(route)-1):
        edges.append(find_edge[route[i].number][route[i+1].number])
    for edge in edges:
        cost += edge.length
    
    return cost, edges


def local_pheromone_update(find_edge, paths): # updates pheromone paths
    for route in paths:
        cost, route_edges = route_cost(find_edge, route)
        for edge in route_edges:
            print("added", min(MAX_PHEROMONE, edge.pheromone + (100/cost)))
            edge.pheromone = min(MAX_PHEROMONE, edge.pheromone + (100/cost))
            print(edge, edge.pheromone)


def global_pheromone_update(edges): # evaporates pheromone from all paths
    for edge in edges:
        edge.pheromone = max(MIN_PHEROMONE, edge.pheromone * (1-EVAPORATION_RATE))


def create_path(screen, nodes, find_edge) -> list: # creates a route through the graph
    ant = Ant(screen, nodes)
    for i in range(len(ant.unvisited_nodes)):
        node_probabilities = list()
        for node in ant.unvisited_nodes:
            edge = find_edge[ant.current_node.number][node.number]
            node_probabilities.append(((edge.pheromone*(1/edge.length))
                                       /sum([find_edge[ant.current_node.number][node.number].pheromone*(1/find_edge[ant.current_node.number][node.number].length) for node in ant.unvisited_nodes]), node))
        
        node_roulette = [(sum([x[0] for x in node_probabilities[:i+1]]), node_probabilities[i][1]) for i in range(len(node_probabilities))]
        pick = random.random()
        for chance, node in node_roulette:
            if pick <= chance:
                ant.visit_node(node)
                break

    return ant.visited_nodes


def walk_ants(nodes, node_names, name_rects, edges, paths: set): # shows the ants walking the path at the same time
    steps = list()
    for i in range(len(paths[0])-1):
        steps.append(set(tuple((paths[j][i:i+2])) for j in range(len(paths))))
    steps.append(set(tuple((paths[j][-1], paths[j][0])) for j in range(len(paths))))

    def l(t: float, A: tuple[float, float], B: tuple[float, float]) -> tuple[float, float]:
        v = (B[0] - A[0], B[1] - A[1])
        v_len = (v[0]**2+v[1]**2)**(0.5)
        u_v = (v[0]/v_len, v[1]/v_len)
        return (A[0] + t/100*v_len*u_v[0], A[1] + t/100*v_len*u_v[1])

    for step in steps:
        for t in range(0, 100, 5):
            ant_positions = set()
            for ant in step:
                A, B = ant[0].coords, ant[1].coords
                ant_positions.add(l(t, A, B))
            update_display(nodes, node_names, name_rects, edges, ant_positions)


def add_node(screen, nodes, node_names, name_rects, edges, find_edge) -> tuple[list, list, list, list, set, list]: # adds a node to the graph
    nodes.append(Node(screen, len(nodes), pygame.mouse.get_pos()))
    added_node = nodes[-1]
    node_names.append(font.render(str(len(nodes)-1), True, WHITE))
    name_rects.append(node_names[-1].get_rect())
    name_rects[-1].center = (nodes[-1].coords[0], nodes[-1].coords[1]+22)
    find_edge.append([])

    for i in range(len(find_edge)-1):
        find_edge[i].append(Edge(screen, nodes[i], added_node))
        find_edge[added_node.number].append(find_edge[i][added_node.number])
    find_edge[-1].append(Edge(screen, added_node, added_node))

    return nodes, node_names, name_rects, {x for xs in find_edge for x in xs}, find_edge


def update_display(nodes=list(), node_names=list(), name_rects=list(), edges=list(), ant_positions=set()): # updates the pygame display
    screen.fill(BLACK)
    for edge in edges:
        edge.draw_edge()
    for i, node in enumerate(nodes):
        node.draw_node()
        screen.blit(node_names[i], name_rects[i])
    
    for ant in ant_positions:
        pygame.gfxdraw.aacircle(screen, round(ant[0]), round(ant[1]), 3, (212, 70, 59))
        pygame.gfxdraw.filled_circle(screen, round(ant[0]), round(ant[1]), 3, (212, 70, 59))
    
    pygame.display.flip()


# define variables
edges = list()
find_edge = list()
nodes = list()
node_names = list()
name_rects = list()
started = False # status of running the simulation

# main loop
update_display()
running = True
while running:

    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and not started: # add node
            nodes, node_names, name_rects, edges, find_edge = add_node(screen, nodes, node_names, name_rects, edges, find_edge)
            update_display(nodes, node_names, name_rects, edges)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q: # quit program
                running = False

            elif event.key == pygame.K_DELETE or event.key == pygame.K_c: # clear graph
                nodes, node_names, name_rects, edges, find_edge = list(), list(), list(), list(), list()
                update_display()
                started = False
            
            elif (event.key == pygame.K_KP_ENTER or event.key == pygame.K_s) and not started: # start simulation
                started = True
                print("started")
                run_ACO(screen, nodes, node_names, name_rects, edges, find_edge) 
                started = False
                nodes, node_names, name_rects, edges, find_edge = list(), list(), list(), list(), list()

            elif event.key == pygame.K_t: # for testing
                print("test started")

    update_display(nodes, node_names, name_rects, edges)
    pygame.display.flip()

pygame.quit()
