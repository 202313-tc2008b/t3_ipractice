import mesa
import numpy as np
import heapq

class Buildings(mesa.Agent):
    """
    A Building Agent. A car can't go through it.
    """
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos


class ParkingSpots(mesa.Agent):
    """
    A ParkingSpot Agent. The start and goal of a car.
    """
    def __init__(self, unique_id, pos, number, model):
        super().__init__(unique_id, model)
        self.pos = pos
        self.number = number


class RoundAbout(mesa.Agent):
    """
    A RoundAbout Agent. A car can't go through it.
    """
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.pos = pos


class Stoplight(mesa.Agent):
    """
    A Stoplight Agent. Will change color each 10 steps.
    """
    def __init__(self, unique_id, pos, color, model):
        super().__init__(unique_id, model)
        self.pos = pos
        self.color = color
        self.step_counter = 0  # Initialize the step counter
    
    def step(self):
        """
        Changes (maybe) Stoplight's color. Will execute on each step. 
        """
        # Increment the step counter in each step
        self.step_counter += 1
        
        # Check if the step number is 2 steps before changing colors
        if (self.step_counter + 2) % 10 == 0:
            if self.color == "green":
                self.color = "yellow"
            else: 
                self.color = self.color 
        # Check if the step number is divisible by 10
        elif self.step_counter % 10 == 0:
            # Change color from green to red or from red to green
            if self.color == "green" or self.color == "yellow":
                self.color = "red"
            else:
                self.color = "green"
        else: 
            self.color = self.color


class Car(mesa.Agent):
    """
    A Car agent. 
    """
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        self.initial_pos = pos
        self.pos = pos
        self.path = []  # Store the path the car will follow
        self.goal_position = None  # Store the goal position for the car
        self.moore = False # Moore neighborhood
        self.vision = 5

    def can_move_to_cell(self, pos):
        """
        Helper function, indicates if the car is allowed to move to cell.
        Takes a pos argument, a tuple of (x,y).
        """
        if pos == self.pos:
            return True
        
        this_cell = self.model.grid.get_cell_list_contents(pos)

        for a in this_cell:
            # Check if it is occupied by another car.
            if isinstance(a, Car) or isinstance(a, Buildings) or isinstance(a, RoundAbout):
                return False
            elif isinstance(a, Stoplight): # if it's Stoplight 
                if a.color == "green": 
                    return True 
                else: 
                    return False
            else: 
                return True

    def step(self):
        """
        1. Identify neighbors
        2. Determine best path according to a global goal
        3. Find local best path
        4. Move to the next location
        """

        """ neighbors = [ i 
                     for i in self.model.grid.get_neighborhood(
            self.pos, self.moore, True, self.vision
        ) if self.can_move_to_cell(i)] 
        """
        
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
            next_cell_contents = self.model.grid.get_cell_list_contents([next_pos])

            # Check if the next position is within the grid
            if self.model.grid.is_cell_empty(next_pos):

                self.model.grid.move_agent(self, next_pos)
                self.path.pop(0)  # Remove the visited position from the path
                # Get the agent (if any) at the next position   
            else: 
                
                # Check if the cell is not occupied by a Building or a Stoplight with color "red"
                if self.can_move_to_cell(next_pos):
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
