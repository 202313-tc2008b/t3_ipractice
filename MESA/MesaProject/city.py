from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random
import csv

# Agent classes

class CityCell(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = None  # Road, Building, ParkingLot, RoadWithRailing, Stoplight

class Car(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.position = None
        self.stopped = False
        self.direction = None  # North, South, East, West

    def move(self):
        # Define movement logic for the car
        possible_moves = self.model.grid.get_neighborhood(
            self.position,
            moore=True,
            include_center=False
        )
        
        # Filter out positions that are outside the grid bounds or are buildings
        valid_moves = [
            pos for pos in possible_moves
            if self.model.grid.is_cell_empty(pos) or
            (isinstance(self.model.grid[pos], CityCell) and self.model.grid[pos].type != "Building")
        ]

        if valid_moves:
            new_position = random.choice(valid_moves)
            self.model.grid.move_agent(self, new_position)
            self.position = new_position

    def step(self):
        if not self.stopped:
            self.move()

class Stoplight(Agent):
    def __init__(self, unique_id, model, position, light_color):
        super().__init__(unique_id, model)
        self.position = position
        self.light_color = light_color  # Red, Green, Yellow

    def step(self):
        # TODO: Define logic for stoplight state transitions
        pass  # TODO: Add logic to change stoplight color over time or conditions


# Model class

class CityModel(Model):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = MultiGrid(self.width, self.height, True)
        self.schedule = RandomActivation(self)

        # Load city layout from a CSV file
        self.load_city_layout("city_layout.csv")  # Pass your CSV file name here


        # Create city grid with different cell types and place agents
        for x in range(self.width):
            for y in range(self.height):
                cell = CityCell((x, y), self)
                # Define the cell types based on the simulation requirements
                # Implement the logic to assign different types of cells (Road, Building, ParkingLot, etc.)
                self.grid.place_agent(cell, (x, y))

        # Add cars to the simulation
        for i in range(5):  # Add 5 cars for example
            car = Car(i, self)
            # Assign initial position to the cars (within parking lots or roads)
            initial_position = (random.randrange(self.width), random.randrange(self.height))
            car.position = initial_position  # Set the car's position
            # Set other car attributes like direction, stopped status, etc.
            self.schedule.add(car)
            self.grid.place_agent(car, initial_position)  # Place the car on the grid

        # TODO: Add stoplights to the simulation
        # TODO: Implement logic to place stoplights in the city grid

    def load_city_layout(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            row_index = 0
            for row in reader:
                if row_index >= self.height:
                    break  # Exit loop if CSV file exceeds grid height
                
                for col_index, cell_type in enumerate(row):
                    if col_index >= self.width:
                        break  # Exit loop if CSV file exceeds grid width
                    
                    cell = CityCell((col_index, row_index), self)
                    if cell_type == "%":  # Assuming "&" represents a Building
                        cell.type = "Building"
                    # TODO: Define other cell types based on your CSV file encoding
                    self.grid.place_agent(cell, (col_index, row_index))
                row_index += 1

    def step(self):
        self.schedule.step()
