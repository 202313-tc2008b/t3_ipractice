from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from city import CityModel, CityCell, Car  # Import necessary classes from city_model

# Create a function to draw each cell in the grid
def city_portrayal(agent):
    portrayal = {
        "Shape": "rect",
        "Filled": "true",
        "Layer": 0,
        "Color": "white",  # Default color
        "w": 1,
        "h": 1
    }

    # Define colors and shapes for different types of agents
    if isinstance(agent, CityCell):
        if agent.type == "Building":
            portrayal["Color"] = "gray"
        elif agent.type == "Road":
            portrayal["Color"] = "black"
        elif agent.type == "ParkingLot":
            portrayal["Color"] = "blue"
        elif agent.type == "RoadWithRailing":
            portrayal["Color"] = "brown"
        elif agent.type == "Stoplight":
            portrayal["Color"] = agent.light_color  # Get stoplight color
            portrayal["Shape"] = "circle"  # Change shape for stoplight

    elif isinstance(agent, Car):
        portrayal["Color"] = "red" if agent.stopped else "green"
        portrayal["Shape"] = "car"  # Change shape for cars

    return portrayal


def main():
    # Create a canvas grid to visualize the city
    grid = CanvasGrid(city_portrayal, 24, 24, 500, 500)

    # Create a ModularServer instance to run the simulation and visualize it
    server = ModularServer(
        CityModel,
        [grid],
        "City Traffic Simulation",
        {"width": 24, "height": 24}  # Pass any required parameters for the model here
    )

    # Run the server at http://127.0.0.1:8521/
    server.port = 8521
    server.launch()
    

if __name__ == '__main__':
    main()
