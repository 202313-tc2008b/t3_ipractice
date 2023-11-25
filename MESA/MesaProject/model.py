import mesa
import random
from agents import *
from scheduler import RandomActivationByTypeFiltered

# TODO: 4 files NSEW ; 0 = Cannot move, 1 = can move
class StreetView(mesa.Model):

    description = "MESA Visualization of the street cross simulation."
    
    def __init__(    
        self,
        width=24,
        height=24,
    ):
        super().__init__()
        def read_matrix(filename):
            nmat = []
            with open(filename, 'r') as file:
                matrix = [line.strip().split(',') for line in file.readlines()]
                for row in matrix[::-1]:
                    nmat.append(row)

            # Iterate through the matrix and print the type of each element
            for y, row in enumerate(nmat):
                for x, element in enumerate(row):
                    if element == '-':
                        continue
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
                        self.parkingSpots_positions.append(position)
                    elif element == 'N':
                        position = (x,y,element)
                        self.road_N.append(position)
                    elif element == 'S':
                        position = (x,y,element)
                        self.road_S.append(position)
                    elif element == 'E':
                        position = (x,y,element)
                        self.road_E.append(position)
                    elif element == 'W':
                        position = (x,y,element)
                        self.road_W.append(position)
                        
                    elif element == 'x':
                        pass
                    else:
                        print(f'Unknown Element: {element}')

        # Set parameters
        self.width = width
        self.height = height
        self.road_N = []
        self.road_S = []
        self.road_E = []
        self.road_W = []
        self.road = [self.road_N, self.road_S, self.road_E, self.road_W]
        self.building_positions = []
        self.parkingSpots_positions = []
        self.roundAbout_positions = []
        self.green_positions = []
        self.red_positions = []
        self.car_positions = []

        # Read the file content
        read_matrix('layout.txt')
        read_matrix('flowN.txt')
        read_matrix('flowS.txt')
        read_matrix('flowE.txt')
        read_matrix('flowW.txt')

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

        # Create roads at specified positions
        
        for compass_rose in self.road: 
            for pos in compass_rose:
                
                x, y, direction = pos
                this_cell =self.grid.get_cell_list_contents((x,y))
                
                if self.grid.is_cell_empty((x,y)):
                    road = Road(self.next_id(), (x, y), self, direction)
                    self.grid.place_agent(road, (x, y))
                    self.schedule.add(road)

                for a in this_cell:
                    if isinstance(a, Road):
                        a.add_direction(direction)
                        print((x,y),a.directions)

        # Create buildings at specified positions
        for pos in self.building_positions:
            x, y = pos
            building = Buildings(self.next_id(), (x, y), self)
            self.grid.place_agent(building, (x, y))
            self.schedule.add(building)

        # Create parking spots at specified positions
        for pos in self.parkingSpots_positions:
            x, y, number = pos
            parkingSpot = ParkingSpots(self.next_id(), (x, y), number, self)
            self.grid.place_agent(parkingSpot, (x, y))
            self.schedule.add(parkingSpot)

        # Create round about
        for pos in self.roundAbout_positions:
            x, y = pos
            roundAbout = RoundAbout(self.next_id(), (x, y), self)
            self.grid.place_agent(roundAbout, (x, y))
            self.schedule.add(roundAbout)

        # Create stop 
        for pos in self.red_positions:
            x, y = pos
            stop = Stoplight(self.next_id(), (x, y), "red", self)
            self.grid.place_agent(stop, (x, y))
            self.schedule.add(stop)

        # Create go
        for pos in self.green_positions:
            x, y = pos
            go = Stoplight(self.next_id(), (x, y), "green", self)
            self.grid.place_agent(go, (x, y))
            self.schedule.add(go)

        # Store available parking spots
        available_spots = list(self.parkingSpots_positions)
        NUMBER_OF_CARS = 8
        
        # Information of cars, initial position and goal
        self.car_info = {}

        # Create cars with random parking spot as initial position and set a different parking spot as the goal
        for i in range(NUMBER_OF_CARS):  # Replace NUMBER_OF_CARS with your desired number of cars
            # Get a random parking spot as the initial position for the car
            initial_spot = random.choice(available_spots)
            x, y, number1 = initial_spot
            car = Car(self.next_id(), (x, y), self)

            # Remove the selected initial spot from available spots
            available_spots.remove(initial_spot)

            # Get a different random parking spot as the goal for the car
            goal_spot = random.choice(available_spots)
            _, _, number2 = goal_spot
            car.goal_position = (goal_spot[0], goal_spot[1])

            # Add to car_info
            self.car_info[f'car_{i + 1}'] = {"initial_spot": number1, "goal_position": number2}

            self.grid.place_agent(car, (x, y))
            self.schedule.add(car)

            # Remove the selected goal spot from available spots to avoid same initial and goal spots
            available_spots.remove(goal_spot)

        self.running = True
        self.datacollector.collect(self)
        
        print(self.car_info)
    
    def step(self):
        self.schedule.step()  # Call the step method for all agents
        self.datacollector.collect(self)  # Collect data for visualization
