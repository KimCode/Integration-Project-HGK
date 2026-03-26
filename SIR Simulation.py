# Pseudo code

# Setup : 
#   * Create window (Split: Left = Simulation, Right = Graph).
#   * Population = List of person objects.
#   * Data = List to store S, I, R counts per day of simulation
#   * Set first "Infected" person.
# Dots :
#   * For each person:
#     * Update position (x + dx, y + dy).
#     * Bounce if hitting simulation boundaries.
#     * If status is "Infected":
#       * If time_elapsed > Recovery_Threshold:
#         * Change status to "Recovered".
#
#   * For each "Infected" person:
#     * For each "Susceptible" Person:
#       * If distance(Infected, Susceptible) < Infection_radius:
#         * If random_chance < p:
#           * Change "Susceptible" status to "Infected".
#           * Set Infection_Timer = current_time. 
# Data Tracking :
#   * Every day of simulation:
#     * Count total S, I, and R agents.
#     * Add counts to Data List.
#
# Visualization
#   * Draw simulation (Dots moving and changing color).
#   * Draw Graph:
#    * Plot S (Blue), I (Red), and R (Green) lines based on Data
#   * Draw UI:
#    * Display Title: "Modeling SARS-CoV-2 Propagation Using the SIR Model".
#    * Display Live Counts and Day Clock.
#    * Display Legend

import math
import pygame
import random

pygame.init()  

# ---- Constants ----
window_width = 1280
window_height = 720

# sim on the left, graph on the right
simulation_width = 720
graph_x = simulation_width + 20        # 20px gap between sim and graph
graph_width = window_width - simulation_width - 40
graph_y = 120
graph_height = window_height - 180 

# --- Simulation parameters ---
starting_pop = 500
radius_infect = 5       # pixel radius where infection can spread
infection_rate = 0.15   # 15% chance per frame of contact
recovery_time = 720     # frames
speed = 1
fps = 60
day_frame = 60          # 60 frames = 1 day

day_cap = 60          

# --- Colors (R, G, B) ---
white = (255, 255, 255)
black = (0,0,0)
background = (200, 200, 200)  
simulation_background = (220, 220, 235)
purple = (127, 0, 255) # Susceptible
red = (220, 60, 60)    # Infected
green = (60, 200, 100) # Recovered

class Human:
    def __init__(self, x, y): 
        self.x = x
        self.y = y
        
        # random direction and speed for each person
        self.dx = random.uniform(-speed, speed)
        self.dy = random.uniform(-speed, speed)
        
        self.status = "Susceptible"
        
        # tracks when they got infected so I know when to recover them
        self.infection_timer = 0
    
    def draw(self, surface): 
        if self.status == "Susceptible":
            dot_colour = purple
        elif self.status == "Infected":
            dot_colour = red
        else:
            dot_colour = green

        # int() because pygame freaks out with floats
        pygame.draw.circle(surface, dot_colour, (int(self.x), int(self.y)), 6) 
    
    def update(self, current_frame):
        self.x += self.dx
        self.y += self.dy

        # bounce off walls
        if self.x < 10 or self.x > simulation_width - 10:
            self.dx *= -1
        if self.y < 80 or self.y > window_height - 10:
            self.dy *= -1
        
        # check if they've been sick long enough to recover
        if self.status == "Infected":
            if current_frame - self.infection_timer > recovery_time:
                self.status = "Recovered"

    # pythagorean distance between this dot and another
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

def main():
    screen = pygame.display.set_mode((window_width, window_height)) 
    pygame.display.set_caption("SIR Model - SARS-CoV-2 Propagation") 
    clock = pygame.time.Clock()

    big_font   = pygame.font.SysFont("Arial", 22, bold=True)
    small_font = pygame.font.SysFont("Arial", 16)
    title_font = pygame.font.SysFont("Arial", 20, bold=True)

    # spawn everyone at a random spot inside the sim box
    people = []
    for _ in range(starting_pop):
        x = random.randint(20, simulation_width - 20)
        y = random.randint(90, window_height - 20)
        people.append(Human(x, y))

    # patient zero
    people[0].status = "Infected"
    people[0].infection_timer = 0
    
    frame   = 0
    day     = 0
    running = True

    # these store the S, I, R counts over time for the graph
    susceptible_data = [] 
    infected_data = [] 
    recovered_data = [] 

    # --- MAIN LOOP ---
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # freeze everything once we hit the cap
        if day < day_cap:
            
            for human in people:
                human.update(frame)

            # split into two lists so I'm not checking recovered people
            infected     = [p for p in people if p.status == "Infected"]
            susceptible  = [p for p in people if p.status == "Susceptible"]

            # check every infected person against every susceptible person
            for inf in infected:
                for sus in susceptible:
                    if inf.distance_to(sus) < radius_infect:
                        # random roll to decide if transmission actually happens
                        if random.random() < infection_rate:
                            sus.status = "Infected"
                            sus.infection_timer = frame
            
            # snapshot the counts once per day
            if frame % day_frame == 0:
                s = sum(1 for p in people if p.status == "Susceptible")
                i = sum(1 for p in people if p.status == "Infected")
                r = sum(1 for p in people if p.status == "Recovered")
                susceptible_data.append(s)
                infected_data.append(i)
                recovered_data.append(r)
                day += 1
            
            frame += 1

        # ==========================================
        # DRAWING
        # ==========================================
        
        screen.fill(background)
        pygame.draw.rect(screen, simulation_background, (0, 60, simulation_width, window_height - 60))

        for human in people:
            human.draw(screen)

        # graph background box
        pygame.draw.rect(screen, simulation_background,(graph_x, graph_y, graph_width, graph_height))

        # need at least 2 points to draw a line
        if len(susceptible_data) > 1:
            max_days = len(susceptible_data)

            def graph_ypos(val):
                # converts a count into a y pixel position on the graph
                return graph_y + graph_height - int(val / starting_pop * graph_height)

            for i in range(1, max_days):
                # map day index to an x pixel position, scaling across graph_width
                x1 = graph_x + int((i - 1) / (max_days - 1) * graph_width)
                x2 = graph_x + int(i / (max_days - 1) * graph_width)

                # draw one segment of each curve, connecting previous day to current,(x1, graph_ypos(susceptible_data[i-1])),(x2, graph_ypos(susceptible_data[i])), 2)
                pygame.draw.line(screen, red,(x1, graph_ypos(infected_data[i-1])),(x2, graph_ypos(infected_data[i])), 2)
                pygame.draw.line(screen, green,(x1, graph_ypos(recovered_data[i-1])),(x2, graph_ypos(recovered_data[i])), 2)
        
        title_surf = big_font.render(
            "Modeling SARS-CoV-2 Propagation Using the SIR Model",
            True, black)
        screen.blit(title_surf, (10, 15))

        # live counters at the top
        current_susceptible = sum(1 for p in people if p.status == "Susceptible")
        current_infected = sum(1 for p in people if p.status == "Infected")
        current_recovered = sum(1 for p in people if p.status == "Recovered")

        screen.blit(small_font.render(f"S: {current_susceptible}", True, purple),  (10,  45))
        screen.blit(small_font.render(f"I: {current_infected}", True, red),   (70,  45))
        screen.blit(small_font.render(f"R: {current_recovered}", True, green), (130, 45))
        screen.blit(small_font.render(f"Day: {day}", True, black), (200, 45))

        if day >= day_cap:
            screen.blit(small_font.render("SIMULATION FINISHED", True, red), (300, 45))

        screen.blit(title_font.render("SIR Graph", True, black),
                    (graph_x, graph_y - 25))

        # legend
        lx, ly = graph_x, window_height - 55
        pygame.draw.circle(screen, purple,  (lx + 8,   ly + 8), 6)
        pygame.draw.circle(screen, red,   (lx + 118, ly + 8), 6)
        pygame.draw.circle(screen, green, (lx + 208, ly + 8), 6)
        screen.blit(small_font.render("Susceptible", True, purple),  (lx + 18,  ly))
        screen.blit(small_font.render("Infected",    True, red),   (lx + 128, ly))
        screen.blit(small_font.render("Recovered",   True, green), (lx + 218, ly))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    main()