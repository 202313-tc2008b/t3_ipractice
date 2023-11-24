import mesa
import random
from agents import *
from scheduler import RandomActivationByTypeFiltered

class StreetView(mesa.Model):

    description = "MESA Visualization of the street cross simulation."
    
    def __init__(    
        self,
        width=24,
        height=24,
    ):
        super().__init__()
        # Iterate through the matrix and print the type of each element
        def read_matrix(matrix):
            for y, row in enumerate(matrix):
                for x, element in enumerate(row):
                    if element == '-':
                        position = (x,y)
                        self.road_positions.append(position)
                    elif element == 'G':
                        position = (x,y)
                        self.green_positions.append(position)
                    elif element == 'R':
                        position = (x,y)
                        self.red_positions.append(position)
                    elif element == '%':
                        position = (x,y)
                        self.building_positions.append(position)
                    elif element == 'B':
                        position = (x,y)
                        self.roundAbout_positions.append(position)
                    elif element.isdigit():
                        position = (x,y,element)
                        # print('Parking Lot ' + element)
                        self.parkingSpots_positions.append(position)
                    elif element == 'W':
                        pass
                        # print("Disallow going E")
                    elif element == 'E':
                        pass
                        #print("Disallow going W")
                    elif element == 'N':
                        pass
                        #print("Disallow going S")
                    elif element == 'S':
                        pass
                        # print("Disallow going N")
                    elif element == 'x':
                        pass
                        # print("Allow all ")
                    else:
                        print(f'Unknown Element: {element}')
        # Read the file content
        nmatL = []
        with open('layout.txt', 'r') as file:
            matrixL = [line.strip().split(',') for line in file.readlines()]
            for row in matrixL[::-1]:
                nmatL.append(row)
                
        
        nmatF = []
        with open('flow.txt', 'r') as file:
            matrixF = [line.strip().split(',') for line in file.readlines()]
            for row in matrixF[::-1]:
                nmatF.append(row)
                

        # Set parameters
        self.width = width
        self.height = height
        self.road_positions = []
        self.building_positions = []
        self.parkingSpots_positions = []
        self.roundAbout_positions = []
        self.green_positions = []
        self.red_positions = []
        self.car_positions = [(0,0)]

        read_matrix(nmatL)
        read_matrix(nmatF)

        self.schedule = RandomActivationByTypeFiltered(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
        self.datacollector = mesa.DataCollector(
            {
                "Buildings": lambda b: b.schedule.get_type_count(Buildings),
                "Parking Spots": lambda p: p.schedule.get_type_count(ParkingSpots),
                "Round About": lambda r: r.schedule.get_type_count(RoundAbout),
                "Stoplights": lambda s: s.schedule.get_type_count(Stoplight),
                "Cars": lambda c: c.schedule.get_type_count(Car),
            }
        )

        # Create buildings at specified positions
        for pos in reversed(self.building_positions):
            x, y = pos
            building = Buildings(self.next_id(), (x, y), self)
            self.grid.place_agent(building, (x, y))
            self.schedule.add(building)

        # Create parking spots at specified positions
        for pos in reversed(self.parkingSpots_positions):
            x, y, number = pos
            parkingSpot = ParkingSpots(self.next_id(), (x, y), number, self)
            self.grid.place_agent(parkingSpot, (x, y))
            self.schedule.add(parkingSpot)

        # Create round about
        for pos in reversed(self.roundAbout_positions):
            x, y = pos
            roundAbout = RoundAbout(self.next_id(), (x, y), self)
            self.grid.place_agent(roundAbout, (x, y))
            self.schedule.add(roundAbout)

        # Create stop 
        for pos in reversed(self.red_positions):
            x, y = pos
            stop = Stoplight(self.next_id(), (x, y), "red", self)
            self.grid.place_agent(stop, (x, y))
            self.schedule.add(stop)

        # Create go
        for pos in reversed(self.green_positions):
            x, y = pos
            go = Stoplight(self.next_id(), (x, y), "green", self)
            self.grid.place_agent(go, (x, y))
            self.schedule.add(go)

        # Store available parking spots
        available_spots = list(self.parkingSpots_positions)
        NUMBER_OF_CARS = 1

        # Create cars with random parking spot as initial position and set a different parking spot as the goal
        for _ in range(NUMBER_OF_CARS):  # Replace NUMBER_OF_CARS with your desired number of cars
            # Get a random parking spot as the initial position for the car
            initial_spot = random.choice(available_spots)
            x, y, number = initial_spot
            car = Car(self.next_id(), (x, y), self)

            # Remove the selected initial spot from available spots
            available_spots.remove(initial_spot)

            # Get a different random parking spot as the goal for the car
            goal_spot = random.choice(available_spots)
            car.goal_position = (goal_spot[0], goal_spot[1])

            self.grid.place_agent(car, (x, y))
            self.schedule.add(car)

            # Remove the selected goal spot from available spots to avoid same initial and goal spots
            available_spots.remove(goal_spot)

        self.running = True
        self.datacollector.collect(self)
        
    def step(self):
        self.schedule.step()  # Call the step method for all agents
        self.datacollector.collect(self)  # Collect data for visualization
