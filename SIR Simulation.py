

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