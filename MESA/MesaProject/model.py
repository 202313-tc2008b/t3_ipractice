import mesa
import random
import json
from agents import *
from scheduler import RandomActivationByTypeFiltered

class StreetView(mesa.Model):
    """Main model: StreetView, controlls agents

    Args:
        mesa (mesa.Model): Mesa's base model

    Returns:
        None: No returns
    """
    description = "MESA Visualization of the street cross simulation."
    
    def __init__(    
        self,
        width=24,
        height=24,
    ):
        super().__init__()
        self.active_cars = 0
        self.max_cars = 40
        self.finished_cars = 0
        
        def read_matrix(filename):
            nmat = []
            with open(filename, 'r') as file:
                matrix = [line.strip().split(',') for line in file.readlines()]
                for row in matrix[::-1]:
                    nmat.append(row)

            # Iterate through the matrix and print the type of each element
            for y, row in enumerate(nmat):
                for x, element in enumerate(row):
                    if element == '-' or element == "":
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
                    else:
                        continue
        

        def make_flow(filename):
            nmat = []
            with open(filename, 'r') as file:
                matrix = [line.strip().split(',') for line in file.readlines()]
                for row in matrix[::-1]:
                    nmat.append(row)

            # Iterate through the matrix and print the type of each element
            for y, row in enumerate(nmat):
                for x, element in enumerate(row):
                    if element == '-' or element == "":
                        continue
                    elif element == 'N':
                        position = (x,y,element)
                        self.flow.append(position)
                    elif element == 'S':
                        position = (x,y,element)
                        self.flow.append(position)
                    elif element == 'E':
                        position = (x,y,element)
                        self.flow.append(position)
                    elif element == 'W':
                        position = (x,y,element)
                        self.flow.append(position)
                        
        # Set parameters
        self.width = width
        self.height = height
        # Main flow of the roads
        self.flow = []
        # Available choices for the cars to move
        self.road_N = []
        self.road_S = []
        self.road_E = []
        self.road_W = []
        # For iteration over all road elements
        self.road = [self.road_N, self.road_S, self.road_E, self.road_W]
        # Other agents
        self.building_positions = []
        self.roundAbout_positions = []
        self.parkingSpots_positions = []
        # Stoplights
        self.green_positions = []
        self.red_positions = []
        # Cars
        self.car_positions = []

        # Read the file content
        read_matrix('layout.txt')
        read_matrix('flowN.txt')
        read_matrix('flowS.txt')
        read_matrix('flowE.txt')
        read_matrix('flowW.txt')
        make_flow('mainFlow.txt')

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
        
        # Set the main directions for the roads
        for pos in self.flow:
            x, y, direction = pos
            this_cell =self.grid.get_cell_list_contents((x,y))
            
            for a in this_cell:
                if isinstance(a, Road):
                    a.set_main_direction(direction)

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


        
        NUMBER_OF_CARS = 5

        self.make_cars(NUMBER_OF_CARS)        

        self.running = True
        self.datacollector.collect(self)
    
    def make_cars(self, cars_num):
        # Store available parking spots
        self.available_spots = list(self.parkingSpots_positions)
        # Create cars with random parking spot as initial position and set a different parking spot as the goal
        for i in range(cars_num):  # Replace NUMBER_OF_CARS with your desired number of cars
            # Get a random parking spot as the initial position for the car
            initial_spot = random.choice(self.available_spots)
            x, y, spot_num1 = initial_spot
            car = Car(self.next_id(), (x, y), self)

            # Remove the selected initial spot from available spots
            self.available_spots.remove(initial_spot)

            # Get a different random parking spot as the goal for the car
            goal_spot = random.choice(self.available_spots)
            x2, y2, spot_num2 = goal_spot
            car.goal_pos = (goal_spot[0], goal_spot[1])
            car.set_spots(spot_num1,spot_num2)
            
            
            self.grid.place_agent(car, (x, y))
            self.schedule.add(car)

            self.active_cars += 1
            self.finished_cars += 1

            self.available_spots.append(initial_spot)


    def check_available_spots(self):
        # Check for available spots and spawn cars
        if self.active_cars < self.max_cars and len(self.available_spots) >= 2:
            if self.finished_cars < 500:
                self.make_cars(1)
                print(self.finished_cars)
        
        

    def get_info(self):
        """ 
        Method that retrieves the information of a step, for JSON output (MESA>>Flask>>Unity) 
        """
        self.car_info = []
        self.stoplight_info = []
        colors = []
        for a in self.schedule.agents:
            if isinstance(a, Car):
                # Add to car_info
                self.car_info.append({"car_id":a.unique_id, 
                                      "position": {
                                          "x":a.pos[0],
                                          "z":a.pos[1]
                                      },
                                   "current_direction":{
                                       "x":a.current_direction[0],
                                       "z":a.current_direction[1]
                                        }
                                     })
            elif isinstance(a, Stoplight):
                if a.color not in colors:
                    self.stoplight_info.append({"stop_type":a.type,
                                        "color":a.color})
                    colors.append(a.color)

        self.info = {"cars":self.car_info, "stoplights": self.stoplight_info}
        return json.dumps(self.info)
    
    def check_active(self):
        try:
            for a in self.schedule.agents:
                if isinstance(a, Car):
                    if not a.is_active:
                        self.grid.remove_agent(a)
                        self.schedule.remove(a)
                        self.active_cars -= 1
                        try: 
                            del a
                        except Exception as e:
                            print(f"An error occurred: {e}")


            self.check_available_spots()
        except Exception as e:  # Catch specific exceptions here or use Exception for a general catch
            print(f"An error occurred: {e}")
            

    def step(self):
        self.schedule.step_type(Car)  # Call the step method for all agents
        self.schedule.step_type(Stoplight)  # Call the step method for all agents
        self.check_active()
        self.datacollector.collect(self)  # Collect data for visualization
