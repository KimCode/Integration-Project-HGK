import math
import random
import pygame

WIDTH, HEIGHT = 1200, 700
SIM_WIDTH = 700
GRAPH_WIDTH = WIDTH - SIM_WIDTH

FPS = 60
DAY_LENGTH_FRAMES = FPS  # 1 simulation day = 1 second

POPULATION_SIZE = 120
PERSON_RADIUS = 5
SPEED = 2

INFECTION_RADIUS = 12
INFECTION_PROBABILITY = 0.18
RECOVERY_DAYS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
BLUE = (60, 120, 255)     # Susceptible
RED = (220, 60, 60)       # Infected
GREEN = (60, 180, 90)     # Recovered
DARK_BLUE = (30, 70, 180)

# ----------------------------
# PERSON CLASS
# ----------------------------
class Person:
    def __init__(self, x, y, dx, dy, status="S"):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.status = status
        self.infection_day = None

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # Bounce off simulation boundaries
        if self.x - PERSON_RADIUS <= 0 or self.x + PERSON_RADIUS >= SIM_WIDTH:
            self.dx *= -1
        if self.y - PERSON_RADIUS <= 60 or self.y + PERSON_RADIUS >= HEIGHT:
            self.dy *= -1

        # Keep inside bounds after bounce
        self.x = max(PERSON_RADIUS, min(SIM_WIDTH - PERSON_RADIUS, self.x))
        self.y = max(60 + PERSON_RADIUS, min(HEIGHT - PERSON_RADIUS, self.y))

    def update_recovery(self, current_day):
        if self.status == "I" and self.infection_day is not None:
            if current_day - self.infection_day >= RECOVERY_DAYS:
                self.status = "R"

    def draw(self, screen):
        if self.status == "S":
            color = BLUE
        elif self.status == "I":
            color = RED
        else:
            color = GREEN

        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), PERSON_RADIUS)


# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def create_population(size):
    population = []
    for _ in range(size):
        x = random.randint(PERSON_RADIUS, SIM_WIDTH - PERSON_RADIUS)
        y = random.randint(60 + PERSON_RADIUS, HEIGHT - PERSON_RADIUS)

        dx = random.choice([-SPEED, -SPEED + 1, SPEED - 1, SPEED])
        dy = random.choice([-SPEED, -SPEED + 1, SPEED - 1, SPEED])

        # Avoid zero movement
        if dx == 0:
            dx = SPEED
        if dy == 0:
            dy = -SPEED

        population.append(Person(x, y, dx, dy, "S"))

    # Set first infected person
    patient_zero = random.choice(population)
    patient_zero.status = "I"
    patient_zero.infection_day = 0

    return population


def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def count_states(population):
    s = sum(1 for p in population if p.status == "S")
    i = sum(1 for p in population if p.status == "I")
    r = sum(1 for p in population if p.status == "R")
    return s, i, r


def draw_text(screen, text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_legend(screen, font):
    legend_x = SIM_WIDTH + 20
    legend_y = HEIGHT - 90

    pygame.draw.circle(screen, BLUE, (legend_x, legend_y), 6)
    draw_text(screen, "Susceptible", font, BLACK, legend_x + 15, legend_y - 10)

    pygame.draw.circle(screen, RED, (legend_x, legend_y + 25), 6)
    draw_text(screen, "Infected", font, BLACK, legend_x + 15, legend_y + 15)

    pygame.draw.circle(screen, GREEN, (legend_x, legend_y + 50), 6)
    draw_text(screen, "Recovered", font, BLACK, legend_x + 15, legend_y + 40)


def draw_graph(screen, data, max_population, small_font, title_font):
    graph_x = SIM_WIDTH + 20
    graph_y = 100
    graph_w = GRAPH_WIDTH - 40
    graph_h = 420

    # Background
    pygame.draw.rect(screen, WHITE, (graph_x, graph_y, graph_w, graph_h))
    pygame.draw.rect(screen, BLACK, (graph_x, graph_y, graph_w, graph_h), 2)

    draw_text(screen, "SIR Graph", title_font, BLACK, graph_x, graph_y - 35)

    # Axes labels
    draw_text(screen, f"{max_population}", small_font, BLACK, graph_x - 5, graph_y - 10)
    draw_text(screen, "0", small_font, BLACK, graph_x - 5, graph_y + graph_h - 10)

    if len(data) < 2:
        return

    max_days = max(1, len(data) - 1)

    def point(day_index, value):
        x = graph_x + (day_index / max_days) * graph_w
        y = graph_y + graph_h - (value / max_population) * graph_h
        return int(x), int(y)

    # Draw lines for S, I, R
    for idx in range(1, len(data)):
        s1, i1, r1 = data[idx - 1]
        s2, i2, r2 = data[idx]

        pygame.draw.line(screen, BLUE, point(idx - 1, s1), point(idx, s2), 2)
        pygame.draw.line(screen, RED, point(idx - 1, i1), point(idx, i2), 2)
        pygame.draw.line(screen, GREEN, point(idx - 1, r1), point(idx, r2), 2)

    # Day labels
    draw_text(screen, "Days", small_font, BLACK, graph_x + graph_w // 2 - 15, graph_y + graph_h + 10)


# ----------------------------
# MAIN PROGRAM
# ----------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Modeling SARS-CoV-2 Propagation Using the SIR Model")
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("arial", 24, bold=True)
    font = pygame.font.SysFont("arial", 18)
    small_font = pygame.font.SysFont("arial", 14)

    population = create_population(POPULATION_SIZE)

    # Data list to store S, I, R counts per day
    data = []
    current_day = 0
    frame_count = 0

    # Initial data point
    data.append(count_states(population))

    running = True
    while running:
        clock.tick(FPS)
        frame_count += 1

        # ----------------------------
        # EVENTS
        # ----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ----------------------------
        # UPDATE MOVEMENT + RECOVERY
        # ----------------------------
        for person in population:
            person.move()
            person.update_recovery(current_day)

        # ----------------------------
        # INFECTION LOGIC
        # For each infected person, check nearby susceptible people
        # ----------------------------
        newly_infected = []

        infected_people = [p for p in population if p.status == "I"]
        susceptible_people = [p for p in population if p.status == "S"]

        for infected in infected_people:
            for susceptible in susceptible_people:
                if susceptible.status != "S":
                    continue

                if distance(infected, susceptible) < INFECTION_RADIUS:
                    if random.random() < INFECTION_PROBABILITY:
                        newly_infected.append(susceptible)

        for person in newly_infected:
            person.status = "I"
            person.infection_day = current_day

        # ----------------------------
        # DATA TRACKING
        # Every day of simulation
        # ----------------------------
        if frame_count % DAY_LENGTH_FRAMES == 0:
            current_day += 1
            data.append(count_states(population))

        s_count, i_count, r_count = count_states(population)

        # ----------------------------
        # DRAW
        # ----------------------------
        screen.fill(LIGHT_GRAY)

        # Left side simulation area
        pygame.draw.rect(screen, WHITE, (0, 0, SIM_WIDTH, HEIGHT))
        pygame.draw.line(screen, BLACK, (SIM_WIDTH, 0), (SIM_WIDTH, HEIGHT), 3)

        # Title
        draw_text(
            screen,
            "Modeling SARS-CoV-2 Propagation Using the SIR Model",
            title_font,
            DARK_BLUE,
            20,
            15
        )

        # Draw people
        for person in population:
            person.draw(screen)

        # Right side graph
        draw_graph(screen, data, POPULATION_SIZE, small_font, font)

        # UI info
        draw_text(screen, f"Day: {current_day}", font, BLACK, SIM_WIDTH + 20, 30)
        draw_text(screen, f"Susceptible: {s_count}", font, BLUE, SIM_WIDTH + 20, 60)
        draw_text(screen, f"Infected: {i_count}", font, RED, SIM_WIDTH + 170, 60)
        draw_text(screen, f"Recovered: {r_count}", font, GREEN, SIM_WIDTH + 300, 60)

        draw_legend(screen, font)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()