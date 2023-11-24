import mesa
import numpy as np
import heapq

class Buildings(mesa.Agent):

    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos


class ParkingSpots(mesa.Agent):

    def __init__(self, unique_id, pos, number, model):
        super().__init__(unique_id, model)
        self.pos = pos
        self.number = number


class RoundAbout(mesa.Agent):

    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos


class Stoplight(mesa.Agent):

    def __init__(self, unique_id, pos, color, model):
        super().__init__(unique_id, model)
        self.pos = pos
        self.color = color
        self.step_counter = 0  # Initialize the step counter
    
    def step(self):
        # Increment the step counter in each step
        self.step_counter += 1
        
        # Check if the step number is divisible by 10
        if self.step_counter % 10 == 0:
            # Change color from green to red or from red to green
            if self.color == "green":
                self.color = "red"
            else:
                self.color = "green"
        else: 
            self.color = self.color


class Car(mesa.Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos
        self.path = []  # Store the path the car will follow
        self.goal_position = None  # Store the goal position for the car

    def step(self):
        # Check if the path is empty (or reaching the end) and the goal position is set
        if not self.path and self.goal_position:
            # Use A* algorithm to find a path from current position to the goal position
            grid = [[0 for _ in range(self.model.width)] for _ in range(self.model.height)]
            # Add obstacles or non-traversable areas to the grid
            for x, y, _ in self.model.parkingSpots_positions:  # Update with actual obstacles
                grid[y][x] = 1  # Assuming parking spots are obstacles

            self.path = astar(self.pos, self.goal_position, grid)

        # Check if the car has a path to follow
        if self.path:
            # Get the next position in the path
            next_pos = self.path[0]

            # Check if the next position is within the grid
            if self.model.grid.is_cell_empty(next_pos):
                # Get the agent (if any) at the next position
                next_cell_contents = self.model.grid.get_cell_list_contents([next_pos])

                # Check if the cell is not occupied by a Building or a Stoplight with color "red"
                is_allowed_move = True
                for agent in next_cell_contents:
                    if isinstance(agent, Buildings) or (isinstance(agent, Stoplight) and agent.color == "red"):
                        is_allowed_move = False
                        break

                if is_allowed_move:
                    # Move the car to the next position
                    self.model.grid.move_agent(self, next_pos)
                    self.path.pop(0)  # Remove the visited position from the path

        


# A* algorithm implementation
def astar(start, goal, grid):
    def heuristic_cost_estimate(current, goal):
        # Manhattan distance heuristic for A* (can be replaced with other heuristics)
        return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

    def reconstruct_path(came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    # Define possible movements (4 directions: up, down, left, right)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic_cost_estimate(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            return reconstruct_path(came_from, current)

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            tentative_g_score = g_score[current] + 1  # Assuming each step has a cost of 1

            if 0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[0]) and grid[neighbor[0]][neighbor[1]] == 0:
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic_cost_estimate(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found
