import mesa
import numpy as np
import math
import random
import heapq
import util

class Road(mesa.Agent):
    """
    A Road Agent. Only traversable in a given trajectory.
    """
    def __init__(self, unique_id, pos, model, initial_direction):
        super().__init__(unique_id, model)
        self.pos = pos
        self.directions = []
        self.directions.append(initial_direction)
        
    def add_direction(self, direction):
        self.directions.append(direction)


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
        self.running = True

    def can_move_to_cell(self, pos):
        """
        Helper function, indicates if the car is allowed to move to cell.
        Takes a pos argument, a tuple of (x,y).
        """
        can_move = False
        if pos == self.pos:
            return True
        
        this_cell =self.model.grid.get_cell_list_contents(pos)

        # TODO: Where it can traverse which direction Moore n Milly neighbore; Moore = False
        for a in this_cell:
            # Check if it is occupied by another car.
            if isinstance(a, Car) or isinstance(a, Buildings) or isinstance(a, RoundAbout):
                can_move = False
                return can_move 
        
            elif isinstance(a, Stoplight): # if it's Stoplight 
                if a.color == "green" or a.color == "yellow": 
                    can_move =True 
                    self.running = True
                else: # If it's red
                    can_move = False
                    self.running = False
                    return can_move
            else: # If its road
                can_move = True
        
        return can_move

    # TODO: Make them de-spawn when entering a parking spot
    # TODO: Make the cars go out of parking spots first
    def direction_is_available(self, curr, next_pos):
        """
        Helper function to check if direction to move is available.
        Input: curr = (x,y); next_pos = (x,y);
        """
        this_cell =self.model.grid.get_cell_list_contents(curr)
        available_directions = []
        for a in this_cell:
            # Check if it is a Road.
            if isinstance(a, Road):
                available_directions = a.directions
            
        next_direct = ""
        if curr == next_pos:
            return True
        # y_curr < y_next => N
        if curr[1] < next_pos[1] and curr[0] == next_pos[0]:
            next_direct = "N"
        # y_curr > y_next => S
        elif curr[1] > next_pos[1] and curr[0] == next_pos[0]:
            next_direct = "S"
        # x_curr < x_next => E
        elif curr[0] < next_pos[0] and curr[1] == next_pos[1]:
            next_direct = "E"
        # x_curr > x_next => W
        elif curr[0] > next_pos[0] and curr[1] == next_pos[1]:
            next_direct = "W"

        if next_direct in available_directions:
            return True
        
        return False
    
    def continue_path(self, position):    
        """
        Helper function that follows the path if there is no AStar path 
        """
        for next_pos in self.model.grid.get_neighborhood(position, moore=self.moore, include_center=False):
            # Check if the next position is valid to move to
            if self.direction_is_available(self.pos,next_pos) and self.can_move_to_cell(next_pos):
                self.model.grid.move_agent(self, next_pos)
                self.path = self.aStarSearch(next_pos, self.goal_position)
        
    def step(self):
        """
        Called every step.
        1. Identify position
        2. Determine best path according to a global goal
        3. Find local best path
        4. Move to the next location
        """
        if self.pos == self.initial_pos:
            self.continue_path(self.pos)
        # Check if car is in goal
        if self.pos == self.goal_position:
            print(f"Car {self.unique_id} arrived to destination {self.goal_position}, {self.pos}")

        if not self.path and self.goal_position:
            self.path = self.aStarSearch(self.pos, self.goal_position)

        # Check if the car has a path to follow
        if self.path:
            next_pos = self.path[0]
            print("MOVE PLAN:",self.pos, next_pos)
            if self.can_move_to_cell(next_pos) and self.direction_is_available(self.pos,next_pos):
                self.model.grid.move_agent(self, next_pos)
                self.path.pop(0)  
            else:
                self.path = self.aStarSearch(next_pos, self.goal_position)
        else:
            print(f"No path at {self.pos}")
            if self.running == True:
                for next_pos in self.model.grid.get_neighborhood(self.pos, moore=self.moore, include_center=False):
                    # Check if the next position is valid to move to
                    if self.direction_is_available(self.pos,next_pos) and self.can_move_to_cell(next_pos):
                        self.path = self.aStarSearch(next_pos, self.goal_position)
                        self.continue_path(self.pos)
            

    def heuristic(self, current, goal):
        """
        Calculate the Euclidean distance heuristic with a tie-breaking rule.
        """
        # Check if the cell can be moved to; if not, increase heuristic value significantly
        if not self.can_move_to_cell(current):
            heuristic = math.inf  # Increase heuristic significantly if the cell cannot be moved to
            return heuristic
            
        # Euclidean distance as base heuristic
        heuristic = math.sqrt((goal[0] - current[0]) ** 2 + (goal[1] - current[1]) ** 2)

        return heuristic
    
    def reconstruct_path(self, came_from, current):
        """
        Reconstructs the path from start to goal using the 'came_from' dictionary.
        """
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]


    def aStarSearch(self, start, goal):
        """
        A* search algorithm to find the shortest path from 'start' to 'goal'.
        """
        frontier = util.PriorityQueue()
        frontier.push(start, 0)
        came_from = {}
        cost_so_far = {start: 0}

        while not frontier.isEmpty():
            current = frontier.pop()

            if current == goal:
                A = self.reconstruct_path(came_from, goal)
                print(A)
                return A

            for next_pos in self.model.grid.get_neighborhood(current, moore=self.moore, include_center=False):
                # Check if the next position is valid to move to
                if self.direction_is_available(current,next_pos):
                    new_cost = cost_so_far[current] + self.heuristic(current, next_pos)
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + self.heuristic(next_pos, goal)
                        frontier.push(next_pos, priority)
                        came_from[next_pos] = current

        return []  # If no path found