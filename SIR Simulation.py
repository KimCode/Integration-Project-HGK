

# Test code and draft to familiarize ourselves with coding using github
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

pygame.init()  # This function initializes all the modules pygame

# ---- Constants ----

# ---- Window Dimensions ----

window_width= 1280
window_height= 720

# ---- Define Sim and Graph dimensions (Using variables to allow easy changes) ----

simulation_width = 720 # Horizontal length of simulation
graph_x = simulation_width + 20 # Starting position in x of graph
graph_width = window_width - simulation_width - 40 # Total window width and subtracts the space used by the simulation
graph_y = 120
graph_height = window_height - 180 # Ensure space between top and bottom of graph and top and bottom of window

# --- Simulation parameters ---

# placeholder values

starting_pop = 100 # starting population
radius_infect = 10 # pixels
infection_rate = 0.2 # % chance per contact
recovery_time = 100 # frames until recovery
speed = 2
fps = 60
day_frame = 60 # frames = 1 simulation "day"

# --- Colors (R, G, B) ---

white = (255,255,255)
background = (15,15,25)  # dark background
simulation_background = ( 20,  20,  35)
purple = (127,0,255)  # Susceptible
red = (220,60,60)  # Infected
green = (60,200,100)  # Recovered

# This class acts as the blueprint for a single dot in the simulation
class Human:
    def __init__(self,x,y): 
        # Set starting coordinates
        self.x = x
        self.y = y
        # Give random speed and direction so movement looks natural/chaotic
        self.dx = random.uniform(-speed, speed)
        self.dy = random.uniform(-speed, speed)
        # Everyone starts out healthy
        self.status = "Susceptible"
        # timer to keep track of how many frames they've been sick which will be used for recovery time/rate
        self.infection_timer = 0
    
    # Attributing colors to dots/humans
    def draw(self, surface): #if/elif/else loops for determining colour
        if self.status == "Susceptible":
            dot_colour = purple
        elif self.status == "Infected":
            dot_colour = red
        else:
            dot_colour = green # Recovered since not infected or susceptible

        pygame.draw.circle(surface, dot_colour,(int(self.x), int(self.y)), 6) # Actually draw the circle. I had to wrap x and y in int() because float values need to be cast to integers for Pygame's pixel grid
    
    # Moving and bouncing function
    def movement(self, current_frame):
        # Move 
        self.x += self.dx
        self.y += self.dy

        # Bounce off the simulation walls if reach boundaries
        if self.x < 10 or self.x > simulation_width - 10:
            self.dx *= -1
        if self.y < 80 or self.y > window_height - 10:
            self.dy *= -1

def main():

    # Kick off all the Pygame internal systems so it actually runs
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height)) # Set up the main application window using the dimensions I defined at the top
    pygame.display.set_caption("SIR Model - SARS-CoV-2 Propagation") # The text that shows up in the top bar of the window
    clock = pygame.time.Clock() # Cap the framerate 

    # Fonts for the S/I/R stats
    big_font   = pygame.font.SysFont("Arial", 22, bold=True)
    small_font = pygame.font.SysFont("Arial", 16)
    title_font = pygame.font.SysFont("Arial", 20, bold=True)

    # Spawn people at random positions inside the sim area
    people = []
    for _ in range(starting_pop):
        x = random.randint(20, simulation_width - 20)
        y = random.randint(90, window_height - 20)
        people.append(Human(x, y))

    # Patient zero — first person gets infected
    people[0].status = "Infected"
    people[0].infection_timer = 0
    
    frame   = 0
    day     = 0
    running = True

    while running:
    # Handle closing the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Update all people ---
        for human in people:
            human.movement(frame)

        # --- Draw everything ---
        screen.fill(background)

        # Simulation box
        pygame.draw.rect(screen, simulation_background, (0, 60, simulation_width, window_height - 60))

        for human in people:
            human.draw(screen)

        pygame.display.flip()
        clock.tick(fps)
        frame += 1

    pygame.quit()


if __name__ == "__main__":
    main()