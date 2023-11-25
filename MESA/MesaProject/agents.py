import mesa
import numpy as np
import math
import heapq
import util

class Road(mesa.Agent):
    """
    A Road Agent. Only traversable in a given trajectory.
    """
    def __init__(self, unique_id, pos, model, main_direction):
        super().__init__(unique_id, model)
        self.pos = pos
        self.main_direction = main_direction


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
        
        this_cell =self.model.grid.get_cell_list_contents(pos)

        # TODO: Where it can traverse which direction Moore yMilly neighbore
        # Moore = False
        for a in this_cell:
            # Check if it is occupied by another car.
            if isinstance(a, Car) or isinstance(a, Buildings) or isinstance(a, RoundAbout):
                return False
        
            elif isinstance(a, Stoplight): # if it's Stoplight 
                if a.color == "green" or a.color == "yellow": 
                    return True 
                else: # If it's red
                    return False
            else: # If its road
                return True

    def step(self):
        """
        1. Identify neighbors
        2. Determine best path according to a global goal
        3. Find local best path
        4. Move to the next location
        """
        if not self.path and self.goal_position:
            self.path = self.aStarSearch(self.pos, self.goal_position)
            print(self.path)

        # Check if the car has a path to follow
        if self.path:
            next_pos = self.path[0]
            print(next_pos)
            if self.can_move_to_cell(next_pos):
                self.model.grid.move_agent(self, next_pos)
                self.path.pop(0) 
            else:
                self.path = self.aStarSearch(self.pos, self.goal_position)

    
    def heuristic_cost_estimate(self, current, goal):
        """
        Calculate the heuristic cost estimate between current and goal positions.
        Uses the Euclidean distance as the base heuristic, considering if the cell can be moved to.
        """
        # Euclidean distance as base heuristic
        heuristic = math.sqrt((goal[0] - current[0]) ** 2 + (goal[1] - current[1]) ** 2)

        # Check if the cell can be moved to; if not, increase heuristic value significantly
        if not self.can_move_to_cell(current):
            heuristic += 1000  # Increase heuristic significantly if the cell cannot be moved to
        
        return heuristic
    

    def aStarSearch(self, initial, goal):
        """
        Search the node that has the lowest combined cost and heuristic first.
        """

        # Get the start state from the problem
        start_node = initial

        # Check if the start state is already the goal state
        if initial == goal:
            return []  # Return an empty list if the start state is the goal state

        # Initialize a list to keep track of visited nodes
        visited_nodes = []

        # Initialize a priority queue to explore nodes based on combined cost and heuristic
        priority_queue = util.PriorityQueue()
        priority_queue.push((start_node, [], 0), 0)  # Push the start node with zero cost initially

        while not priority_queue.isEmpty():
            # Get the current node, its associated actions, and the previous cost from the priority queue
            current_node, actions, prev_cost = priority_queue.pop()

            # If the current node has not been visited yet
            if current_node not in visited_nodes:
                # Mark the current node as visited
                visited_nodes.append(current_node)

                # Check if the current node is the goal state
                if current_node == goal:
                    return actions  # Return the list of actions if the goal state is reached

                # Explore the neighbors of the current node
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue  # Skip the current position

                        # Determine the next node coordinates
                        next_x, next_y = current_node[0] + dx, current_node[1] + dy
                        next_pos = (next_x, next_y)

                        # Check if the next position is within the bounds of the grid
                        if next_x >= 0 and next_x < self.model.grid.width and next_y >= 0 and next_y < self.model.grid.height:
                            # Calculate the new cost to reach the next node
                            new_cost_to_node = prev_cost + 1  # Assuming uniform cost

                            # Check if the next position is valid to move to
                            if self.can_move_to_cell(next_pos):
                                # Calculate the heuristic cost from the next node to the goal
                                heuristic_cost = new_cost_to_node + self.heuristic_cost_estimate(next_pos, goal)

                                # Create new actions by appending the current action
                                new_actions = actions + [(next_x, next_y)]

                                # Calculate the combined cost and heuristic and add it to the priority queue
                                priority_queue.push((next_pos, new_actions, new_cost_to_node), heuristic_cost)

        return []  # Return an empty list if the goal state is not reachable
