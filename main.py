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
font1 = pygame.font.Font("freesansbold.ttf", 15)
font2 = pygame.font.Font("freesansbold.ttf", 30)

# colors
global GREEN, BLUE, WHITE, ITERATION_NUM
GREEN = (42, 232, 64)
BLUE = (48, 171, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ITERATION_NUM = None

# global constants
global NUMBER_OF_ANTS, MAX_PHEROMONE, MIN_PHEROMONE, EVAPORATION_RATE, NUM_INTERATIONS, START_ELITIST_ROUND, START_MIN_MAX_ROUND, ANT_SPEED, ALPHA, BETA
NUMBER_OF_ANTS = 50
MAX_PHEROMONE = 1
MIN_PHEROMONE = 0.01
EVAPORATION_RATE = 0.3
NUM_ITERATIONS = 80
START_ELITIST_ROUND = 30
START_MIN_MAX_ROUND = 60
ANT_SPEED = 5
ALPHA = 1
BETA = 3


def run_ACO(screen, nodes, node_names, name_rects, edges, find_edge): # runs the ACO algorithm
    global_best = (float("inf"), [])
    for i in range(NUM_ITERATIONS):
        clock.tick(80)
        global ITERATION_NUM
        ITERATION_NUM = i+1
        paths = list()
        best = set()
        for ant in range(NUMBER_OF_ANTS):
            paths.append(create_path(screen, nodes, find_edge))
        length_path = sorted([(route_cost(find_edge, path)) for path in paths], key=lambda a: a[0])
        for edge in length_path[0][1]:
            edge.is_best = True
            best.add(edge)
        for x in length_path[1:]:
            for edge in x[1]:
                if edge in best:
                    continue
                edge.is_best = False

        walk_ants(nodes, node_names, name_rects, edges, paths)
        if i < START_ELITIST_ROUND:
            stage = 1
        elif i < START_MIN_MAX_ROUND:
            stage = 2
        else:
            stage = 3
        global_best = local_pheromone_update(find_edge, paths, stage, global_best)
        global_pheromone_update(edges)
        update_display(nodes, node_names, name_rects, edges)


def route_cost(find_edge, route): # returns the total cost of a route and the edges that make up the route
    edges = list()
    cost = 0
    for i in range(len(route)-1):
        edges.append(find_edge[route[i].number][route[i+1].number])
    edges.append(find_edge[route[-1].number][route[0].number])
    for edge in edges:
        cost += edge.length
    
    return cost, edges


def local_pheromone_update(find_edge, paths, stage, global_best): # updates pheromone paths
    cost_edges = list()
    for route in paths:
        cost_edges.append(route_cost(find_edge, route))
        cost, route_edges = route_cost(find_edge, route)
    cost_edges.sort(key = lambda x: x[0])

    if cost_edges[0][0] < global_best[0]:
        global_best = (cost_edges[0][0], cost_edges[0][1])
    if stage == 1:
        for edge in cost_edges[0][1]:
            edge.pheromone = min(MAX_PHEROMONE, edge.pheromone + (90/cost))
        for path in cost_edges[1:]:
            for edge in path[1]:
                edge.pheromone = min(MAX_PHEROMONE, edge.pheromone + (70/cost))
    elif stage == 2:
        for edge in cost_edges[0][1]:
            edge.pheromone = min(MAX_PHEROMONE, edge.pheromone + (150/cost))
        for path in cost_edges[1:]:
            edge.pheromone = min(MAX_PHEROMONE, edge.pheromone + (70/cost))
    elif stage == 3:
        for edge in global_best[1]:
            edge.pheromone = min(MAX_PHEROMONE, edge.pheromone + (170))

    return global_best


def global_pheromone_update(edges): # evaporates pheromone from all paths
    for edge in edges:
        edge.pheromone = max(MIN_PHEROMONE, edge.pheromone * (1-EVAPORATION_RATE))


def create_path(screen, nodes, find_edge) -> list: # creates a route through the graph
    ant = Ant(screen, nodes)
    for i in range(len(ant.unvisited_nodes)):
        node_probabilities = list()
        for node in ant.unvisited_nodes:
            edge = find_edge[ant.current_node.number][node.number]
            node_probabilities.append((((edge.pheromone**ALPHA)*(1/edge.length)**BETA)
                                       /sum([find_edge[ant.current_node.number][node.number].pheromone**ALPHA*((1/find_edge[ant.current_node.number][node.number].length)**BETA) for node in ant.unvisited_nodes]), node))
        
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
        for t in range(0, 100, ANT_SPEED):
            ant_positions = set()
            for ant in step:
                A, B = ant[0].coords, ant[1].coords
                ant_positions.add(l(t, A, B))
            update_display(nodes, node_names, name_rects, edges, ant_positions)
        return


def add_node(screen, nodes, node_names, name_rects, edges, find_edge) -> tuple[list, list, list, list, set, list]: # adds a node to the graph
    nodes.append(Node(screen, len(nodes), pygame.mouse.get_pos()))
    added_node = nodes[-1]
    node_names.append(font1.render(str(len(nodes)-1), True, WHITE))
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
    best = set()
    for edge in edges:
        if edge.is_best:
            best.add(edge)
        else:
            edge.draw_edge(EVAPORATION_RATE)
    for edge in best:
        edge.draw_edge(EVAPORATION_RATE)
        edge.draw_edge(EVAPORATION_RATE)
    for i, node in enumerate(nodes):
        node.draw_node()
        screen.blit(node_names[i], name_rects[i])
    
    for ant in ant_positions:
        pygame.gfxdraw.aacircle(screen, round(ant[0]), round(ant[1]), 3, (212, 70, 59))
        pygame.gfxdraw.filled_circle(screen, round(ant[0]), round(ant[1]), 3, (212, 70, 59))

    if ITERATION_NUM is not None:
        iter_text = font2.render("Round " + str(ITERATION_NUM), True, WHITE)
        iter_rect = iter_text.get_rect()
        iter_rect.center = (130, 70)
        screen.blit(iter_text, iter_rect)
    
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
            
            elif (event.key == pygame.K_RETURN or event.key == pygame.K_s) and not started: # start simulation
                started = True
                print("started")
                run_ACO(screen, nodes, node_names, name_rects, edges, find_edge) 
                started = False

            elif event.key == pygame.K_t: # for testing
                print("test started")

    update_display(nodes, node_names, name_rects, edges)
    pygame.display.flip()

pygame.quit()
